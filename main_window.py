# Standard libraries
import sys
import os

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party libraries
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt6.QtGui import QAction  # QAction moved from QtWidgets to QtGui in PyQt6
from PyQt6.QtCore import Qt

# Local imports
from views.project_view import ProjectView
from views.position_view import PositionView
from views.aufmass_view import AufmassView
from utils.logger import get_logger


class MainWindow(QMainWindow):
    """Main application window with tabs for different views."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("Aufmaß-Verwaltung")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
        self._create_menu()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Project view
        self.project_view = ProjectView()
        self.tab_widget.addTab(self.project_view, "Projekte")
        
        # Position view
        self.position_view = PositionView()
        self.tab_widget.addTab(self.position_view, "Positionen")
        
        # Aufmass view
        self.aufmass_view = AufmassView()
        self.tab_widget.addTab(self.aufmass_view, "Aufmaß")
        
        # Initially disable position and aufmass tabs
        self.tab_widget.setTabEnabled(1, False)  # Positions tab
        self.tab_widget.setTabEnabled(2, False)  # Aufmass tab
        
    def _create_menu(self):
        """Create the menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("&Datei")
        
        # Exit action
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Hilfe")
        
        # About action
        about_action = QAction("Ü&ber", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _connect_signals(self):
        """Connect signals and slots."""
        # When a project is selected
        self.project_view.project_selected.connect(self._on_project_selected)
        
        # When a position is selected
        self.position_view.position_selected.connect(self._on_position_selected)
        
        # When a new position is created
        self.position_view.new_position_created.connect(self._on_new_position_created)
        
        # When tab is changed
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
    def _on_project_selected(self, project_id):
        """Handle project selection."""
        # Update position view with the selected project
        self.position_view.set_project(project_id)
        
        # Enable position tab
        self.tab_widget.setTabEnabled(1, True)
        
        # Disable aufmass tab until a position is selected
        self.tab_widget.setTabEnabled(2, False)
        
    def _on_position_selected(self, position_id):
        """Handle position selection."""
        # Update aufmass view with the selected position
        self.aufmass_view.set_position(position_id)
        
        # Enable aufmass tab
        self.tab_widget.setTabEnabled(2, True)
    
    def _on_new_position_created(self, position_id):
        """Handle new position creation - auto-switch to Aufmaß tab."""
        # Update aufmass view with the new position
        self.aufmass_view.set_position(position_id)
        
        # Enable and switch to aufmass tab
        self.tab_widget.setTabEnabled(2, True)
        self.tab_widget.setCurrentIndex(2)  # Switch to Aufmaß tab (index 2)
        
    def _on_tab_changed(self, index):
        """Handle tab change."""
        # Refresh the active view
        if index == 0:
            self.project_view.refresh()
        elif index == 1:
            self.position_view.refresh()
        elif index == 2:
            self.aufmass_view.refresh()
            
    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "Über Aufmaß-Verwaltung",
            "Aufmaß-Verwaltung\n\n"
            "Eine Anwendung zur Verwaltung von Projekten, Positionen und Aufmaßen."
        )