"""
Position service for managing position-related operations.
"""
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import List, Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class PositionService:
    """Service for handling position-related operations."""
    
    def __init__(self, data_service=None):
        """Initialize the position service with optional data service."""
        if data_service:
            self.data_service = data_service
        else:
            # Create a new data service if none is provided
            from services.data_service import DataService
            self.data_service = DataService()
        
        logger.info("PositionService initialized")
    
    def get_position(self, position_id: str) -> Dict[str, Any]:
        """
        Get a position by ID.
        
        Args:
            position_id: ID of the position to retrieve
            
        Returns:
            Dictionary with position information formatted for UI
        """
        try:
            position = self.data_service.get_position(position_id)
            if not position:
                logger.warning(f"Position not found: {position_id}")
                return {}
            
            # Convert Position object to dictionary for UI
            position_dict = {
                'id': position.id,
                'number': position.id,
                'title': position.name,
                'template_code': position.template_code,
                'product_id': position.product_id,
                'product_name': position.product,
                'product_type': position.product_type,
                'product_ids': position.product_ids,
                'description': position.notes,
                'quantity': 1.0,  # Default
                'unit': 'Stück',  # Default
                'price': 0.0,  # Default
                'floor': position.floor,
                'existing_window_type': position.existing_window_type,
                'roller_shutter_type': position.roller_shutter_type,
                'status': position.status
            }
                
            return position_dict
        except Exception as e:
            logger.error(f"Error getting position {position_id}: {e}")
            return {}
    
    def get_positions(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all positions for a project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of position dictionaries
        """
        try:
            positions = self.data_service.get_positions(project_id)
            
            # Convert to dictionaries if they're model objects
            result = []
            for position in positions:
                if hasattr(position, 'to_dict'):
                    result.append(position.to_dict())
                else:
                    result.append(position)
            
            logger.info(f"Retrieved {len(result)} positions for project {project_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting positions for project {project_id}: {e}")
            return []
    
    def create_position(self, position_data: Dict[str, Any]) -> str:
        """
        Create a new position.
        
        Args:
            position_data: Position data to create
            
        Returns:
            Position ID
        """
        try:
            # Convert dict to Position object if needed
            from models.position import Position
            from models.product import ProductType
            
            # Handle product_type conversion
            product_type_str = ""
            if 'product_type' in position_data and position_data['product_type']:
                if isinstance(position_data['product_type'], ProductType):
                    product_type_str = position_data['product_type'].display_name
                else:
                    product_type_str = str(position_data['product_type'])
            
            # Create Position object
            position = Position(
                id="",  # Will be set by viewmodel
                project_id=position_data.get('project_id', 0),
                template_code=position_data.get('template_code', ''),
                name=position_data.get('title', ''),  # UI uses 'title'
                floor="Erdgeschoss",  # Default
                existing_window_type="Holz",  # Default
                roller_shutter_type="Nicht vorhanden",  # Default
                notes=position_data.get('description', ''),  # UI uses 'description'
                product=position_data.get('product_name', ''),
                product_id=position_data.get('product_id'),
                product_type=product_type_str,
                product_ids=position_data.get('product_ids', [])
            )
            
            # Use viewmodel to create position properly
            from viewmodels.position_viewmodel import PositionViewModel
            viewmodel = PositionViewModel(self.data_service)
            
            position_id = viewmodel.create_position_with_template(
                project_id=position.project_id,
                template_code=position.template_code,
                name=position.name,
                floor=position.floor,
                existing_window_type=position.existing_window_type,
                roller_shutter_type=position.roller_shutter_type,
                notes=position.notes,
                selected_products=[position.product] if position.product else [],
                product_id=position.product_id,
                product_type=position.product_type,
                product_ids=position.product_ids
            )
            
            logger.info(f"Position created with ID: {position_id}")
            return position_id
        except Exception as e:
            logger.error(f"Error creating position: {e}")
            return ""
    
    def save_position(self, position_data: Dict[str, Any]) -> str:
        """
        Save a position (create or update).
        
        Args:
            position_data: Position data to save
            
        Returns:
            Position ID
        """
        try:
            position_id = self.data_service.save_position(position_data)
            logger.info(f"Position saved with ID: {position_id}")
            return position_id
        except Exception as e:
            logger.error(f"Error saving position: {e}")
            return ""
    
    def delete_position(self, position_id: str) -> bool:
        """
        Delete a position.
        
        Args:
            position_id: ID of the position to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.data_service.delete_position(position_id)
            if success:
                logger.info(f"Position deleted: {position_id}")
            else:
                logger.warning(f"Failed to delete position: {position_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting position: {e}")
            return False
    
    def get_positions_by_project(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all positions for a specific project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of position dictionaries formatted for UI
        """
        try:
            # Get positions from data service (returns Position objects)
            positions = self.data_service.get_positions(project_id)
            
            # Convert to dictionaries for UI
            result = []
            for position in positions:
                # Only include main positions in the list (not sub-positions)
                if position.is_main_position:
                    position_dict = {
                        'id': position.id,
                        'number': position.id,  # Use position ID as number
                        'title': position.name,
                        'quantity': 1.0,  # Default quantity
                        'price': 0.0,  # Default price
                        'product_type': position.product_type,
                        'product_name': position.product,
                        'product_ids': position.product_ids,
                        'template_code': position.template_code,
                        'floor': position.floor,
                        'status': position.status
                    }
                    result.append(position_dict)
            
            logger.info(f"Retrieved {len(result)} main positions for project {project_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting positions for project {project_id}: {e}")
            return []
    
    def update_position_quantity(self, position_id: str, quantity: float) -> bool:
        """
        Update the quantity of a position based on measurements.
        
        Args:
            position_id: ID of the position to update
            quantity: New quantity value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            position = self.data_service.get_position(position_id)
            if not position:
                logger.warning(f"Position not found: {position_id}")
                return False
            
            # Update quantity based on the structure of position object
            if hasattr(position, 'quantity'):
                # For object-like position
                position.quantity = quantity
                position.has_measurement_data = True
            else:
                # For dict-like position
                position['quantity'] = quantity
                position['has_measurement_data'] = True
            
            # Save the updated position
            self.data_service.save_position(position)
            
            logger.info(f"Updated quantity for position {position_id}: {quantity:.2f}")
            return True
        except Exception as e:
            logger.error(f"Error updating position quantity: {e}")
            return False
