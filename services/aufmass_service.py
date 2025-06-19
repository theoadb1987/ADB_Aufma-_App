# Korrigierte Importe für services/aufmass_service.py
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from typing import List, Dict, Any, Optional
from utils.logger import get_logger
from models.aufmass_item import AufmassItem

logger = get_logger(__name__)


class AufmassService:
    """Service for handling measurement (Aufmass) operations."""
    
    def __init__(self, data_service=None):
        """Initialize the aufmass service with optional data service."""
        if data_service:
            self.data_service = data_service
        else:
            # Create a new data service if none is provided
            from services.data_service import DataService
            self.data_service = DataService()
        
        logger.info("AufmassService initialized")
    
    def get_measurements_by_position(self, position_id: str) -> List[Dict[str, Any]]:
        """
        Get all measurements for a position.
        
        Args:
            position_id: ID of the position
            
        Returns:
            List of measurement dictionaries
        """
        try:
            measurements = []
            
            # First, try to get measurements specifically for this position
            try:
                measurements = self.data_service.get_measurements_by_position(position_id)
            except AttributeError:
                # If the method doesn't exist, try an alternative approach
                logger.info("get_measurements_by_position method not found, trying alternative")
                measurement = self.data_service.get_measurement(position_id)
                if measurement:
                    measurements = [measurement]
            
            # Process measurements into expected format
            result = []
            for measurement in measurements:
                # Convert to dictionary if it's a model object
                if hasattr(measurement, 'to_dict'):
                    measurement_dict = measurement.to_dict()
                else:
                    measurement_dict = measurement
                
                result.append(measurement_dict)
            
            logger.info(f"Retrieved {len(result)} measurements for position {position_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting measurements for position {position_id}: {e}")
            return []
    
    def get_measurement(self, position_id: str) -> Optional[Any]:
        """
        Get a single measurement for a position.
        
        Args:
            position_id: ID of the position
            
        Returns:
            Measurement object or None if not found
        """
        try:
            measurement = self.data_service.get_measurement(position_id)
            if measurement:
                logger.info(f"Retrieved measurement for position {position_id}")
            else:
                logger.warning(f"No measurement found for position {position_id}")
            return measurement
        except Exception as e:
            logger.error(f"Error getting measurement for position {position_id}: {e}")
            return None
    
    def create_measurement(self, measurement_data: Dict[str, Any]) -> int:
        """
        Create a new measurement.
        
        Args:
            measurement_data: Measurement data to create
            
        Returns:
            ID of the created measurement
        """
        try:
            measurement = AufmassItem.from_dict(measurement_data)
            measurement_id = self.data_service.save_measurement(measurement)
            logger.info(f"Measurement created with ID: {measurement_id}")
            return measurement_id
        except Exception as e:
            logger.error(f"Error creating measurement: {e}")
            return 0
    
    def update_measurement(self, measurement_data: Dict[str, Any]) -> int:
        """
        Update an existing measurement.
        
        Args:
            measurement_data: Measurement data to update
            
        Returns:
            ID of the updated measurement or 0 on failure
        """
        try:
            measurement = AufmassItem.from_dict(measurement_data)
            measurement_id = self.data_service.save_measurement(measurement)
            logger.info(f"Measurement updated: {measurement_id}")
            return measurement_id
        except Exception as e:
            logger.error(f"Error updating measurement: {e}")
            return 0
    
    def delete_measurement(self, measurement_id: int) -> bool:
        """
        Delete a measurement.
        
        Args:
            measurement_id: ID of the measurement to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.data_service.delete_measurement(measurement_id)
            if success:
                logger.info(f"Measurement deleted: {measurement_id}")
            else:
                logger.warning(f"Failed to delete measurement: {measurement_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting measurement: {e}")
            return False
    
    def calculate_total(self, measurements: List[Dict[str, Any]]) -> float:
        """
        Calculate the total quantity from a list of measurements.
        
        Args:
            measurements: List of measurement dictionaries
            
        Returns:
            Total quantity (length * width * height * count)
        """
        try:
            total = 0.0
            for measurement in measurements:
                length = measurement.get('length', 0.0)
                width = measurement.get('width', 0.0)
                height = measurement.get('height', 0.0)
                count = measurement.get('count', 0.0)
                
                total += length * width * height * count
            
            logger.info(f"Calculated total: {total:.2f}")
            return total
        except Exception as e:
            logger.error(f"Error calculating total: {e}")
            return 0.0
