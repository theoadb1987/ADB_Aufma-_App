"""
EventBus service for inter-component communication.
"""
# Standard libraries
import sys
import os
from typing import Dict, Callable, List, Any

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party libraries
from PyQt6.QtCore import QObject, pyqtSignal

class EventBus(QObject):
    """
    Centralized event bus for application-wide communication between components.
    """
    
    # Generic signal that can carry any payload
    event_occurred = pyqtSignal(str, object)
    
    def __init__(self):
        """Initialize the event bus with empty subscribers dictionary."""
        super().__init__()
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish an event to all subscribers."""
        # Emit PyQt signal for QObject-based subscribers
        self.event_occurred.emit(event_type, data)
        
        # Call direct callbacks
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event subscriber callback: {e}")

# Singleton instance
event_bus = EventBus()