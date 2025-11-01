"""
Context Retrieval Module

This module provides functionality for capturing desktop screenshots at regular intervals
and analyzing them using Claude AI to extract contextual information.
"""

__version__ = "1.0.0"

from context_retrieval.screenshot_capture import ScreenshotCapture
from context_retrieval.claude_analyzer import ClaudeAnalyzer
from context_retrieval.context_manager import ContextManager
from context_retrieval.ContextRetrievalService import ContextRetrievalService

__all__ = [
    "ScreenshotCapture",
    "ClaudeAnalyzer",
    "ContextManager",
    "ContextRetrievalService",
]

