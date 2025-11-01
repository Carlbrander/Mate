"""
Claude Analyzer Module

This module handles sending screenshots to Claude API for analysis and context extraction.
"""

import base64
import io
from typing import Optional
from PIL import Image
import logging
from anthropic import Anthropic


class ClaudeAnalyzer:
    """Handles Claude API interactions for image analysis"""
    
    def __init__(self, api_key: str, model: str, max_tokens: int, prompt: str):
        """
        Initialize Claude analyzer.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens for API response
            prompt: Prompt template for analysis
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.prompt = prompt
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Claude analyzer initialized with model: {model}")
    
    def _image_to_base64(self, image: Image.Image, format: str = "PNG") -> str:
        """
        Convert PIL Image to base64 string.
        
        Args:
            image: PIL Image object
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Base64 encoded image string
        """
        buffered = io.BytesIO()
        image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def analyze_screenshot(self, screenshot: Image.Image) -> Optional[str]:
        """
        Analyze a screenshot using Claude API.
        
        Args:
            screenshot: PIL Image object to analyze
            
        Returns:
            XML string containing analysis results, or None if error
        """
        try:
            # Convert image to base64
            self.logger.debug("Converting screenshot to base64...")
            image_b64 = self._image_to_base64(screenshot)
            
            self.logger.info("Sending screenshot to Claude API for analysis...")
            
            # Create message with image
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": self.prompt
                            }
                        ],
                    }
                ],
            )
            
            # Extract response text
            response = message.content[0].text
            self.logger.info("Successfully received analysis from Claude API")
            self.logger.debug(f"Response length: {len(response)} characters")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error analyzing screenshot with Claude API: {e}")
            return None

