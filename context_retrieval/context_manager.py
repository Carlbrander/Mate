"""
Context Manager Module

This module handles saving and managing extracted contexts.
"""

import os
from datetime import datetime
from typing import Optional
import logging


class ContextManager:
    """Handles context storage and management"""
    
    def __init__(self, contexts_dir: Optional[str] = None, save_contexts: bool = True):
        """
        Initialize context manager.
        
        Args:
            contexts_dir: Directory to save context files
            save_contexts: Whether to save contexts to disk
        """
        self.contexts_dir = contexts_dir
        self.save_contexts = save_contexts
        self.logger = logging.getLogger(__name__)
        
        # Create contexts directory if it doesn't exist and we're saving
        if self.save_contexts and self.contexts_dir:
            os.makedirs(self.contexts_dir, exist_ok=True)
            self.logger.info(f"Context save directory: {self.contexts_dir}")
    
    def save_context(self, context_xml: str) -> Optional[str]:
        """
        Save context XML to disk with timestamp.
        
        Args:
            context_xml: XML string containing extracted context
            
        Returns:
            Path to saved context file, or None if not saved
        """
        if not self.save_contexts or not self.contexts_dir:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"context_{timestamp}.xml"
            filepath = os.path.join(self.contexts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(context_xml)
            
            self.logger.info(f"Context saved: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving context: {e}")
            return None
    
    def get_latest_context(self) -> Optional[str]:
        """
        Retrieve the most recent context from disk.
        
        Returns:
            XML string of latest context, or None if no contexts found
        """
        if not self.contexts_dir or not os.path.exists(self.contexts_dir):
            return None
        
        try:
            # Get all context files
            context_files = [
                f for f in os.listdir(self.contexts_dir) 
                if f.startswith("context_") and f.endswith(".xml")
            ]
            
            if not context_files:
                return None
            
            # Sort by filename (which includes timestamp)
            context_files.sort(reverse=True)
            latest_file = os.path.join(self.contexts_dir, context_files[0])
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                context = f.read()
            
            self.logger.debug(f"Retrieved latest context from: {latest_file}")
            return context
            
        except Exception as e:
            self.logger.error(f"Error retrieving latest context: {e}")
            return None

