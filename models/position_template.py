"""
Position Template models for predefined position types.
"""
from dataclasses import dataclass
from typing import Optional
from models.product import ProductType


@dataclass
class PositionTemplate:
    """Template for creating standard positions."""
    
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    w_mm: int = 0
    h_mm: int = 0
    default_product_type: Optional[ProductType] = None
    is_active: bool = True
    sort_order: int = 0
    
    @property
    def display_name(self) -> str:
        """Get display name for UI dropdowns."""
        if self.w_mm and self.h_mm:
            return f"{self.name} ({self.w_mm}×{self.h_mm}mm)"
        return self.name
    
    @property
    def dimensions_text(self) -> str:
        """Get formatted dimensions text."""
        if self.w_mm and self.h_mm:
            return f"{self.w_mm} × {self.h_mm} mm"
        return "Keine Vorgabe"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'w_mm': self.w_mm,
            'h_mm': self.h_mm,
            'default_product_type': self.default_product_type.code if self.default_product_type else None,
            'is_active': self.is_active,
            'sort_order': self.sort_order
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PositionTemplate':
        """Create PositionTemplate from dictionary data."""
        # Find product type by code
        default_product_type = None
        if data.get('default_product_type'):
            for pt in ProductType:
                if pt.code == data['default_product_type']:
                    default_product_type = pt
                    break
        
        return cls(
            id=data.get('id'),
            code=data.get('code', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            category=data.get('category', ''),
            w_mm=data.get('w_mm', 0),
            h_mm=data.get('h_mm', 0),
            default_product_type=default_product_type,
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0)
        )


# Standard position templates
STANDARD_TEMPLATES = [
    PositionTemplate(
        code="WZ_WIN",
        name="Wohnzimmer-Fenster",
        description="Standard Wohnzimmerfenster",
        category="Fenster",
        w_mm=1200,
        h_mm=1400,
        default_product_type=ProductType.WINDOW,
        sort_order=1
    ),
    PositionTemplate(
        code="SZ_WIN",
        name="Schlafzimmer-Fenster",
        description="Standard Schlafzimmerfenster",
        category="Fenster",
        w_mm=1000,
        h_mm=1200,
        default_product_type=ProductType.WINDOW,
        sort_order=2
    ),
    PositionTemplate(
        code="KUE_WIN",
        name="Küchen-Fenster",
        description="Küchenfenster über Arbeitsplatte",
        category="Fenster",
        w_mm=800,
        h_mm=600,
        default_product_type=ProductType.WINDOW,
        sort_order=3
    ),
    PositionTemplate(
        code="BAD_WIN",
        name="Badezimmer-Fenster",
        description="Kleines Badezimmerfenster",
        category="Fenster",
        w_mm=600,
        h_mm=800,
        default_product_type=ProductType.WINDOW,
        sort_order=4
    ),
    PositionTemplate(
        code="HAU_TUR",
        name="Haustür",
        description="Standard Eingangstür",
        category="Türen",
        w_mm=900,
        h_mm=2100,
        default_product_type=ProductType.WINDOW,
        sort_order=5
    ),
    PositionTemplate(
        code="KUE_TUR",
        name="Küchentür",
        description="Küchentür zum Garten",
        category="Türen",
        w_mm=900,
        h_mm=2100,
        default_product_type=ProductType.WINDOW,
        sort_order=6
    ),
    PositionTemplate(
        code="TER_TUR",
        name="Terrassentür",
        description="Große Terrassentür",
        category="Türen",
        w_mm=1600,
        h_mm=2200,
        default_product_type=ProductType.WINDOW,
        sort_order=7
    ),
    PositionTemplate(
        code="ROL_STD",
        name="Standard Rollladen",
        description="Rollladen für Standardfenster",
        category="Sonnenschutz",
        w_mm=1200,
        h_mm=1400,
        default_product_type=ProductType.ROLLER_SHUTTER,
        sort_order=8
    ),
    PositionTemplate(
        code="FLY_STD",
        name="Standard Fliegengitter",
        description="Fliegengitter für Standardfenster",
        category="Insektenschutz",
        w_mm=1200,
        h_mm=1400,
        default_product_type=ProductType.FLY_SCREEN,
        sort_order=9
    ),
    PositionTemplate(
        code="PLI_STD",
        name="Standard Plissee",
        description="Plissee für Standardfenster",
        category="Sonnenschutz",
        w_mm=1200,
        h_mm=1400,
        default_product_type=ProductType.PLEATED_BLIND,
        sort_order=10
    )
]