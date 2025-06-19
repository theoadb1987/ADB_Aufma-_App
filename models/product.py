"""
Product models for the application.
Defines product types and related data structures.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import os


class ProductType(Enum):
    """Product type enumeration with icons and display information."""
    
    WINDOW = ("WIN", "Fenster", "ICON_WIN.svg", "Fenster und Türen")
    ROLLER_SHUTTER = ("ROL", "Rollladen", "ICON_ROL.svg", "Rollläden und Jalousien")  
    FLY_SCREEN = ("FLY", "Fliegengitter", "ICON_FLY.svg", "Insektenschutz")
    PLEATED_BLIND = ("PLI", "Plissee", "ICON_PLI.svg", "Plissees und Faltstores")
    AWNING = ("MAR", "Markise", "ICON_MAR.svg", "Markisen und Sonnenschutz")
    
    def __init__(self, code: str, display_name: str, icon_file: str, description: str):
        self.code = code
        self.display_name = display_name
        self.icon_file = icon_file
        self.description = description
    
    @property
    def icon_path(self) -> str:
        """Get full path to the icon file."""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        return str(project_root / "assets" / "icons" / "products" / self.icon_file)
    
    def icon_exists(self) -> bool:
        """Check if the icon file exists."""
        return os.path.exists(self.icon_path)


@dataclass
class Product:
    """Product data model."""
    
    id: Optional[int] = None
    product_type: ProductType = ProductType.WINDOW
    name: str = ""
    manufacturer: str = ""
    model: str = ""
    price: float = 0.0
    description: str = ""
    color: str = "#FFFFFF"
    material: str = ""
    dimensions_mm: str = ""  # Format: "width x height x depth"
    weight_kg: Optional[float] = None
    energy_rating: str = ""
    warranty_years: int = 0
    is_active: bool = True
    sort_order: int = 0
    notes: str = ""
    
    @property
    def display_name(self) -> str:
        """Get display name for UI."""
        if self.manufacturer and self.model:
            return f"{self.manufacturer} {self.model}"
        elif self.name:
            return self.name
        else:
            return f"{self.product_type.display_name} (ohne Name)"
    
    @property
    def full_description(self) -> str:
        """Get full description including type and specs."""
        parts = [self.product_type.display_name]
        
        if self.name:
            parts.append(f"- {self.name}")
        if self.manufacturer:
            parts.append(f"({self.manufacturer})")
        if self.dimensions_mm:
            parts.append(f"[{self.dimensions_mm}]")
            
        return " ".join(parts)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'product_type_code': self.product_type.code,
            'name': self.name,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'price': self.price,
            'description': self.description,
            'color': self.color,
            'material': self.material,
            'dimensions_mm': self.dimensions_mm,
            'weight_kg': self.weight_kg,
            'energy_rating': self.energy_rating,
            'warranty_years': self.warranty_years,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Create Product from dictionary data."""
        # Find product type by code
        product_type = ProductType.WINDOW  # Default
        for pt in ProductType:
            if pt.code == data.get('product_type_code', ''):
                product_type = pt
                break
        
        return cls(
            id=data.get('id'),
            product_type=product_type,
            name=data.get('name', ''),
            manufacturer=data.get('manufacturer', ''),
            model=data.get('model', ''),
            price=data.get('price', 0.0),
            description=data.get('description', ''),
            color=data.get('color', '#FFFFFF'),
            material=data.get('material', ''),
            dimensions_mm=data.get('dimensions_mm', ''),
            weight_kg=data.get('weight_kg'),
            energy_rating=data.get('energy_rating', ''),
            warranty_years=data.get('warranty_years', 0),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0),
            notes=data.get('notes', '')
        )


# Sample products for testing/fallback
SAMPLE_PRODUCTS = [
    Product(
        id=1,
        product_type=ProductType.WINDOW,
        name="Standard Kunststoff-Fenster",
        manufacturer="VEKA",
        model="Softline 70",
        price=450.00,
        description="Energieeffizientes Kunststoff-Fenster",
        color="#FFFFFF",
        material="PVC",
        dimensions_mm="1200 x 1400 x 70",
        energy_rating="A+",
        warranty_years=10
    ),
    Product(
        id=2,
        product_type=ProductType.ROLLER_SHUTTER,
        name="Aluminium Rollladen",
        manufacturer="Roma",
        model="Zipscreen",
        price=280.00,
        description="Motorisierter Aluminium-Rollladen",
        color="#7F8C8D",
        material="Aluminium",
        dimensions_mm="1200 x 1400",
        warranty_years=5
    ),
    Product(
        id=3,
        product_type=ProductType.FLY_SCREEN,
        name="Spannrahmen Fliegengitter",
        manufacturer="Neher",
        model="Basic",
        price=89.00,
        description="Stabiler Spannrahmen mit Fiberglas-Gewebe",
        color="#2C3E50",
        material="Aluminium + Fiberglas",
        dimensions_mm="1200 x 1400 x 25",
        warranty_years=2
    )
]