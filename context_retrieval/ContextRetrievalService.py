"""
Context Retrieval Main Module

This is the main entry point for the context retrieval feature.
It captures screenshots at regular intervals and analyzes them using Claude API.
"""

import os
import sys
import time
import logging
import signal
from datetime import datetime

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context_retrieval import config
from context_retrieval.screenshot_capture import ScreenshotCapture
from context_retrieval.claude_analyzer import ClaudeAnalyzer
from context_retrieval.context_manager import ContextManager
from context_retrieval.shared_queue import links_queue
from context_retrieval.insights_generation import generate_links, update_summary_history


class ContextRetrievalService:
    """Main service for context retrieval"""
    
    def __init__(self):
        """Initialize the context retrieval service"""
        self.running = False
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        self.links_queue = None
        # Load API key
        try:
            with open(config.API_KEY_PATH, 'r') as f:
                api_key = f.read().strip()
            self.logger.info("API key loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading API key: {e}")
            raise
        
        # Initialize components
        self.screenshot_capture = ScreenshotCapture(
            save_dir=config.SCREENSHOTS_DIR,
            save_screenshots=config.SAVE_SCREENSHOTS
        )
        
        self.claude_analyzer = ClaudeAnalyzer(
            api_key=api_key,
            model=config.CLAUDE_MODEL,
            max_tokens=config.MAX_TOKENS,
            prompt=config.ANALYSIS_PROMPT
        )
        
        self.context_manager = ContextManager(
            contexts_dir=config.CONTEXTS_DIR,
            save_contexts=config.SAVE_CONTEXTS
        )
        
        # Track latest context and link generation timing
        self.latest_context = None
        self.last_link_generation = 0
        self.link_generation_interval = 60  # Generate links every 60 seconds
        
        self.logger.info("Context Retrieval Service initialized")
        self.logger.info(f"Screenshot interval: {config.SCREENSHOT_INTERVAL} seconds")
        self.logger.info(f"Link generation interval: {self.link_generation_interval} seconds")
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(config.LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def process_screenshot(self):
        """Capture and analyze a single screenshot"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("Starting screenshot capture and analysis...")
            
            # Capture screenshot
            screenshot, screenshot_path = self.screenshot_capture.capture_and_save()
            
            if screenshot_path:
                self.logger.info(f"Screenshot saved to: {screenshot_path}")
            
            # Analyze with Claude
            self.logger.info("Analyzing screenshot with Claude API...")
            context_xml = self.claude_analyzer.analyze_screenshot(screenshot)
            
            if context_xml:
                # Store context for link generation
                self.latest_context = context_xml
                
                # Print context to console
                print("\n" + "=" * 60)
                print("EXTRACTED CONTEXT:")
                print("=" * 60)
                print(context_xml)
                print("=" * 60 + "\n")
                
                # Save context
                context_path = self.context_manager.save_context(context_xml)
                if context_path:
                    self.logger.info(f"Context saved to: {context_path}")
                    return context_xml
            else:
                self.logger.warning("Failed to extract context from screenshot")
            
            self.logger.info("Screenshot processing completed")
            self.logger.info("=" * 60 + "\n")
            
        except Exception as e:
            self.logger.error(f"Error processing screenshot: {e}", exc_info=True)
    
    def generate_links_if_needed(self):
        """Generate links every minute if we have context"""
        current_time = time.time()
        
        # Check if it's time to generate links and we have context
        if (current_time - self.last_link_generation >= self.link_generation_interval 
            and self.latest_context):
            
            try:
                self.logger.info("Generating links from context...")
                
                # Use the environment variable for learning objective
                learning_objective = os.getenv("LEARNING_OBJECTIVE")
                if not learning_objective:
                    self.logger.warning("Learning objective environment variable is not set")
                    return
                
                # Update the summary history with new context
                self.logger.info("Updating summary history...")
                updated_summary = update_summary_history(learning_objective, self.latest_context)
                
                if updated_summary:
                    self.logger.info("Summary history updated successfully")
                    
                    # Print summary to console
                    print("\n" + "=" * 60)
                    print("UPDATED LEARNING SUMMARY:")
                    print("=" * 60)
                    print(updated_summary)
                    print("=" * 60 + "\n")
                else:
                    self.logger.warning("Failed to update summary history")
                
                # Generate links using the function from insights_generation.py
                insights = generate_links(learning_objective, self.latest_context)
                
                if insights and insights.links:
                    # Put links in the queue (overwrites old entry if full)
                    self.links_queue.put(insights.links)
                    self.logger.info(f"Generated {len(insights.links)} links and added to queue")
                    
                    # Print links to console
                    print("\n" + "=" * 60)
                    print("GENERATED LINKS:")
                    print("=" * 60)
                    for i, link in enumerate(insights.links, 1):
                        print(f"{i}. {link.summary}")
                        print(f"   URL: {link.url}")
                    print("=" * 60 + "\n")
                else:
                    self.logger.warning("Failed to generate links")
                
                self.last_link_generation = current_time
                
            except Exception as e:
                self.logger.error(f"Error generating links: {e}", exc_info=True)
    
    def run(self):
        """Run the context retrieval service"""
        self.running = True
        self.logger.info("Context Retrieval Service started")
        self.logger.info(f"Press Ctrl+C to stop")
        
        try:
            iteration = 0
            while self.running:
                iteration += 1
                self.logger.info(f"\n[Iteration {iteration}] Next capture in {config.SCREENSHOT_INTERVAL} seconds...")
                
                # Wait for the interval
                time.sleep(config.SCREENSHOT_INTERVAL)
                
                # Process screenshot
                self.process_screenshot()
                
                # Check if we should generate links
                self.generate_links_if_needed()
                
        except KeyboardInterrupt:
            self.logger.info("\nReceived shutdown signal")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the service"""
        self.running = False
        self.logger.info("Context Retrieval Service stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\nShutting down Context Retrieval Service...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        service = ContextRetrievalService()
        service.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

