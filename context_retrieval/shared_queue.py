"""
Simple queue for sharing links between context retrieval thread and main app.
Max size of 1 - new items overwrite old ones.
"""
import threading
from typing import Optional, Any


class OverwritingQueue:
    """A simple queue that overwrites old items when full (max_size=1)"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._item: Optional[Any] = None
        self._has_item = False
    
    def put(self, item):
        """Put an item in the queue, overwriting any existing item"""
        with self._lock:
            self._item = item
            self._has_item = True
    
    def get(self) -> Optional[Any]:
        """Get item from queue without removing it (peek)"""
        with self._lock:
            return self._item if self._has_item else None
    
    def has_item(self) -> bool:
        """Check if queue has an item"""
        with self._lock:
            return self._has_item
    
    def clear(self):
        """Clear the queue"""
        with self._lock:
            self._item = None
            self._has_item = False


# Global queue instance for links
links_queue = OverwritingQueue()

