# ui/aufmass_ui.py - PyQt5 zu PyQt6 migriert
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QPushButton, QDoubleSpinBox,
                            QComboBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import pyqtSignal, Qt


class AufmassUI(QWidget):
    """UI component for displaying and editing measurements (Aufmass)."""
    
    # Signals
    measurement_added = pyqtSignal(dict)
    measurement_updated = pyqtSignal(dict)
    measurement_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize the Aufmass UI component."""
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Position info display
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position:"))
        self.position_label = QLabel()
        self.position_label.setStyleSheet("font-weight: bold;")
        position_layout.addWidget(self.position_label, 1)
        main_layout.addLayout(position_layout)
        
        # Measurements table
        self.measurements_table = QTableWidget()
        self.measurements_table.setColumnCount(6)
        self.measurements_table.setHorizontalHeaderLabels(
            ["ID", "Länge", "Breite", "Höhe", "Anzahl", "Gesamt"]
        )
        self.measurements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.measurements_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.measurements_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.measurements_table)
        
        # Measurement input form
        form_layout = QFormLayout()
        
        # Length
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(0, 999.99)
        self.length_spin.setDecimals(2)
        self.length_spin.setSuffix(" m")
        form_layout.addRow("Länge:", self.length_spin)
        
        # Width
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0, 999.99)
        self.width_spin.setDecimals(2)
        self.width_spin.setSuffix(" m")
        form_layout.addRow("Breite:", self.width_spin)
        
        # Height
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0, 999.99)
        self.height_spin.setDecimals(2)
        self.height_spin.setSuffix(" m")
        form_layout.addRow("Höhe:", self.height_spin)
        
        # Count
        self.count_spin = QDoubleSpinBox()
        self.count_spin.setRange(0, 999.99)
        self.count_spin.setDecimals(2)
        form_layout.addRow("Anzahl:", self.count_spin)
        
        # Description
        self.description_edit = QLineEdit()
        form_layout.addRow("Beschreibung:", self.description_edit)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Hinzufügen")
        self.add_button.clicked.connect(self._add_measurement)
        
        self.update_button = QPushButton("Aktualisieren")
        self.update_button.clicked.connect(self._update_measurement)
        self.update_button.setEnabled(False)  # Disabled until a row is selected
        
        self.delete_button = QPushButton("Löschen")
        self.delete_button.clicked.connect(self._delete_measurement)
        self.delete_button.setEnabled(False)  # Disabled until a row is selected
        
        self.clear_button = QPushButton("Leeren")
        self.clear_button.clicked.connect(self._clear_inputs)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout)
        
        # Summary
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(QLabel("Gesamtmenge:"))
        self.total_label = QLabel("0.00")
        self.total_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.total_label)
        
        summary_layout.addWidget(QLabel("Einheit:"))
        self.unit_label = QLabel()
        self.unit_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.unit_label)
        
        main_layout.addLayout(summary_layout)
        
        # Connect table selection signal
        self.measurements_table.itemSelectionChanged.connect(self._on_selection_changed)
        
    def set_position_info(self, position_info):
        """Set the position information display."""
        if not position_info:
            self.position_label.setText("")
            self.unit_label.setText("")
            return
            
        position_text = f"{position_info.get('number', '')} - {position_info.get('title', '')}"
        self.position_label.setText(position_text)
        self.unit_label.setText(position_info.get('unit', ''))
        
    def set_measurements(self, measurements):
        """Set the measurements to display in the table."""
        self.measurements_table.setRowCount(0)
        total = 0.0
        
        for measurement in measurements:
            row = self.measurements_table.rowCount()
            self.measurements_table.insertRow(row)
            
            # ID (hidden for internal use)
            id_item = QTableWidgetItem(str(measurement.get('id', '')))
            self.measurements_table.setItem(row, 0, id_item)
            
            # Length
            length = measurement.get('length', 0.0)
            length_item = QTableWidgetItem(f"{length:.2f}")
            length_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.measurements_table.setItem(row, 1, length_item)
            
            # Width
            width = measurement.get('width', 0.0)
            width_item = QTableWidgetItem(f"{width:.2f}")
            width_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.measurements_table.setItem(row, 2, width_item)
            
            # Height
            height = measurement.get('height', 0.0)
            height_item = QTableWidgetItem(f"{height:.2f}")
            height_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.measurements_table.setItem(row, 3, height_item)
            
            # Count
            count = measurement.get('count', 0.0)
            count_item = QTableWidgetItem(f"{count:.2f}")
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.measurements_table.setItem(row, 4, count_item)
            
            # Total (length * width * height * count)
            total_value = length * width * height * count
            total_item = QTableWidgetItem(f"{total_value:.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.measurements_table.setItem(row, 5, total_item)
            
            # Add to total
            total += total_value
            
        # Update total display
        self.total_label.setText(f"{total:.2f}")
        
    def get_input_data(self):
        """Get the measurement data from input fields."""
        return {
            'length': self.length_spin.value(),
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
            'count': self.count_spin.value(),
            'description': self.description_edit.text()
        }
        
    def _add_measurement(self):
        """Handle adding a new measurement."""
        measurement_data = self.get_input_data()
        
        # Calculate total value
        total = (measurement_data['length'] * 
                measurement_data['width'] * 
                measurement_data['height'] * 
                measurement_data['count'])
                
        # Only add if there's actually a value
        if total > 0:
            self.measurement_added.emit(measurement_data)
            self._clear_inputs()
        
    def _update_measurement(self):
        """Handle updating the selected measurement."""
        selected_rows = self.measurements_table.selectedIndexes()
        
        if not selected_rows:
            return
            
        # Get the row of the first selected cell
        row = selected_rows[0].row()
        
        # Get measurement ID
        measurement_id = int(self.measurements_table.item(row, 0).text())
        
        # Get new data
        measurement_data = self.get_input_data()
        measurement_data['id'] = measurement_id
        
        # Emit signal for the view to handle
        self.measurement_updated.emit(measurement_data)
        
        # Clear selection and inputs
        self.measurements_table.clearSelection()
        self._clear_inputs()
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
    def _delete_measurement(self):
        """Handle deleting the selected measurement."""
        selected_rows = self.measurements_table.selectedIndexes()
        
        if not selected_rows:
            return
            
        # Get the row of the first selected cell
        row = selected_rows[0].row()
        
        # Get measurement ID
        measurement_id = int(self.measurements_table.item(row, 0).text())
        
        # Emit signal for the view to handle
        self.measurement_deleted.emit(measurement_id)
        
        # Clear selection and inputs
        self.measurements_table.clearSelection()
        self._clear_inputs()
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
    def _clear_inputs(self):
        """Clear all input fields."""
        self.length_spin.setValue(0.0)
        self.width_spin.setValue(0.0)
        self.height_spin.setValue(0.0)
        self.count_spin.setValue(0.0)
        self.description_edit.clear()
        
    def _on_selection_changed(self):
        """Handle table selection change."""
        selected_rows = self.measurements_table.selectedIndexes()
        
        if not selected_rows:
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
            
        # Get the row of the first selected cell
        row = selected_rows[0].row()
        
        # Enable update and delete buttons
        self.update_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Fill the input fields with the selected measurement data
        length = float(self.measurements_table.item(row, 1).text())
        width = float(self.measurements_table.item(row, 2).text())
        height = float(self.measurements_table.item(row, 3).text())
        count = float(self.measurements_table.item(row, 4).text())
        
        self.length_spin.setValue(length)
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
        self.count_spin.setValue(count)