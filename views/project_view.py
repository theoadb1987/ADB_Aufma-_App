# Standard libraries
import sys
import os
from datetime import datetime

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party libraries
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

# Local imports
from models.project import Project
from services.service_container import container
from utils.logger import get_logger
from viewmodels.project_viewmodel import ProjectViewModel

logger = get_logger(__name__)

class ProjectView(QWidget):
    """View for managing projects."""
    ...
    
    # Signals
    project_selected = pyqtSignal(int)
    
    def __init__(self, parent=None, viewmodel=None):
        """Initialize the project view."""
        super().__init__(parent)
        
        # Get ViewModel through dependency injection or create if not provided
        if viewmodel is None:
            self._viewmodel = container.get(ProjectViewModel)
        else:
            self._viewmodel = viewmodel
        
        # Current state
        self._current_project_id = None
        self._is_new_project = False
        self._current_projects = []  # Store current projects list
        
        self._setup_ui()
        self._connect_signals()
        
        # Load initial data
        self._load_projects()
        
        logger.info("ProjectView initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create a splitter for the list and detail views
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create project list UI (using ProjectListUI from UI module)
        from ui.project_ui import ProjectListUI
        self.list_ui = ProjectListUI()
        self.list_widget = QWidget()
        self.list_ui.setup_ui(self.list_widget)
        self.splitter.addWidget(self.list_widget)
        
        # Create project detail UI (using ProjectDetailUI from UI module)
        from ui.project_ui import ProjectDetailUI
        self.detail_ui = ProjectDetailUI()
        self.detail_widget = QWidget()
        self.detail_ui.setup_ui(self.detail_widget)
        self.splitter.addWidget(self.detail_widget)
        
        # Set initial sizes (40% list, 60% detail)
        self.splitter.setSizes([400, 600])
        
        layout.addWidget(self.splitter)
        
        logger.info("ProjectView UI setup completed")
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect add button in list UI
        self.list_ui.set_add_button_callback(self.create_new_project)
        
        # Connect save button in detail UI
        self.detail_ui.set_save_callback(self._save_project)
        
        # Connect delete button in detail UI
        self.detail_ui.set_delete_callback(self._confirm_delete_project)
        
        # Connect toggle view button in detail UI
        self.detail_ui.set_toggle_view_callback(self._toggle_view)
        
        # Connect ViewModel signals
        self._viewmodel.project_details_updated.connect(self._on_project_details_updated)
        self._viewmodel.project_status_changed.connect(self._on_project_status_changed)
        self._viewmodel.project_validation_error.connect(self._on_validation_error)
        
        logger.info("ProjectView signals connected")
    
    def _load_projects(self):
        """Load projects from the ViewModel."""
        try:
            projects = self._viewmodel.get_projects()
            self._current_projects = projects  # Store for later use
            
            # Update the list UI
            self.list_ui.update_project_list(projects, self._on_project_item_selected)
            
            logger.info(f"Loaded {len(projects)} projects")
        except Exception as e:
            logger.error(f"Error loading projects: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Projekte: {str(e)}")
    
    def create_new_project(self):
        """Create a new project."""
        self._is_new_project = True
        self._current_project_id = None
        
        # Clear and prepare the detail UI for a new project
        self.detail_ui.setup_for_new_project()
        
        # Set default dates
        today = datetime.now().date()
        next_month = today.replace(month=today.month % 12 + 1)
        if today.month == 12:
            next_month = next_month.replace(year=today.year + 1)
            
        self.detail_ui.measurement_date.setDate(today)
        self.detail_ui.installation_date.setDate(next_month)
        
        logger.info("New project creation initiated")
    
    def set_project(self, project_id):
        """Set the current project and load its details."""
        if project_id == self._current_project_id:
            return
            
        self._current_project_id = project_id
        self._is_new_project = False
        
        # Load project details
        self._load_project_details()
        
        # Emit signal
        self.project_selected.emit(project_id)
        
        logger.info(f"Project set: {project_id}")
    
    def _load_project_details(self):
        """Load details for the current project."""
        if not self._current_project_id:
            return
            
        try:
            # Get project from ViewModel
            project = self._viewmodel.get_project(self._current_project_id)
            
            if project:
                # Update detail UI
                self.detail_ui.set_project_data(project)
                
                # Select in list UI
                for proj in self._current_projects:
                    proj.is_selected = (proj.id == self._current_project_id)
                self.list_ui.update_project_list(self._current_projects, self._on_project_item_selected)
                
                logger.info(f"Loaded details for project: {project.name}")
            else:
                logger.warning(f"No project found with ID: {self._current_project_id}")
        except Exception as e:
            logger.error(f"Error loading project details: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Projektdetails: {str(e)}")
    
    def _save_project(self):
        """Save the current project."""
        try:
            # Get data from UI
            if self._is_new_project:
                project = Project()
            else:
                project = self._viewmodel.get_project(self._current_project_id)
                if not project:
                    project = Project()
            
            # Update from UI data
            project_data = self.detail_ui.get_project_data(project)
            
            # Save through ViewModel
            project_id = self._viewmodel.save_project(project_data)
            
            # Update state
            self._current_project_id = project_id
            self._is_new_project = False
            
            # Refresh projects list
            self._load_projects()
            
            # Load saved project details
            self._load_project_details()
            
            # Show success message
            QMessageBox.information(self, "Erfolg", "Projekt erfolgreich gespeichert.")
            
            # Emit signal
            self.project_selected.emit(project_id)
            
            logger.info(f"Project saved: {project_data.get('name', '')} (ID: {project_id})")
            return True
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern des Projekts: {str(e)}")
            return False
    
    def _confirm_delete_project(self):
        """Confirm and handle project deletion."""
        if not self._current_project_id:
            return
            
        # Get project name
        project = self._viewmodel.get_project(self._current_project_id)
        if not project:
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Projekt löschen",
            f"Möchten Sie das Projekt '{project.name}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._delete_project()
    
    def _delete_project(self):
        """Delete the current project."""
        if not self._current_project_id:
            return
            
        try:
            # Delete through ViewModel
            success = self._viewmodel.delete_project(self._current_project_id)
            
            if success:
                # Clear current project
                self._current_project_id = None
                self._is_new_project = False
                
                # Clear detail UI
                self.detail_ui.setup_for_new_project()
                
                # Refresh projects list
                self._load_projects()
                
                # Show success message
                QMessageBox.information(self, "Erfolg", "Projekt erfolgreich gelöscht.")
                
                logger.info(f"Project deleted: {self._current_project_id}")
            else:
                QMessageBox.warning(self, "Fehler", "Projekt konnte nicht gelöscht werden.")
                logger.warning(f"Failed to delete project: {self._current_project_id}")
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen des Projekts: {str(e)}")
    
    def _toggle_view(self):
        """Toggle to Aufmaß view."""
        # Access the MainViewModel to toggle view
        from viewmodels.main_viewmodel import MainViewModel
        try:
            main_viewmodel = container.get(MainViewModel)
            main_viewmodel.toggle_view()
            logger.info("View toggled to Aufmaß")
        except Exception as e:
            logger.error(f"Error toggling view: {e}")
    
    def _on_project_item_selected(self, project):
        """Handle project selection from list item."""
        self.set_project(project.id)
    
    @pyqtSlot(Project)
    def _on_project_details_updated(self, project):
        """Handle project details update from ViewModel."""
        if project.id == self._current_project_id:
            self.detail_ui.set_project_data(project)
            logger.info(f"Project details updated: {project.name}")
    
    @pyqtSlot(Project)
    def _on_project_status_changed(self, project):
        """Handle project status change from ViewModel."""
        # Refresh the projects list to show updated status
        self._load_projects()
        logger.info(f"Project status changed: {project.status}")
    
    @pyqtSlot(str)
    def _on_validation_error(self, message):
        """Handle validation error from ViewModel."""
        QMessageBox.warning(self, "Validierungsfehler", message)
        logger.warning(f"Validation error: {message}")
    
    def refresh(self):
        """Refresh the view."""
        self._load_projects()
        
        if self._current_project_id:
            self._load_project_details()
            
        logger.info("ProjectView refreshed")
