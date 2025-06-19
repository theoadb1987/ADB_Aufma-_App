# Korrigierte Importe für viewmodels/main_viewmodel.py
import sys
import os
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

# Projektwurzel sicherstellen
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# PyQt imports
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# Lokale Importe
from models.project import Project
from models.position import Position
from models.aufmass_item import AufmassItem
from services.data_service import DataService
from services.error_handler import error_handler, ErrorSeverity
from utils.logger import get_logger

logger = get_logger(__name__)


class MainViewModel(QObject):
    """ViewModel for main application interactions."""
    
    # Signals
    view_changed = pyqtSignal(str)  # Signal when the view is changed
    data_updated = pyqtSignal()     # Signal when data has been updated
    
    def __init__(self, data_service: DataService):
        """Initialize with data service."""
        super().__init__()
        self.data_service = data_service
        self.current_view = "projects"  # Default view
        logger.info("MainViewModel initialized")
    
    @pyqtSlot()
    def toggle_view(self) -> None:
        """Toggle between different views."""
        # Cycle through views: projects -> positions -> aufmass -> projects
        if self.current_view == "projects":
            self.current_view = "positions"
        elif self.current_view == "positions":
            self.current_view = "aufmass"
        else:
            self.current_view = "projects"
        
        # Emit signal for UI to handle
        self.view_changed.emit(self.current_view)
        logger.info(f"View toggled to {self.current_view}")
    
    @pyqtSlot(str)
    def set_active_view(self, view_name: str) -> None:
        """Set the active view directly."""
        if view_name in ["projects", "positions", "aufmass"]:
            self.current_view = view_name
            self.view_changed.emit(self.current_view)
            logger.info(f"Active view set to {view_name}")
        else:
            logger.error(f"Invalid view name: {view_name}")
    
    @pyqtSlot()
    def refresh_data(self) -> None:
        """Refresh application data."""
        # This would typically reload data from services
        # And then emit signal for views to update
        self.data_updated.emit()
        logger.info("Application data refreshed")
