"""
Screenshot Capture Module

This module handles capturing screenshots of the desktop at regular intervals.
"""

import os
import time
from datetime import datetime
from typing import Optional
import pyautogui
from PIL import Image
import logging


class ScreenshotCapture:
    """Handles screenshot capture functionality"""
    
    def __init__(self, save_dir: Optional[str] = None, save_screenshots: bool = True):
        """
        Initialize screenshot capture.
        
        Args:
            save_dir: Directory to save screenshots (if None, uses current directory)
            save_screenshots: Whether to save screenshots to disk
        """
        self.save_dir = save_dir
        self.save_screenshots = save_screenshots
        self.logger = logging.getLogger(__name__)
        
        # Create save directory if it doesn't exist and we're saving
        if self.save_screenshots and self.save_dir:
            os.makedirs(self.save_dir, exist_ok=True)
            self.logger.info(f"Screenshot save directory: {self.save_dir}")
    
    def capture_screenshot(self) -> Image.Image:
        """
        Capture a screenshot of the entire screen.
        
        Returns:
            PIL Image object containing the screenshot
        """
        try:
            screenshot = pyautogui.screenshot()
            self.logger.debug("Screenshot captured successfully")
            return screenshot
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            raise
    
    def save_screenshot(self, screenshot: Image.Image) -> Optional[str]:
        """
        Save screenshot to disk with timestamp.
        
        Args:
            screenshot: PIL Image object to save
            
        Returns:
            Path to saved screenshot file, or None if not saved
        """
        if not self.save_screenshots or not self.save_dir:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.save_dir, filename)
            
            screenshot.save(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error saving screenshot: {e}")
            return None
    
    def capture_and_save(self) -> tuple[Image.Image, Optional[str]]:
        """
        Capture a screenshot and optionally save it to disk.
        
        Returns:
            Tuple of (PIL Image object, filepath or None)
        """
        screenshot = self.capture_screenshot()
        filepath = self.save_screenshot(screenshot)
        return screenshot, filepath

