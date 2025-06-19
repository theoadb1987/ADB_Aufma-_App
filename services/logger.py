# services/logger.py - Compatibility layer for old imports
"""
This module re-exports functionality from utils.logger to maintain backward compatibility.
"""
import os
import sys
import logging
from datetime import datetime  # This was the missing import

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)  # Fixed indentation

# Re-export from utils.logger
from utils.logger import get_logger, configure_global_logging