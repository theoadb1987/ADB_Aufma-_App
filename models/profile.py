"""
VEKA Profile Models for window element design.
Contains all profile data for offline Element-Designer operation.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class VEKASystem(Enum):
    """VEKA Profile Systems."""
    SOFTLINE_70 = ("SL70", "Softline 70", 70)
    SOFTLINE_82 = ("SL82", "Softline 82 MD", 82)
    ALPHALINE_90 = ("AL90", "Alphaline 90", 90)
    PERFECTLINE_76 = ("PL76", "Perfectline 76", 76)
    
    def __init__(self, code: str, display_name: str, depth_mm: int):
        self.code = code
        self.display_name = display_name
        self.depth_mm = depth_mm


class ProfileType(Enum):
    """Profile component types."""
    FRAME = ("frame", "Blendrahmen")
    SASH = ("sash", "Flügel")
    MULLION = ("mullion", "Pfosten")
    TRANSOM = ("transom", "Kämpfer")
    GLAZING_BEAD = ("glazing_bead", "Glasleiste")
    
    def __init__(self, code: str, display_name: str):
        self.code = code
        self.display_name = display_name


@dataclass
class ProfileDimensions:
    """Profile dimensional data."""
    depth_mm: float
    view_width_mm: float
    rebate_height_mm: float
    wall_thickness_mm: float
    chamber_count: int
    glazing_thickness_max: float


@dataclass
class ThermalData:
    """Thermal performance data."""
    uf_value: float  # W/(m²K)
    psi_value: Optional[float] = None  # Linear thermal bridge coefficient
    test_standard: str = "EN ISO 10077-2"


@dataclass
class Profile:
    """VEKA Window Profile with all technical data."""
    
    # Identification
    id: str
    system: VEKASystem
    profile_type: ProfileType
    name: str
    description: str
    
    # Dimensions
    dimensions: ProfileDimensions
    
    # Thermal performance
    thermal: ThermalData
    
    # Visual/CAD data
    svg_path: Optional[str] = None
    section_drawing_path: Optional[str] = None
    
    # Material properties
    reinforcement_possible: bool = True
    standard_colors: list = None
    surface_textures: list = None
    
    # Technical specs
    max_sash_weight_kg: Optional[float] = None
    max_element_height_mm: Optional[float] = None
    max_element_width_mm: Optional[float] = None
    
    # Sealing system
    seal_count: int = 2
    seal_type: str = "EPDM"
    
    # Metadata
    is_active: bool = True
    sort_order: int = 0
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.standard_colors is None:
            self.standard_colors = ["Weiß", "Braun", "Anthrazit", "Grau"]
        if self.surface_textures is None:
            self.surface_textures = ["Glatt", "Foliert", "Dekorfolie"]
    
    @property
    def display_name(self) -> str:
        """Human readable profile name."""
        return f"{self.system.display_name} - {self.name}"
    
    @property
    def technical_code(self) -> str:
        """Technical identification code."""
        return f"{self.system.code}_{self.profile_type.code.upper()}_{int(self.dimensions.depth_mm)}"
    
    def get_svg_geometry(self) -> Optional[str]:
        """Load SVG geometry data if available."""
        if not self.svg_path:
            return None
        
        try:
            import os
            if os.path.exists(self.svg_path):
                with open(self.svg_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'system_code': self.system.code,
            'profile_type_code': self.profile_type.code,
            'name': self.name,
            'description': self.description,
            'depth_mm': self.dimensions.depth_mm,
            'view_width_mm': self.dimensions.view_width_mm,
            'rebate_height_mm': self.dimensions.rebate_height_mm,
            'wall_thickness_mm': self.dimensions.wall_thickness_mm,
            'chamber_count': self.dimensions.chamber_count,
            'glazing_thickness_max': self.dimensions.glazing_thickness_max,
            'uf_value': self.thermal.uf_value,
            'psi_value': self.thermal.psi_value,
            'test_standard': self.thermal.test_standard,
            'svg_path': self.svg_path,
            'section_drawing_path': self.section_drawing_path,
            'reinforcement_possible': self.reinforcement_possible,
            'standard_colors': ','.join(self.standard_colors) if self.standard_colors else '',
            'surface_textures': ','.join(self.surface_textures) if self.surface_textures else '',
            'max_sash_weight_kg': self.max_sash_weight_kg,
            'max_element_height_mm': self.max_element_height_mm,
            'max_element_width_mm': self.max_element_width_mm,
            'seal_count': self.seal_count,
            'seal_type': self.seal_type,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """Create Profile from dictionary data."""
        # Find system and profile type by code
        system = next((s for s in VEKASystem if s.code == data['system_code']), VEKASystem.SOFTLINE_70)
        profile_type = next((pt for pt in ProfileType if pt.code == data['profile_type_code']), ProfileType.FRAME)
        
        # Create dimensions
        dimensions = ProfileDimensions(
            depth_mm=data['depth_mm'],
            view_width_mm=data['view_width_mm'],
            rebate_height_mm=data['rebate_height_mm'],
            wall_thickness_mm=data['wall_thickness_mm'],
            chamber_count=data['chamber_count'],
            glazing_thickness_max=data['glazing_thickness_max']
        )
        
        # Create thermal data
        thermal = ThermalData(
            uf_value=data['uf_value'],
            psi_value=data.get('psi_value'),
            test_standard=data.get('test_standard', 'EN ISO 10077-2')
        )
        
        # Parse list fields
        standard_colors = data.get('standard_colors', '').split(',') if data.get('standard_colors') else []
        surface_textures = data.get('surface_textures', '').split(',') if data.get('surface_textures') else []
        
        return cls(
            id=data['id'],
            system=system,
            profile_type=profile_type,
            name=data['name'],
            description=data['description'],
            dimensions=dimensions,
            thermal=thermal,
            svg_path=data.get('svg_path'),
            section_drawing_path=data.get('section_drawing_path'),
            reinforcement_possible=data.get('reinforcement_possible', True),
            standard_colors=standard_colors,
            surface_textures=surface_textures,
            max_sash_weight_kg=data.get('max_sash_weight_kg'),
            max_element_height_mm=data.get('max_element_height_mm'),
            max_element_width_mm=data.get('max_element_width_mm'),
            seal_count=data.get('seal_count', 2),
            seal_type=data.get('seal_type', 'EPDM'),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0),
            notes=data.get('notes')
        )


# Standard VEKA profile definitions for testing/fallback
STANDARD_PROFILES = [
    Profile(
        id="SL70_FRAME_70",
        system=VEKASystem.SOFTLINE_70,
        profile_type=ProfileType.FRAME,
        name="Blendrahmen 70mm",
        description="Standard Blendrahmen für Softline 70",
        dimensions=ProfileDimensions(
            depth_mm=70.0,
            view_width_mm=119.0,
            rebate_height_mm=20.0,
            wall_thickness_mm=2.8,
            chamber_count=5,
            glazing_thickness_max=41.0
        ),
        thermal=ThermalData(uf_value=1.3),
        max_sash_weight_kg=130.0,
        max_element_height_mm=2500.0,
        max_element_width_mm=1600.0
    ),
    Profile(
        id="SL70_SASH_70",
        system=VEKASystem.SOFTLINE_70,
        profile_type=ProfileType.SASH,
        name="Flügel 70mm",
        description="Standard Flügelprofil für Softline 70",
        dimensions=ProfileDimensions(
            depth_mm=70.0,
            view_width_mm=94.0,
            rebate_height_mm=20.0,
            wall_thickness_mm=2.8,
            chamber_count=5,
            glazing_thickness_max=41.0
        ),
        thermal=ThermalData(uf_value=1.3)
    ),
    Profile(
        id="SL82_FRAME_82",
        system=VEKASystem.SOFTLINE_82,
        profile_type=ProfileType.FRAME,
        name="Blendrahmen 82mm MD",
        description="Mitteldichtung Blendrahmen für Softline 82",
        dimensions=ProfileDimensions(
            depth_mm=82.0,
            view_width_mm=127.0,
            rebate_height_mm=24.0,
            wall_thickness_mm=3.0,
            chamber_count=6,
            glazing_thickness_max=53.0
        ),
        thermal=ThermalData(uf_value=1.0),
        max_sash_weight_kg=150.0,
        max_element_height_mm=2800.0,
        max_element_width_mm=1800.0
    )
]