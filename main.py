"""
Hauptmodul für die Aufmaß-Verwaltungsanwendung

ÄNDERUNGSHINWEIS:
- In PyQt6 wurde QAction vom QtWidgets-Modul ins QtGui-Modul verschoben
- Import-Statements aktualisiert, um dieser Änderung Rechnung zu tragen
- QApplication-Import hinzugefügt, der in der main()-Funktion verwendet wird
"""
# Standard libraries
import sys
import os

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party libraries
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QApplication
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

# Local imports - Views
from views.project_view import ProjectView
from views.position_view import PositionView
from views.aufmass_view import AufmassView

# Local imports - Services
from services.position_service import PositionService
from services.aufmass_service import AufmassService
from services.data_service import DataService
from services.style_service import StyleService
from services.config_service import ConfigService
from services.service_container import container

# Local imports - ViewModels
from viewmodels.project_viewmodel import ProjectViewModel
from viewmodels.position_viewmodel import PositionViewModel
from viewmodels.aufmass_viewmodel import AufmassViewModel
from viewmodels.main_viewmodel import MainViewModel

# Local imports - Utils
from utils.logger import get_logger, configure_global_logging

# Configure logging
configure_global_logging()
logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window with tabs for different views."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("Aufmaß-Verwaltung")
        self.setMinimumSize(800, 600)
        
        # Initialize services and register in container
        self._init_services()
        
        # Initialize ViewModels
        self._init_viewmodels()
        
        # Setup UI
        self._setup_ui()
        self._create_menu()
        self._connect_signals()
        
        # Apply theme from config
        self._apply_theme()
        
        # Element Designer dock widget
        self.element_designer_dock = None
        
        logger.info("MainWindow initialized")
    
    def _init_services(self):
        """Initialize all services and register them in the container."""
        # Create services
        config_service = ConfigService()
        data_service = DataService()
        position_service = PositionService()
        aufmass_service = AufmassService()
        style_service = StyleService(config_service)
        
        # Register services in container
        container.register(ConfigService, config_service)
        container.register(DataService, data_service)
        container.register(PositionService, position_service)
        container.register(AufmassService, aufmass_service)
        container.register(StyleService, style_service)
        
        # Store references
        self.config_service = config_service
        self.style_service = style_service
        
        logger.info("Services initialized and registered")
    
    def _init_viewmodels(self):
        """Initialize all ViewModels with dependency injection."""
        # Get services from container
        data_service = container.get(DataService)
        position_service = container.get(PositionService)
        aufmass_service = container.get(AufmassService)
        
        # Create ViewModels
        self.main_viewmodel = MainViewModel(data_service)
        self.project_viewmodel = ProjectViewModel(data_service)
        self.position_viewmodel = PositionViewModel(data_service)  # Only inject DataService
        self.aufmass_viewmodel = AufmassViewModel(position_service, aufmass_service)
        
        # Register ViewModels in container
        container.register(MainViewModel, self.main_viewmodel)
        container.register(ProjectViewModel, self.project_viewmodel)
        container.register(PositionViewModel, self.position_viewmodel)
        container.register(AufmassViewModel, self.aufmass_viewmodel)
        
        logger.info("ViewModels initialized and registered")
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Project view with ViewModel injection
        self.project_view = ProjectView(viewmodel=self.project_viewmodel)
        self.tab_widget.addTab(self.project_view, "Projekte")
        
        # Position view with ViewModel injection
        self.position_view = PositionView(viewmodel=self.position_viewmodel)
        self.tab_widget.addTab(self.position_view, "Positionen")
        
        # Aufmass view with ViewModel injection
        self.aufmass_view = AufmassView(viewmodel=self.aufmass_viewmodel)
        self.tab_widget.addTab(self.aufmass_view, "Aufmaß")
        
        # Initially disable position and aufmass tabs
        self.tab_widget.setTabEnabled(1, False)  # Positions tab
        self.tab_widget.setTabEnabled(2, False)  # Aufmass tab
        
        # Apply window settings from config
        window_settings = self.config_service.get_window_settings()
        if window_settings:
            self.resize(window_settings.get('width', 800), window_settings.get('height', 600))
            if window_settings.get('maximized', False):
                self.showMaximized()
        
        logger.info("UI components set up")
    
    def _create_menu(self):
        """Create the menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("&Datei")
        
        # Exit action
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&Ansicht")
        
        # Theme toggle action
        theme_action = QAction("Dunkles Theme", self)
        theme_action.setCheckable(True)
        theme_action.setChecked(self.style_service.is_dark_theme())
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)
        
        # Window menu
        window_menu = self.menuBar().addMenu("&Fenster")
        
        # Element Designer action
        designer_action = QAction("Element-Designer...", self)
        designer_action.setShortcut("Ctrl+D")
        designer_action.triggered.connect(self._show_element_designer)
        window_menu.addAction(designer_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Hilfe")
        
        # About action
        about_action = QAction("Ü&ber", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        logger.info("Menu created")
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # When a project is selected
        self.project_view.project_selected.connect(self._on_project_selected)
        
        # When a position is selected
        self.position_view.position_selected.connect(self._on_position_selected)
        
        # When tab is changed
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Connect style service theme change callback
        self.style_service.register_theme_changed_callback(self._on_theme_changed)
        
        logger.info("Signals connected")
    
    def _on_project_selected(self, project_id):
        """Handle project selection."""
        # Update position view with the selected project
        self.position_view.set_project(project_id)
        
        # Enable position tab
        self.tab_widget.setTabEnabled(1, True)
        
        # Disable aufmass tab until a position is selected
        self.tab_widget.setTabEnabled(2, False)
        
        # Add to recent projects if using config service
        project = self.project_viewmodel.get_project(project_id)
        if project and self.config_service:
            self.config_service.add_recent_project(project_id, project.name)
        
        logger.info(f"Project selected: {project_id}")
    
    def _on_position_selected(self, position_id):
        """Handle position selection."""
        # Update aufmass view with the selected position
        self.aufmass_view.set_position(position_id)
        
        # Enable aufmass tab
        self.tab_widget.setTabEnabled(2, True)
        
        logger.info(f"Position selected: {position_id}")
    
    def _on_tab_changed(self, index):
        """Handle tab change."""
        # Refresh the active view
        if index == 0:
            self.project_view.refresh()
        elif index == 1:
            self.position_view.refresh()
        elif index == 2:
            self.aufmass_view.refresh()
            
        logger.info(f"Tab changed to index: {index}")
    
    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "Über Aufmaß-Verwaltung",
            "Aufmaß-Verwaltung\n\n"
            "Eine Anwendung zur Verwaltung von Projekten, Positionen und Aufmaßen."
        )
        logger.info("About dialog shown")
    
    def _toggle_theme(self):
        """Toggle between dark and light theme."""
        self.style_service.toggle_theme()
    
    def _on_theme_changed(self, theme):
        """Handle theme change."""
        # Update the menu item if needed
        theme_action = self.menuBar().findChild(QAction, "Dunkles Theme")
        if theme_action:
            theme_action.setChecked(theme == "dark")
    
    def _apply_theme(self):
        """Apply the current theme."""
        self.style_service.set_theme(self.style_service.get_current_theme())
    
    def _show_element_designer(self):
        """Show the Element Designer dock widget."""
        if self.element_designer_dock is None:
            from PyQt6.QtWidgets import QDockWidget
            from views.element_designer_view import ElementDesignerView
            
            # Create dock widget
            self.element_designer_dock = QDockWidget("Element-Designer", self)
            self.element_designer_dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                QDockWidget.DockWidgetFeature.DockWidgetClosable
            )
            
            # Create Element Designer view
            self.element_designer_view = ElementDesignerView()
            self.element_designer_dock.setWidget(self.element_designer_view)
            
            # Connect signals
            self.element_designer_view.window_type_selected.connect(self._on_window_type_selected)
            self.element_designer_view.svg_export_requested.connect(self._on_svg_export_requested)
            
            # Add as floating window
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.element_designer_dock)
            self.element_designer_dock.setFloating(True)
            self.element_designer_dock.resize(800, 600)
            
        # Show the dock widget
        self.element_designer_dock.show()
        self.element_designer_dock.raise_()
        logger.info("Element Designer opened")
    
    def _on_window_type_selected(self, window_type):
        """Handle window type selection from Element Designer."""
        logger.info(f"Window type selected: {window_type.code} - {window_type.display_name}")
        # TODO: Integrate with current project
    
    def _on_svg_export_requested(self, export_path):
        """Handle SVG export request from Element Designer."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from services.svg_export_service import SVGExportService
        
        logger.info(f"SVG export requested: {export_path}")
        
        try:
            # Get current window type from Element Designer
            window_type = self.element_designer_view.get_current_window_type()
            if not window_type:
                QMessageBox.warning(self, "Export Fehler", "Bitte wählen Sie zuerst einen Fenstertyp aus.")
                return
                
            # Get project name if available
            project_name = "Unbenanntes Projekt"
            if hasattr(self, 'project_viewmodel') and self.project_viewmodel:
                # Try to get current project name
                try:
                    current_project = getattr(self.project_viewmodel, 'current_project', None)
                    if current_project and hasattr(current_project, 'name'):
                        project_name = current_project.name
                except:
                    pass
            
            # Ask user for save location
            suggested_name = f"{window_type.code}_{project_name.replace(' ', '_')}.svg"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "SVG Export - Speicherort wählen",
                suggested_name,
                "SVG Dateien (*.svg);;Alle Dateien (*)"
            )
            
            if file_path:
                # Export SVG
                svg_service = SVGExportService()
                success = svg_service.export_window_element(window_type, file_path, project_name)
                
                if success:
                    QMessageBox.information(
                        self, 
                        "Export erfolgreich", 
                        f"SVG wurde erfolgreich exportiert:\n{file_path}"
                    )
                    logger.info(f"SVG successfully exported: {file_path}")
                else:
                    QMessageBox.critical(
                        self, 
                        "Export Fehler", 
                        "SVG Export fehlgeschlagen. Bitte prüfen Sie die Logs."
                    )
                    
        except Exception as e:
            logger.error(f"SVG export error: {e}")
            QMessageBox.critical(self, "Export Fehler", f"Fehler beim SVG Export: {str(e)}")

    def closeEvent(self, event):
        """Handle window close event to save settings."""
        # Save window settings
        maximized = self.isMaximized()
        if not maximized:
            size = self.size()
            self.config_service.save_window_settings(size.width(), size.height(), maximized)
        else:
            self.config_service.save_window_settings(800, 600, maximized)
        
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
