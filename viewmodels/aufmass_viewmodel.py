"""
AufmassViewModel for managing measurement data and business logic.
"""
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from typing import List, Optional, Dict, Any
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from models.project import Project
from services.data_service import DataService
from services.position_service import PositionService
from services.aufmass_service import AufmassService
from services.error_handler import error_handler, ErrorSeverity
from utils.logger import get_logger
logger = get_logger(__name__)

class AufmassViewModel(QObject):
    """ViewModel for managing measurements (Aufmass) data and logic."""
    
    # Signals with relevant data
    measurements_loaded = pyqtSignal(list)
    position_info_loaded = pyqtSignal(dict)
    measurement_added = pyqtSignal(dict)  # Include measurement data
    measurement_updated = pyqtSignal(dict)  # Include measurement data
    measurement_deleted = pyqtSignal(int)  # Include measurement ID
    error_occurred = pyqtSignal(str, str)  # (title, message)
    
    def __init__(self, position_service: PositionService, aufmass_service: AufmassService):
        """Initialize AufmassViewModel with required services."""
        super().__init__()
        self._position_service = position_service
        self._aufmass_service = aufmass_service
        self._current_position_id = None
        logger.info("AufmassViewModel initialized")
    
    @pyqtSlot(str)  # Position ID as string for consistency
    def set_position(self, position_id: str) -> None:
        """Set the current position and load its data."""
        self._current_position_id = position_id
        self.load_position_info()
        self.load_measurements()
        logger.info(f"Current position set to: {position_id}")
    
    @pyqtSlot()
    def load_position_info(self) -> None:
        """Load position information for the current position."""
        if not self._current_position_id:
            self.position_info_loaded.emit(None)
            return
        
        try:
            position_info = self._position_service.get_position(self._current_position_id)
            self.position_info_loaded.emit(position_info)
            logger.info(f"Loaded position info: {position_info.get('number', '')} - {position_info.get('title', '')}")
        except Exception as e:
            logger.error(f"Error loading position info: {e}")
            self.error_occurred.emit("Fehler", f"Fehler beim Laden der Positionsdaten: {str(e)}")
            self.position_info_loaded.emit(None)
    
    @pyqtSlot()
    def load_measurements(self) -> None:
        """Load measurements for the current position."""
        if not self._current_position_id:
            self.measurements_loaded.emit([])
            return
        
        try:
            measurements = self._aufmass_service.get_measurements_by_position(self._current_position_id)
            self.measurements_loaded.emit(measurements)
            logger.info(f"Loaded {len(measurements)} measurements for position {self._current_position_id}")
        except Exception as e:
            logger.error(f"Error loading measurements: {e}")
            self.error_occurred.emit("Fehler", f"Fehler beim Laden der Messungen: {str(e)}")
            self.measurements_loaded.emit([])
    
    @pyqtSlot(dict)
    def add_measurement(self, measurement_data: Dict[str, Any]) -> bool:
        """Add a new measurement for the current position."""
        if not self._current_position_id:
            self.error_occurred.emit("Fehler", "Keine Position ausgewählt.")
            return False
        
        try:
            # Add position_id to the data
            measurement_data['position_id'] = self._current_position_id
            
            # Create the measurement
            measurement_id = self._aufmass_service.create_measurement(measurement_data)
            measurement_data['id'] = measurement_id
            
            # Reload measurements
            self.load_measurements()
            
            # Update position quantity
            self._update_position_quantity()
            
            # Emit signal with the added measurement data
            self.measurement_added.emit(measurement_data)
            
            logger.info(f"Added measurement for position {self._current_position_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding measurement: {e}")
            self.error_occurred.emit("Fehler", f"Fehler beim Hinzufügen: {str(e)}")
            return False
    
    @pyqtSlot(dict)
    def update_measurement(self, measurement_data: Dict[str, Any]) -> bool:
        """Update an existing measurement."""
        if not self._current_position_id:
            self.error_occurred.emit("Fehler", "Keine Position ausgewählt.")
            return False
        
        try:
            # Ensure position_id is set
            if 'position_id' not in measurement_data:
                measurement_data['position_id'] = self._current_position_id
                
            # Update the measurement
            success = self._aufmass_service.update_measurement(measurement_data)
            
            if not success:
                raise ValueError(f"Failed to update measurement {measurement_data.get('id')}")
            
            # Reload measurements
            self.load_measurements()
            
            # Update position quantity
            self._update_position_quantity()
            
            # Emit signal with updated data
            self.measurement_updated.emit(measurement_data)
            
            logger.info(f"Updated measurement {measurement_data.get('id', '?')} for position {self._current_position_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating measurement: {e}")
            self.error_occurred.emit("Fehler", f"Fehler beim Aktualisieren: {str(e)}")
            return False
    
    @pyqtSlot(int)
    def delete_measurement(self, measurement_id: int) -> bool:
        """Delete a measurement."""
        try:
            # Delete the measurement
            success = self._aufmass_service.delete_measurement(measurement_id)
            
            if not success:
                raise ValueError(f"Failed to delete measurement {measurement_id}")
            
            # Reload measurements
            self.load_measurements()
            
            # Update position quantity
            self._update_position_quantity()
            
            # Emit signal with deleted measurement ID
            self.measurement_deleted.emit(measurement_id)
            
            logger.info(f"Deleted measurement {measurement_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting measurement: {e}")
            self.error_occurred.emit("Fehler", f"Fehler beim Löschen: {str(e)}")
            return False
    
    def _update_position_quantity(self) -> None:
        """Update the position's quantity based on measurements."""
        if not self._current_position_id:
            return
        
        try:
            # Calculate total from measurements
            measurements = self._aufmass_service.get_measurements_by_position(self._current_position_id)
            
            # Let the AufmassItem model perform the calculation to keep business logic consistent
            total = 0.0
            for measurement_data in measurements:
                # Create a model instance to use its calculation methods
                measurement = AufmassItem(
                    length=measurement_data.get('length', 0.0),
                    width=measurement_data.get('width', 0.0),
                    height=measurement_data.get('height', 0.0),
                    count=measurement_data.get('count', 0.0)
                )
                total += measurement.calculate_volume()
            
            # Update position quantity
            self._position_service.update_position_quantity(self._current_position_id, total)
            
            logger.info(f"Updated quantity for position {self._current_position_id}: {total:.2f}")
        except Exception as e:
            logger.error(f"Error updating position quantity: {e}")
            self.error_occurred.emit("Fehler", f"Fehler beim Aktualisieren der Menge: {str(e)}")
    
    @property
    def current_position_id(self) -> Optional[str]:
        """Get the current position ID."""
        return self._current_position_id
