"""
AufmassItem data model representing measurement data for a position.
"""
# Standard libraries
import sys
import os
from datetime import datetime
from dataclasses import dataclass, field
import dataclasses
from typing import List, Optional, Dict, Any
import math

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@dataclass
class AufmassItem:
    """Measurement data model with all dimensions and calculations."""
    
    id: int = 0
    position_id: str = ""  # References the position id
    project_id: int = 0
    
    # Core measurements (in mm)
    inner_width: int = 0  # IB: Innen-Breite
    inner_height: int = 0  # IH: Innen-Höhe
    outer_width: int = 0  # AB: Außen-Breite
    outer_height: int = 0  # AH: Außen-Höhe
    diagonal: int = 0  # DIA: Diagonale
    
    # Extended measurements for ElementDesigner integration
    sill_height: float = 0.0  # Brüstungshöhe in mm
    frame_depth: float = 70.0  # Rahmenbreite in mm  
    mullion_offset: float = 50.0  # Pfosten-Versatz in %
    transom_offset: float = 50.0  # Kämpfer-Versatz in %
    glazing_thickness: float = 24.0  # Verglasungsdicke in mm
    reveal_left: float = 0.0  # Laibung links in mm
    reveal_right: float = 0.0  # Laibung rechts in mm
    reveal_top: float = 0.0  # Laibung oben in mm
    reveal_bottom: float = 0.0  # Laibung unten in mm
    
    # Calculated values
    area: float = 0.0  # Fläche in m²
    perimeter: float = 0.0  # Umfang in m
    
    # Legacy measurements (for backward compatibility)
    length: float = 0.0  # Length in meters
    width: float = 0.0   # Width in meters
    height: float = 0.0  # Height in meters
    count: float = 1.0   # Quantity/count
    
    # Additional notes about special characteristics
    special_notes: str = ""
    description: str = ""
    
    # List of photo file paths
    photos: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def area(self) -> float:
        """Calculate area in square meters from inner dimensions."""
        if self.inner_width <= 0 or self.inner_height <= 0:
            return 0.0
        return round((self.inner_width * self.inner_height) / 1000000, 2)  # mm² to m²
    
    @property
    def perimeter(self) -> float:
        """Calculate perimeter in meters from inner dimensions."""
        if self.inner_width <= 0 or self.inner_height <= 0:
            return 0.0
        return round(2 * (self.inner_width + self.inner_height) / 1000, 2)  # mm to m
    
    @property
    def aspect_ratio(self) -> str:
        """Calculate aspect ratio as a string (width:height)."""
        if self.inner_width <= 0 or self.inner_height <= 0:
            return "0:0"
        
        # Simplify the ratio
        gcd = self._gcd(self.inner_width, self.inner_height)
        width_ratio = self.inner_width // gcd if gcd > 0 else 0
        height_ratio = self.inner_height // gcd if gcd > 0 else 0
        
        # Protect against division by zero
        if width_ratio == 0:
            return "0:0"
            
        return f"1:{round(height_ratio/width_ratio, 2)}"
    
    def calculate_area(self) -> float:
        """Calculate area based on length, width, and count."""
        return round(self.length * self.width * self.count, 2)
    
    def calculate_volume(self) -> float:
        """Calculate volume based on length, width, height, and count."""
        return round(self.length * self.width * self.height * self.count, 2)
    
    def _gcd(self, a: int, b: int) -> int:
        """Calculate greatest common divisor using Euclidean algorithm."""
        if a == 0 or b == 0:
            return max(abs(a), abs(b)) or 1  # Avoid division by zero
        return math.gcd(a, b)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "position_id": self.position_id,
            "project_id": self.project_id,
            "inner_width": self.inner_width,
            "inner_height": self.inner_height,
            "outer_width": self.outer_width,
            "outer_height": self.outer_height,
            "diagonal": self.diagonal,
            "sill_height": self.sill_height,
            "frame_depth": self.frame_depth,
            "mullion_offset": self.mullion_offset,
            "transom_offset": self.transom_offset,
            "glazing_thickness": self.glazing_thickness,
            "reveal_left": self.reveal_left,
            "reveal_right": self.reveal_right,
            "reveal_top": self.reveal_top,
            "reveal_bottom": self.reveal_bottom,
            "area": self.area,
            "perimeter": self.perimeter,
            "length": self.length,
            "width": self.width,
            "height": self.height,
            "count": self.count,
            "special_notes": self.special_notes,
            "description": self.description,
            "photos": self.photos,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AufmassItem':
        """Create an AufmassItem instance from a dictionary."""
        # Create a copy to avoid modifying the original
        data_copy = data.copy()

        # Handle dates
        if "created_at" in data_copy and isinstance(data_copy["created_at"], str):
            data_copy["created_at"] = datetime.fromisoformat(data_copy["created_at"])
        if "updated_at" in data_copy and isinstance(data_copy["updated_at"], str):
            data_copy["updated_at"] = datetime.fromisoformat(data_copy["updated_at"])

        # Handle photos list if present
        if "photos" in data_copy and isinstance(data_copy["photos"], list):
            data_copy["photos"] = data_copy["photos"].copy()

        # Manually create instance without calling dataclass __init__ to avoid
        # issues with read-only properties like 'area' and 'perimeter'
        inst = cls.__new__(cls)
        for field_obj in cls.__dataclass_fields__.values():
            if field_obj.name in data_copy:
                value = data_copy[field_obj.name]
            else:
                if field_obj.default_factory is not dataclasses.MISSING:
                    value = field_obj.default_factory()
                elif field_obj.default is not dataclasses.MISSING:
                    value = field_obj.default
                else:
                    value = None
            inst.__dict__[field_obj.name] = value

        return inst
