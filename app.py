# Standard libraries
import sys
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party libraries
from PyQt6.QtWidgets import QApplication  # Added missing import
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# Local imports
from models.project import Project
from services.position_service import PositionService
from services.aufmass_service import AufmassService
from services.error_handler import error_handler, ErrorSeverity
from utils.logger import get_logger, configure_global_logging  # Added missing import

configure_global_logging()
logger = get_logger(__name__)

class Application:
    """Application bootstrapper that creates and manages application services."""
    
    def __init__(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Aufmaß-Verwaltung")
        self.app.setOrganizationName("Aufmaß-App")
        self.app.setOrganizationDomain("aufmass-app.de")
        
        # Initialize and register services
        self._init_services()
        
        # Initialize and register ViewModels
        self._init_viewmodels()
        
        # Set global error handler
        self._setup_error_handler()
        
        # Apply theme
        self._apply_theme()
        
        logger.info("Application initialized")
    
    def _init_services(self):
        """Initialize and register all services."""
        # Create services
        self.config_service = ConfigService()
        self.data_service = DataService()
        self.position_service = PositionService()
        self.aufmass_service = AufmassService()
        self.style_service = StyleService(self.config_service)
        
        # Register in container
        container.register(ConfigService, self.config_service)
        container.register(DataService, self.data_service)
        container.register(PositionService, self.position_service)
        container.register(AufmassService, self.aufmass_service)
        container.register(StyleService, self.style_service)
        
        logger.info("Services initialized and registered")
    
    def _init_viewmodels(self):
        """Initialize and register all ViewModels."""
        # Create ViewModels with services from container
        self.main_viewmodel = MainViewModel(self.data_service)
        self.project_viewmodel = ProjectViewModel(self.data_service)
        self.position_viewmodel = PositionViewModel(self.data_service)
        self.aufmass_viewmodel = AufmassViewModel(self.position_service, self.aufmass_service)
        
        # Register in container
        container.register(MainViewModel, self.main_viewmodel)
        container.register(ProjectViewModel, self.project_viewmodel)
        container.register(PositionViewModel, self.position_viewmodel)
        container.register(AufmassViewModel, self.aufmass_viewmodel)
        
        logger.info("ViewModels initialized and registered")
    
    def _setup_error_handler(self):
        """Set up global error handler."""
        # Error handler is already a singleton
        error_handler.register_callback("application_error", self._handle_application_error)
        logger.info("Error handler configured")
    
    def _handle_application_error(self, message, severity, details):
        """Handle application-wide errors."""
        # Log the error
        log_level = {
            ErrorSeverity.INFO: logger.info,
            ErrorSeverity.WARNING: logger.warning,
            ErrorSeverity.ERROR: logger.error,
            ErrorSeverity.CRITICAL: logger.critical
        }.get(severity, logger.error)
        
        log_level(f"Application error: {message}" + (f" - {details}" if details else ""))
    
    def _apply_theme(self):
        """Apply the theme from config."""
        theme = self.config_service.get("theme", "dark")
        self.style_service.set_theme(theme)
        logger.info(f"Applied theme: {theme}")
    
    def run(self):
        """Run the application."""
        from main import MainWindow
        
        # Create and show main window
        self.main_window = MainWindow()
        self.main_window.show()
        
        # Run the application
        logger.info("Application starting")
        return self.app.exec()
    
    def shutdown(self):
        """Shutdown the application and clean up resources."""
        # Shutdown services that need cleanup
        self.data_service.shutdown()
        
        logger.info("Application shutdown complete")

# Application entry point
if __name__ == "__main__":
    app = Application()
    exit_code = app.run()
    app.shutdown()
    sys.exit(exit_code)
