"""
Position data model representing window/door positions within a project.
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

# Local imports
from services.event_bus import EventBus, event_bus


class PositionStatus(Enum):
    """Enum for position status values."""
    AUSSTEHEND = "Ausstehend"
    AUFGEMESSEN = "Aufgemessen"
    KLARUNG = "Klärung"
    ANPASSUNG = "Anpassung"


@dataclass
class Position:
    """Position data model for window/door positions with measurements."""
    
    id: str = ""  # Format: "1" for main positions, "1.1" for sub-positions
    project_id: int = 0
    template_code: str = ""  # Reference to position template
    name: str = ""
    floor: str = "Erdgeschoss"
    existing_window_type: str = "Holz"
    roller_shutter_type: str = "Nicht vorhanden"
    notes: str = ""
    product: str = ""  # Main product (window type) - legacy field
    product_id: Optional[int] = None  # Optional reference to product - legacy field
    product_type: str = ""  # Product type (Fenster, Rollladen, etc.) - legacy field
    product_ids: List[int] = field(default_factory=list)  # Multiple selected products
    is_main_position: bool = True
    parent_id: Optional[str] = None  # For sub-positions, references parent position id
    color: str = "#30d158"  # Default color
    is_selected: bool = False
    is_expanded: bool = True  # For main positions with sub-positions
    status: str = PositionStatus.AUSSTEHEND.value
    accessories: List[str] = field(default_factory=list)
    has_measurement_data: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def details(self) -> str:
        """Return formatted details of the position."""
        details_parts = []
        if self.product:
            details_parts.append(self.product)
        details_parts.append(f"({self.floor})")
        return " ".join(details_parts)
    
    @property
    def product_count(self) -> int:
        """Return number of selected products."""
        return len(self.product_ids)
    
    @property
    def status_info(self) -> Dict[str, str]:
        """Return color based on status."""
        status_mapping = {
            PositionStatus.AUFGEMESSEN.value: {"color": "#30d158"},
            PositionStatus.AUSSTEHEND.value: {"color": "#ff9f0a"},
            PositionStatus.KLARUNG.value: {"color": "#bf5af2"},
            PositionStatus.ANPASSUNG.value: {"color": "#64d2ff"}
        }
        return status_mapping.get(self.status, {"color": "#999999"})
    
    def update_status(self, new_status: str) -> None:
        """Update the position status and color."""
        self.status = new_status
        self.color = self.status_info["color"]
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "template_code": self.template_code,
            "name": self.name,
            "floor": self.floor,
            "existing_window_type": self.existing_window_type,
            "roller_shutter_type": self.roller_shutter_type,
            "notes": self.notes,
            "product": self.product,
            "product_id": self.product_id,
            "product_type": self.product_type,
            "product_ids": self.product_ids,
            "is_main_position": self.is_main_position,
            "parent_id": self.parent_id,
            "color": self.color,
            "is_selected": self.is_selected,
            "is_expanded": self.is_expanded,
            "status": self.status,
            "accessories": self.accessories,
            "has_measurement_data": self.has_measurement_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """Create a Position instance from a dictionary."""
        # Create a copy to avoid modifying the original
        data_copy = data.copy()
        
        # Convert string dates to datetime objects
        if "created_at" in data_copy:
            data_copy["created_at"] = datetime.fromisoformat(data_copy["created_at"])
        if "updated_at" in data_copy:
            data_copy["updated_at"] = datetime.fromisoformat(data_copy["updated_at"])
        
        # Handle accessories list if present
        if "accessories" in data_copy and isinstance(data_copy["accessories"], list):
            # Make a copy to avoid reference issues
            data_copy["accessories"] = data_copy["accessories"].copy()
        
        # Ensure new fields have default values if missing
        data_copy.setdefault("template_code", "")
        data_copy.setdefault("product_id", None)
        data_copy.setdefault("product_type", "")
        data_copy.setdefault("product_ids", [])
        
        # Migration: Handle legacy w_mm, h_mm fields
        if "w_mm" in data_copy:
            del data_copy["w_mm"]
        if "h_mm" in data_copy:
            del data_copy["h_mm"]
        
        # Migration: Handle legacy product selection without product_ids
        if "product_ids" not in data_copy or not data_copy["product_ids"]:
            # If we have a legacy product but no product_ids, create a default list
            if data_copy.get("product_id") and data_copy.get("product"):
                data_copy["product_ids"] = [data_copy["product_id"]]
            else:
                data_copy["product_ids"] = []
        
        # Migration: Handle JSON string format for product_ids if it comes from database
        if isinstance(data_copy.get("product_ids"), str):
            try:
                import json
                data_copy["product_ids"] = json.loads(data_copy["product_ids"])
            except (json.JSONDecodeError, TypeError):
                data_copy["product_ids"] = []
        
        # Migration: Ensure accessories is a list
        if "accessories" not in data_copy:
            data_copy["accessories"] = []
        elif isinstance(data_copy["accessories"], str):
            try:
                import json
                data_copy["accessories"] = json.loads(data_copy["accessories"])
            except (json.JSONDecodeError, TypeError):
                data_copy["accessories"] = []
            
        return cls(**data_copy)
