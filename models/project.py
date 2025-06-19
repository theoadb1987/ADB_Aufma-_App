"""
Project data model representing project information.
"""
# Standard libraries
import sys
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ProjectStatus(Enum):
    """Enum for project status values."""
    AUSSTEHEND = "Ausstehend"
    AUFMASS = "Aufmaß"
    KLARUNG = "Klärung"
    ANPASSUNG = "Anpassung"


@dataclass
class Project:
    """Project data model with all relevant project information."""
    
    id: int = 0
    name: str = ""
    address: str = ""
    city: str = ""
    postal_code: str = ""
    status: str = ProjectStatus.AUSSTEHEND.value
    profile_system: str = ""
    contact_person: str = ""
    installation_date: Optional[datetime] = None
    measurement_date: Optional[datetime] = None
    field_service_employee: str = ""
    color: str = "#ff9f0a"  # Default color for pending status
    icon: str = "⏱"  # Default icon for pending status
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_selected: bool = False
    
    @property
    def full_address(self) -> str:
        """Return the full address as a formatted string."""
        return f"{self.address}, {self.postal_code} {self.city}"
    
    @property
    def status_info(self) -> Dict[str, str]:
        """Return color and icon based on status."""
        status_mapping = {
            ProjectStatus.AUFMASS.value: {"color": "#30d158", "icon": "✓"},
            ProjectStatus.AUSSTEHEND.value: {"color": "#ff9f0a", "icon": "⏱"},
            ProjectStatus.KLARUNG.value: {"color": "#bf5af2", "icon": "?"},
            ProjectStatus.ANPASSUNG.value: {"color": "#64d2ff", "icon": "🔧"}
        }
        return status_mapping.get(self.status, {"color": "#999999", "icon": "•"})
    
    def update_status(self, new_status: str) -> None:
        """Update the project status and corresponding color/icon."""
        self.status = new_status
        status_info = self.status_info
        self.color = status_info["color"]
        self.icon = status_info["icon"]
        self.updated_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "status": self.status,
            "profile_system": self.profile_system,
            "contact_person": self.contact_person,
            "installation_date": self.installation_date.isoformat() if self.installation_date else None,
            "measurement_date": self.measurement_date.isoformat() if self.measurement_date else None,
            "field_service_employee": self.field_service_employee,
            "color": self.color,
            "icon": self.icon,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_selected": self.is_selected
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create a Project instance from dictionary data."""
        # Create a copy to avoid modifying the original
        data_copy = data.copy()
        
        # Convert date strings to datetime objects if provided
        if data_copy.get('installation_date'):
            data_copy['installation_date'] = datetime.fromisoformat(data_copy['installation_date'])
        if data_copy.get('measurement_date'):
            data_copy['measurement_date'] = datetime.fromisoformat(data_copy['measurement_date'])
        if data_copy.get('created_at'):
            data_copy['created_at'] = datetime.fromisoformat(data_copy['created_at'])
        if data_copy.get('updated_at'):
            data_copy['updated_at'] = datetime.fromisoformat(data_copy['updated_at'])
            
        return cls(**data_copy)
