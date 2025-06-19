# aufmass_view.py - PyQt5 zu PyQt6 migriert
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt6.QtCore import pyqtSlot

from ui.dynamic_aufmass_ui import DynamicAufmassUI
from services.position_service import PositionService
from services.aufmass_service import AufmassService
from services.designer_bridge_service import DesignerBridgeService
from viewmodels.aufmass_viewmodel import AufmassViewModel
from utils.logger import get_logger

logger = get_logger(__name__)


class AufmassView(QWidget):
    """View for managing measurements (Aufmass) for positions."""
    
    def __init__(self, parent=None, viewmodel=None):
        """Initialize the Aufmass view."""
        super().__init__(parent)
        
        # Set viewmodel
        self.viewmodel = viewmodel
        
        # Initialize services
        self._position_service = PositionService()
        self._aufmass_service = AufmassService()
        self._designer_bridge = DesignerBridgeService(self)
        
        # Current state
        self._current_position_id = None
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Dynamic Aufmass UI component
        self.aufmass_ui = DynamicAufmassUI()
        layout.addWidget(self.aufmass_ui)
        
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect signals from Dynamic AufmassUI
        self.aufmass_ui.measurement_data_changed.connect(self._on_measurement_data_changed)
        self.aufmass_ui.designer_requested.connect(self._open_designer)
        
    def set_position(self, position_id):
        """Set the current position and load its measurements."""
        self._current_position_id = position_id
        self._load_position_info()
        self._load_measurements()
        
    def _load_position_info(self):
        """Load position information."""
        if not self._current_position_id:
            self.aufmass_ui.set_position(None)
            return
            
        position_info = self._position_service.get_position(self._current_position_id)
        self.aufmass_ui.set_position(self._current_position_id, position_info)
        
    def _load_measurements(self):
        """Load measurements for the current position."""
        if not self._current_position_id:
            return
            
        try:
            measurement = self._aufmass_service.get_measurement(self._current_position_id)
            if measurement is None:
                logger.warning(f"No measurement found for position {self._current_position_id}")
                return
            self.aufmass_ui.load_measurement_data(measurement.to_dict())
        except Exception as e:
            logger.error(f"Failed to load measurement for position {self._current_position_id}: {e}")
            # Clear UI if measurement can't be loaded
            self.aufmass_ui.load_measurement_data({})
            
    @pyqtSlot(dict)
    def _on_measurement_data_changed(self, measurement_data):
        """Handle measurement data changes."""
        if not self._current_position_id:
            return
            
        try:
            # Save or update measurement data
            measurement_data['position_id'] = self._current_position_id
            measurement_data['project_id'] = self._get_project_id()
            
            # Check if measurement exists
            existing_measurement = self._aufmass_service.get_measurement(self._current_position_id)
            
            if existing_measurement:
                # Update existing measurement
                measurement_data['id'] = existing_measurement.id
                success = self._aufmass_service.update_measurement(measurement_data)
                if not success:
                    logger.error(f"Failed to update measurement for position {self._current_position_id}")
            else:
                # Create new measurement
                measurement_id = self._aufmass_service.create_measurement(measurement_data)
                if measurement_id == 0:
                    logger.error(f"Failed to create measurement for position {self._current_position_id}")
                
            logger.info(f"Saved measurement data for position: {self._current_position_id}")
            
        except Exception as e:
            logger.error(f"Failed to save measurement data: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {str(e)}")
            
    @pyqtSlot(str, dict)
    def _open_designer(self, position_id, measurement_data):
        """Open Element Designer with measurement data."""
        try:
            success = self._designer_bridge.open_designer(position_id, measurement_data, self)
            if success:
                logger.info(f"Successfully opened Element Designer for position: {position_id}")
            else:
                QMessageBox.warning(self, "Fehler", "Element Designer konnte nicht geöffnet werden.")
                
        except Exception as e:
            logger.error(f"Failed to open Element Designer: {e}")
            QMessageBox.critical(self, "Fehler", f"Element Designer Fehler: {str(e)}")
            
    def _get_project_id(self) -> int:
        """Get the current project ID."""
        if not self._current_position_id:
            return 0
            
        try:
            position = self._position_service.get_position(self._current_position_id)
            return position.get('project_id', 0) if position else 0
        except Exception:
            return 0
        
    @pyqtSlot(dict)
    def _add_measurement(self, measurement_data):
        """Add a new measurement."""
        if not self._current_position_id:
            QMessageBox.warning(self, "Fehler", "Keine Position ausgewählt.")
            return
            
        try:
            # Add position_id to the data
            measurement_data['position_id'] = self._current_position_id
            
            # Create the measurement
            self._aufmass_service.create_measurement(measurement_data)
            
            # Reload measurements
            self._load_measurements()
            
            # Update position quantity
            self._update_position_quantity()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Hinzufügen: {str(e)}")
            
    @pyqtSlot(dict)
    def _update_measurement(self, measurement_data):
        """Update an existing measurement."""
        if not self._current_position_id:
            return
            
        try:
            # Update the measurement
            self._aufmass_service.update_measurement(measurement_data)
            
            # Reload measurements
            self._load_measurements()
            
            # Update position quantity
            self._update_position_quantity()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Aktualisieren: {str(e)}")
            
    @pyqtSlot(int)
    def _delete_measurement(self, measurement_id):
        """Delete a measurement."""
        try:
            # Delete the measurement
            self._aufmass_service.delete_measurement(measurement_id)
            
            # Reload measurements
            self._load_measurements()
            
            # Update position quantity
            self._update_position_quantity()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen: {str(e)}")
            
    def _update_position_quantity(self):
        """Update the position's quantity based on measurements."""
        if not self._current_position_id:
            return
            
        try:
            # Calculate total from measurements
            measurements = self._aufmass_service.get_measurements_by_position(self._current_position_id)
            total = 0.0
            
            for measurement in measurements:
                length = measurement.get('length', 0.0)
                width = measurement.get('width', 0.0)
                height = measurement.get('height', 0.0)
                count = measurement.get('count', 0.0)
                
                total += length * width * height * count
                
            # Update position quantity
            self._position_service.update_position_quantity(self._current_position_id, total)
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Aktualisieren der Menge: {str(e)}")
            
    def refresh(self):
        """Refresh the view."""
        self._load_position_info()
        self._load_measurements()