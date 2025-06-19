"""
Service for dynamically extracting measurement fields from configuration files.
"""
import os
import json
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MeasurementField:
    """Definition of a measurement field with constraints and metadata."""
    
    key: str
    label: str
    description: str
    unit: str = "mm"
    min_value: float = 0.0
    max_value: float = 5000.0
    step: float = 1.0
    default_value: float = 0.0
    is_required: bool = True
    field_type: str = "dimension"  # dimension, offset, percentage, calculated
    category: str = "basic"  # basic, advanced, calculated
    
    @property
    def display_name(self) -> str:
        """Get display name with unit."""
        return f"{self.label} ({self.unit})"


class MeasurementSchemaService:
    """Service for extracting and managing dynamic measurement field definitions."""
    
    def __init__(self):
        """Initialize the service and load field definitions."""
        self.project_root = project_root
        self.glossary = {}
        self.schnitt_mapping = {}
        self.measurement_fields = {}
        
        self._load_configurations()
        self._extract_measurement_fields()
        
    def _load_configurations(self) -> None:
        """Load all configuration files."""
        try:
            # Load glossary
            glossary_path = os.path.join(self.project_root, 'assets', 'glossar.json')
            if os.path.exists(glossary_path):
                with open(glossary_path, 'r', encoding='utf-8') as f:
                    self.glossary = json.load(f)
                    
            # Load schnitt mapping
            mapping_path = os.path.join(self.project_root, 'config', 'schnitt_map.json')
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    self.schnitt_mapping = json.load(f)
                    
            logger.info("Configuration files loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration files: {e}")
            
    def _extract_measurement_fields(self) -> None:
        """Extract measurement field definitions from configurations."""
        
        # Core window dimensions - always required
        core_fields = {
            "inner_width": MeasurementField(
                key="inner_width",
                label="Lichte Breite",
                description="Innenmaß Breite zwischen den Leibungen",
                unit="mm",
                min_value=100,
                max_value=5000,
                is_required=True,
                category="basic"
            ),
            "inner_height": MeasurementField(
                key="inner_height", 
                label="Lichte Höhe",
                description="Innenmaß Höhe zwischen Sturz und Brüstung",
                unit="mm",
                min_value=100,
                max_value=5000,
                is_required=True,
                category="basic"
            ),
            "outer_width": MeasurementField(
                key="outer_width",
                label="Rohbaumaß Breite", 
                description="Außenmaß Breite der Rohbauöffnung",
                unit="mm",
                min_value=100,
                max_value=5000,
                is_required=True,
                category="basic"
            ),
            "outer_height": MeasurementField(
                key="outer_height",
                label="Rohbaumaß Höhe",
                description="Außenmaß Höhe der Rohbauöffnung", 
                unit="mm",
                min_value=100,
                max_value=5000,
                is_required=True,
                category="basic"
            ),
            "diagonal": MeasurementField(
                key="diagonal",
                label="Diagonale",
                description="Diagonalmaß zur Rechtwinkligkeitsprüfung",
                unit="mm",
                min_value=0,
                max_value=7000,
                is_required=False,
                field_type="calculated",
                category="basic"
            )
        }
        
        # Extended fields for ElementDesigner integration
        extended_fields = {
            "sill_height": MeasurementField(
                key="sill_height",
                label="Brüstungshöhe",
                description="Höhe der Brüstung unter dem Fenster",
                unit="mm",
                min_value=0,
                max_value=2000,
                default_value=900,
                is_required=False,
                category="advanced"
            ),
            "frame_depth": MeasurementField(
                key="frame_depth",
                label="Rahmenbreite",
                description="Breite des Blendrahmens",
                unit="mm",
                min_value=50,
                max_value=200,
                default_value=70,
                is_required=False,
                category="advanced"
            ),
            "mullion_offset": MeasurementField(
                key="mullion_offset",
                label="Pfosten-Versatz",
                description="Horizontaler Versatz des Mittelpfostens",
                unit="%",
                min_value=10,
                max_value=90,
                default_value=50,
                step=1,
                is_required=False,
                field_type="percentage",
                category="advanced"
            ),
            "transom_offset": MeasurementField(
                key="transom_offset", 
                label="Kämpfer-Versatz",
                description="Vertikaler Versatz des Kämpfers",
                unit="%",
                min_value=10,
                max_value=90,
                default_value=50,
                step=1,
                is_required=False,
                field_type="percentage",
                category="advanced"
            ),
            "glazing_thickness": MeasurementField(
                key="glazing_thickness",
                label="Verglasungsdicke",
                description="Dicke der Verglasung",
                unit="mm",
                min_value=4,
                max_value=50,
                default_value=24,
                is_required=False,
                category="advanced"
            ),
            "reveal_left": MeasurementField(
                key="reveal_left",
                label="Laibung links",
                description="Tiefe der linken Laibung",
                unit="mm",
                min_value=0,
                max_value=500,
                default_value=0,
                is_required=False,
                category="advanced"
            ),
            "reveal_right": MeasurementField(
                key="reveal_right",
                label="Laibung rechts", 
                description="Tiefe der rechten Laibung",
                unit="mm",
                min_value=0,
                max_value=500,
                default_value=0,
                is_required=False,
                category="advanced"
            ),
            "reveal_top": MeasurementField(
                key="reveal_top",
                label="Laibung oben",
                description="Tiefe der oberen Laibung",
                unit="mm",
                min_value=0,
                max_value=500,
                default_value=0,
                is_required=False,
                category="advanced"
            ),
            "reveal_bottom": MeasurementField(
                key="reveal_bottom",
                label="Laibung unten",
                description="Tiefe der unteren Laibung",
                unit="mm",
                min_value=0,
                max_value=500,
                default_value=0,
                is_required=False,
                category="advanced"
            )
        }
        
        # Combine all fields
        self.measurement_fields = {**core_fields, **extended_fields}
        
        # Add translations from glossary if available
        self._apply_glossary_translations()
        
        logger.info(f"Extracted {len(self.measurement_fields)} measurement fields")
        
    def _apply_glossary_translations(self) -> None:
        """Apply translations and descriptions from glossary."""
        if not self.glossary:
            return
            
        begriffe = self.glossary.get('begriffe', {})
        
        # Update labels and descriptions from glossary
        for field_key, field in self.measurement_fields.items():
            for term, description in begriffe.items():
                if term.lower() in field.label.lower():
                    field.description = description
                    break
                    
    def get_measurement_fields(self, category: Optional[str] = None) -> Dict[str, MeasurementField]:
        """Get measurement fields, optionally filtered by category."""
        if category is None:
            return self.measurement_fields
            
        return {
            key: field for key, field in self.measurement_fields.items()
            if field.category == category
        }
        
    def get_required_fields(self) -> Dict[str, MeasurementField]:
        """Get only required measurement fields."""
        return {
            key: field for key, field in self.measurement_fields.items()
            if field.is_required
        }
        
    def get_field_categories(self) -> List[str]:
        """Get list of all field categories."""
        categories = set()
        for field in self.measurement_fields.values():
            categories.add(field.category)
        return sorted(list(categories))
        
    def validate_measurement_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate measurement data against field definitions."""
        errors = []
        
        # Check required fields
        for key, field in self.get_required_fields().items():
            if key not in data or data[key] is None:
                errors.append(f"Pflichtfeld '{field.label}' fehlt")
                continue
                
            value = data[key]
            if not isinstance(value, (int, float)):
                errors.append(f"'{field.label}' muss eine Zahl sein")
                continue
                
            if value < field.min_value or value > field.max_value:
                errors.append(f"'{field.label}' muss zwischen {field.min_value} und {field.max_value} {field.unit} liegen")
                
        return len(errors) == 0, errors
        
    def calculate_derived_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived values like diagonal, area, etc."""
        result = data.copy()
        
        # Calculate diagonal if not provided
        inner_width = data.get('inner_width', 0)
        inner_height = data.get('inner_height', 0)
        
        if inner_width > 0 and inner_height > 0:
            import math
            diagonal = math.sqrt(inner_width**2 + inner_height**2)
            result['diagonal'] = round(diagonal, 1)
            
            # Calculate area
            result['area'] = round((inner_width * inner_height) / 1000000, 2)  # mm² to m²
            
            # Calculate perimeter
            result['perimeter'] = round(2 * (inner_width + inner_height) / 1000, 2)  # mm to m
            
        return result
        
    def get_database_columns(self) -> List[str]:
        """Get list of database column names for measurements table."""
        base_columns = ['id', 'position_id', 'project_id', 'created_at', 'updated_at']
        measurement_columns = list(self.measurement_fields.keys())
        calculated_columns = ['area', 'perimeter']
        
        return base_columns + measurement_columns + calculated_columns