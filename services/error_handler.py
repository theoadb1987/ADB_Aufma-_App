"""
Error handling service for managing and displaying application errors.
"""
# Standard libraries
import sys
import os
from typing import Dict, Callable, Optional, Any
from enum import Enum, auto
import logging

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Local imports
from utils.logger import get_logger

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Enum for error severity levels."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class ErrorHandler:
    """Centralized error handling service for application errors."""
    
    def __init__(self):
        """Initialize error handler with empty callbacks dictionary."""
        self.error_callbacks: Dict[str, Callable] = {}
        self.default_parent = None
    
    def set_default_parent(self, parent: Any) -> None:
        """Set default parent widget for error dialogs."""
        self.default_parent = parent
    
    def register_callback(self, error_type: str, callback: Callable) -> None:
        """Register a callback for a specific error type."""
        self.error_callbacks[error_type] = callback
        logger.info(f"Registered error callback for: {error_type}")
    
    def handle_error(self, error_type: str, message: str, 
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    details: Optional[str] = None,
                    parent: Optional[Any] = None) -> None:
        """
        Handle an error by showing a message and invoking registered callbacks.
        
        Args:
            error_type: Type of error for routing to appropriate callback
            message: Main error message to display
            severity: Severity level of the error
            details: Optional detailed error information
            parent: Parent widget for message dialogs
        """
        # Log the error
        log_method = {
            ErrorSeverity.INFO: logger.info,
            ErrorSeverity.WARNING: logger.warning,
            ErrorSeverity.ERROR: logger.error,
            ErrorSeverity.CRITICAL: logger.critical
        }.get(severity, logger.error)
        
        log_method(f"{error_type}: {message}" + (f" - {details}" if details else ""))
        
        # Execute any registered callback for this error type
        if error_type in self.error_callbacks:
            self.error_callbacks[error_type](message, severity, details)
        else:
            # Use default error handling - this would typically show a dialog
            # But we're handling this part in the viewmodel with appropriate signals
            pass


# Singleton instance
error_handler = ErrorHandler()
