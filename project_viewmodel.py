"""
Project ViewModel for managing project-specific operations and data.
"""
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from typing import List, Optional, Dict, Any
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from models.project import Project
from services.data_service import DataService
from services.error_handler import error_handler, ErrorSeverity
from utils.logger import get_logger


logger = get_logger(__name__)


class ProjectViewModel(QObject):
    """ViewModel for project-related operations."""
    
    # Signals
    project_details_updated = pyqtSignal(Project)
    project_status_changed = pyqtSignal(Project)
    project_validation_error = pyqtSignal(str)
    
    def __init__(self, data_service: DataService):
        """Initialize with data service."""
        super().__init__()
        self.data_service = data_service
        logger.info("ProjectViewModel initialized")
    
    @pyqtSlot(int, str, str, str, str, str, str, str, object, object, str)
    def create_or_update_project(self, project_id: int, name: str, address: str, 
                               city: str, postal_code: str, status: str,
                               profile_system: str, contact_person: str, 
                               installation_date: Optional[datetime], 
                               measurement_date: Optional[datetime],
                               field_service_employee: str) -> Optional[int]:
        """Create or update a project with the provided details."""
        try:
            # Validate essential fields
            if not name:
                self.project_validation_error.emit("Projektname darf nicht leer sein.")
                return None
            
            # Create or retrieve project
            if project_id > 0:
                project = self.data_service.get_project(project_id)
                if not project:
                    raise ValueError(f"Project with ID {project_id} not found")
            else:
                project = Project()
            
            # Update project fields
            project.name = name
            project.address = address
            project.city = city
            project.postal_code = postal_code
            project.profile_system = profile_system
            project.contact_person = contact_person
            project.installation_date = installation_date
            project.measurement_date = measurement_date
            project.field_service_employee = field_service_employee
            
            # Update status (this also updates color and icon)
            if project.status != status:
                project.update_status(status)
            
            # Save project
            saved_id = self.data_service.save_project(project)
            
            # Update ID for new projects
            if project.id == 0:
                project.id = saved_id
            
            # Emit signal for UI update
            self.project_details_updated.emit(project)
            
            logger.info(f"{'Created' if project_id == 0 else 'Updated'} project: {name} (ID: {saved_id})")
            return saved_id
        except Exception as e:
            error_message = f"Failed to {'create' if project_id == 0 else 'update'} project"
            self._handle_error(error_message, str(e))
            return None
    
    def save_project(self, project_data: Dict[str, Any]) -> int:
        """Save a project using a dictionary of data."""
        try:
            project = Project(**project_data) if isinstance(project_data, dict) else project_data
            project_id = self.data_service.save_project(project)
            
            # Update ID for new projects
            if project.id == 0:
                project.id = project_id
                
            # Emit signal for UI update
            self.project_details_updated.emit(project)
            
            logger.info(f"Saved project: {project.name} (ID: {project_id})")
            return project_id
        except Exception as e:
            self._handle_error("Failed to save project", str(e))
            return 0
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        try:
            project = self.data_service.get_project(project_id)
            return project
        except Exception as e:
            self._handle_error("Failed to get project", str(e))
            return None
    
    def get_projects(self) -> List[Project]:
        """Get all projects."""
        try:
            projects = self.data_service.get_projects()
            return projects
        except Exception as e:
            self._handle_error("Failed to get projects", str(e))
            return []
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project by ID."""
        try:
            success = self.data_service.delete_project(project_id)
            if success:
                logger.info(f"Deleted project with ID: {project_id}")
            else:
                logger.warning(f"Failed to delete project with ID: {project_id}")
            return success
        except Exception as e:
            self._handle_error("Failed to delete project", str(e))
            return False
    
    @pyqtSlot(int, str)
    def update_project_status(self, project_id: int, new_status: str) -> None:
        """Update the status of a project."""
        try:
            project = self.data_service.get_project(project_id)
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")
            
            project.update_status(new_status)
            self.data_service.save_project(project)
            
            # Emit signal for UI update
            self.project_status_changed.emit(project)
            
            logger.info(f"Updated project status: {project.name} -> {new_status}")
        except Exception as e:
            self._handle_error("Failed to update project status", str(e))
    
    @pyqtSlot(int, str)
    def update_project_notes(self, project_id: int, notes: str) -> bool:
        """Update project notes."""
        try:
            project = self.data_service.get_project(project_id)
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")
            
            project.notes = notes
            project.updated_at = datetime.now()
            self.data_service.save_project(project)
            
            # Emit signal for UI update
            self.project_details_updated.emit(project)
            
            logger.info(f"Updated notes for project: {project.name}")
            return True
        except Exception as e:
            self._handle_error("Failed to update project notes", str(e))
            return False
    
    def create_sample_projects(self) -> List[Project]:
        """Create sample projects for testing or initial data."""
        sample_projects = [
            Project(
                name="Projekt Alpha",
                address="Musterstraße 1",
                city="Musterstadt",
                postal_code="12345",
                status="Aufmaß",
                contact_person="Max Mustermann",
                field_service_employee="S. Müller"
            ),
            Project(
                name="Projekt Beta",
                address="Beispielweg 7",
                city="Neustadt",
                postal_code="98765",
                status="Ausstehend",
                contact_person="Erika Musterfrau",
                field_service_employee="T. Schmidt"
            ),
            Project(
                name="Projekt Delta",
                address="Testplatz 42",
                city="Altdorf",
                postal_code="54321",
                status="Klärung",
                contact_person="Peter Test",
                field_service_employee="F. Meyer"
            ),
            Project(
                name="Projekt Gamma",
                address="Demoallee 15",
                city="Mittelhausen",
                postal_code="67890",
                status="Anpassung",
                contact_person="Laura Demo",
                field_service_employee="H. Wagner"
            )
        ]
        
        # Set status info (colors and icons)
        for project in sample_projects:
            project.color = project.status_info["color"]
            project.icon = project.status_info["icon"]
            
            # Save to database
            try:
                self.data_service.save_project(project)
            except Exception as e:
                logger.warning(f"Could not save sample project {project.name}: {e}")
        
        logger.info(f"Created {len(sample_projects)} sample projects")
        return sample_projects
    
    def _handle_error(self, message: str, details: str = None, 
                    severity: ErrorSeverity = ErrorSeverity.ERROR) -> None:
        """Handle errors through error handler service."""
        error_type = "project_error"
        error_handler.handle_error(error_type, message, severity, details)
