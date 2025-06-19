"""
Dynamic Aufmass UI component that generates form fields based on measurement schema.
"""
import sys
import os
from typing import Dict, Any, Optional

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QDoubleSpinBox, QPushButton, QGroupBox,
                            QScrollArea, QMessageBox, QTabWidget)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from services.measurement_schema_service import MeasurementSchemaService, MeasurementField
from utils.logger import get_logger

logger = get_logger(__name__)


class DynamicAufmassUI(QWidget):
    """Dynamic measurement UI that generates form fields from schema."""
    
    # Signals
    measurement_data_changed = pyqtSignal(dict)
    designer_requested = pyqtSignal(str, dict)  # position_id, measurement_data
    
    def __init__(self, parent=None):
        """Initialize the dynamic aufmass UI."""
        super().__init__(parent)
        
        # Services
        self.schema_service = MeasurementSchemaService()
        
        # State
        self.current_position_id = None
        self.field_widgets = {}  # key -> QDoubleSpinBox
        self.measurement_data = {}
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the UI components dynamically."""
        layout = QVBoxLayout(self)
        
        # Position info header
        self.position_info_label = QLabel()
        self.position_info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.position_info_label.setStyleSheet("color: #2196F3; margin: 10px 0px;")
        layout.addWidget(self.position_info_label)
        
        # Create tabbed interface for field categories
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs for each category
        categories = self.schema_service.get_field_categories()
        for category in categories:
            tab = self._create_category_tab(category)
            category_name = self._get_category_display_name(category)
            self.tab_widget.addTab(tab, category_name)
        
        # Validation status
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.validation_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.calculate_button = QPushButton("🧮 Werte berechnen")
        self.calculate_button.clicked.connect(self._calculate_values)
        button_layout.addWidget(self.calculate_button)
        
        self.clear_button = QPushButton("🗑️ Zurücksetzen")
        self.clear_button.clicked.connect(self._clear_form)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        self.designer_button = QPushButton("🎨 Element-Designer öffnen")
        self.designer_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.designer_button.clicked.connect(self._open_designer)
        self.designer_button.setEnabled(False)  # Disabled until validation passes
        button_layout.addWidget(self.designer_button)
        
        layout.addLayout(button_layout)
        
        # Summary section
        self.summary_group = QGroupBox("📊 Berechnete Werte")
        summary_layout = QFormLayout(self.summary_group)
        
        self.area_label = QLabel("0.00 m²")
        self.area_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        summary_layout.addRow("Fläche:", self.area_label)
        
        self.perimeter_label = QLabel("0.00 m")
        self.perimeter_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        summary_layout.addRow("Umfang:", self.perimeter_label)
        
        self.diagonal_label = QLabel("0.0 mm")
        self.diagonal_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        summary_layout.addRow("Diagonale:", self.diagonal_label)
        
        layout.addWidget(self.summary_group)
        
    def _create_category_tab(self, category: str) -> QWidget:
        """Create a tab widget for a specific field category."""
        tab_widget = QWidget()
        
        # Create scroll area for the tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        content_widget = QWidget()
        form_layout = QFormLayout(content_widget)
        form_layout.setSpacing(10)
        
        # Get fields for this category
        fields = self.schema_service.get_measurement_fields(category)
        
        for field_key, field in fields.items():
            widget = self._create_field_widget(field)
            self.field_widgets[field_key] = widget
            
            # Create label with tooltip
            label = QLabel(field.display_name)
            if field.is_required:
                label.setText(f"{field.display_name} *")
                label.setStyleSheet("font-weight: bold;")
            
            if field.description:
                label.setToolTip(field.description)
                widget.setToolTip(field.description)
            
            form_layout.addRow(label, widget)
        
        scroll_area.setWidget(content_widget)
        
        # Main layout for the tab
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.addWidget(scroll_area)
        
        return tab_widget
        
    def _create_field_widget(self, field: MeasurementField) -> QDoubleSpinBox:
        """Create a widget for a measurement field."""
        widget = QDoubleSpinBox()
        widget.setRange(field.min_value, field.max_value)
        widget.setSingleStep(field.step)
        widget.setValue(field.default_value)
        widget.setSuffix(f" {field.unit}")
        widget.setMinimumWidth(150)
        
        # Set decimals based on unit
        if field.unit == "mm":
            widget.setDecimals(1)
        elif field.unit == "%":
            widget.setDecimals(0)
        else:
            widget.setDecimals(2)
        
        # Required fields styling
        if field.is_required:
            widget.setStyleSheet("QDoubleSpinBox { border: 2px solid #ff9800; }")
        
        return widget
        
    def _get_category_display_name(self, category: str) -> str:
        """Get display name for category."""
        category_names = {
            "basic": "📏 Grundmaße",
            "advanced": "⚙️ Erweiterte Maße",
            "calculated": "🧮 Berechnete Werte"
        }
        return category_names.get(category, category.title())
        
    def _connect_signals(self):
        """Connect widget signals."""
        for field_key, widget in self.field_widgets.items():
            widget.valueChanged.connect(self._on_value_changed)
            
    def _on_value_changed(self):
        """Handle value changes in form fields."""
        self._update_measurement_data()
        self._validate_form()
        self._update_calculated_values()
        
    def _update_measurement_data(self):
        """Update measurement data from form widgets."""
        self.measurement_data = {}
        
        for field_key, widget in self.field_widgets.items():
            self.measurement_data[field_key] = widget.value()
            
        # Add position ID if available
        if self.current_position_id:
            self.measurement_data['position_id'] = self.current_position_id
            
        self.measurement_data_changed.emit(self.measurement_data)
        
    def _validate_form(self) -> bool:
        """Validate the form and update UI accordingly."""
        is_valid, errors = self.schema_service.validate_measurement_data(self.measurement_data)
        
        if is_valid:
            self.validation_label.setText("✅ Alle Pflichtfelder ausgefüllt")
            self.validation_label.setStyleSheet("color: green; font-weight: bold;")
            self.designer_button.setEnabled(True)
            
            # Update required field styling
            for field_key, widget in self.field_widgets.items():
                field = self.schema_service.measurement_fields[field_key]
                if field.is_required:
                    widget.setStyleSheet("QDoubleSpinBox { border: 2px solid #4caf50; }")
        else:
            self.validation_label.setText(f"❌ {'; '.join(errors)}")
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")
            self.designer_button.setEnabled(False)
            
            # Update required field styling
            for field_key, widget in self.field_widgets.items():
                field = self.schema_service.measurement_fields[field_key]
                if field.is_required:
                    if field_key not in self.measurement_data or self.measurement_data[field_key] <= 0:
                        widget.setStyleSheet("QDoubleSpinBox { border: 2px solid #f44336; }")
                    else:
                        widget.setStyleSheet("QDoubleSpinBox { border: 2px solid #4caf50; }")
        
        return is_valid
        
    def _update_calculated_values(self):
        """Update calculated values display."""
        calculated_data = self.schema_service.calculate_derived_values(self.measurement_data)
        
        # Update display labels
        self.area_label.setText(f"{calculated_data.get('area', 0.0):.2f} m²")
        self.perimeter_label.setText(f"{calculated_data.get('perimeter', 0.0):.2f} m")
        self.diagonal_label.setText(f"{calculated_data.get('diagonal', 0.0):.1f} mm")
        
        # Update diagonal field if it exists
        if 'diagonal' in self.field_widgets:
            diagonal_value = calculated_data.get('diagonal', 0.0)
            self.field_widgets['diagonal'].setValue(diagonal_value)
        
    def _calculate_values(self):
        """Calculate and update derived values."""
        self._update_calculated_values()
        QMessageBox.information(self, "Berechnung", "Abgeleitete Werte wurden berechnet.")
        
    def _clear_form(self):
        """Clear all form fields."""
        for field_key, widget in self.field_widgets.items():
            field = self.schema_service.measurement_fields[field_key]
            widget.setValue(field.default_value)
            
        self.validation_label.setText("")
        
    def _open_designer(self):
        """Open the Element Designer with current measurement data."""
        if not self.current_position_id:
            QMessageBox.warning(self, "Fehler", "Keine Position ausgewählt.")
            return
            
        if not self._validate_form():
            QMessageBox.warning(self, "Fehler", "Bitte füllen Sie alle Pflichtfelder aus.")
            return
            
        # Calculate final values
        final_data = self.schema_service.calculate_derived_values(self.measurement_data)
        
        # Emit signal to open designer with position ID as string
        self.designer_requested.emit(str(self.current_position_id), final_data)
        
    def set_position(self, position_id: str, position_info: Optional[Dict[str, Any]] = None):
        """Set the current position and update UI."""
        self.current_position_id = position_id
        
        if position_info:
            position_text = f"Position: {position_info.get('number', '')} - {position_info.get('title', '')}"
            self.position_info_label.setText(position_text)
        else:
            self.position_info_label.setText(f"Position: {position_id}")
            
        self._update_measurement_data()
        
    def load_measurement_data(self, data: Dict[str, Any]):
        """Load existing measurement data into the form."""
        for field_key, widget in self.field_widgets.items():
            if field_key in data:
                widget.setValue(data[field_key])
                
        self._update_measurement_data()
        self._validate_form()
        self._update_calculated_values()
        
    def get_measurement_data(self) -> Dict[str, Any]:
        """Get current measurement data including calculated values."""
        return self.schema_service.calculate_derived_values(self.measurement_data)