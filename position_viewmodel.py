"""
Position ViewModel for managing position-specific operations and data.
"""
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from typing import List, Optional, Dict, Any
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from models.position import Position
from models.aufmass_item import AufmassItem
from services.data_service import DataService
from services.error_handler import error_handler, ErrorSeverity
from utils.logger import get_logger

logger = get_logger(__name__)


class PositionViewModel(QObject):
    """ViewModel for position-related operations and measurement data."""
    
    # Signals
    position_details_updated = pyqtSignal(Position)
    position_status_changed = pyqtSignal(Position)
    position_validation_error = pyqtSignal(str)
    measurement_updated = pyqtSignal(AufmassItem)
    products_selected = pyqtSignal(list)
    
    def __init__(self, data_service: DataService):
        """Initialize with data service."""
        super().__init__()
        self.data_service = data_service
        self.selected_products = []
        self.next_position_id = 1
        logger.info("PositionViewModel initialized")
    
    @pyqtSlot(int, str, str, str, str, str, list)
    def create_position(self, project_id: int, name: str, floor: str, 
                       existing_window_type: str, roller_shutter_type: str,
                       notes: str, selected_products: List[str]) -> Optional[str]:
        """Create a new position with the provided details (legacy method)."""
        return self.create_position_with_template(
            project_id=project_id,
            template_code="",
            name=name,
            floor=floor,
            existing_window_type=existing_window_type,
            roller_shutter_type=roller_shutter_type,
            notes=notes,
            selected_products=selected_products,
            product_id=None
        )
    
    def create_position_with_template(self, project_id: int, template_code: str, 
                                    name: str, floor: str, existing_window_type: str, 
                                    roller_shutter_type: str, notes: str, 
                                    selected_products: List[str], product_id: Optional[int] = None,
                                    product_type: str = "", product_ids: List[int] = None) -> Optional[str]:
        """Create a new position with the provided details."""
        try:
            # Validate essential fields
            if not name:
                self.position_validation_error.emit("Positionsname darf nicht leer sein.")
                return None
            
            if not selected_products:
                self.position_validation_error.emit("Bitte wählen Sie mindestens ein Produkt aus.")
                return None
            
            # Determine main product (window) and accessories
            main_product = None
            accessories = []
            
            # Check for window products first (prioritize them)
            for product in selected_products:
                if "fenster" in product.lower():
                    main_product = product
                    break
            
            # If no window product found, use the first product as main
            if not main_product and selected_products:
                main_product = selected_products[0]
            
            # All other products become accessories
            accessories = [p for p in selected_products if p != main_product]
            
            # Get next position ID for this project
            position_id = self.get_next_position_number(project_id)
            
            main_position = Position(
                id=position_id,
                project_id=project_id,
                template_code=template_code,
                name=name,
                floor=floor,
                existing_window_type=existing_window_type,
                roller_shutter_type=roller_shutter_type,
                notes=notes,
                product=main_product,
                product_id=product_id,
                product_type=product_type,
                product_ids=product_ids or [],
                accessories=[],  # Main position has empty accessories list
                is_main_position=True,
                parent_id=None,
                color="#30d158",  # Default color for main positions
                is_selected=True,
                is_expanded=True,  # Sub-positions visible by default
                status="Ausstehend"
            )
            
            # Save main position
            self.data_service.save_position(main_position)
            
            # Create sub-positions for accessories
            for i, accessory in enumerate(accessories):
                sub_position_id = f"{position_id}.{i+1}"
                
                sub_position = Position(
                    id=sub_position_id,
                    project_id=project_id,
                    name=name,
                    floor=floor,
                    existing_window_type=existing_window_type,
                    roller_shutter_type=roller_shutter_type,
                    notes=notes,
                    product=accessory,
                    accessories=[],  # Sub-positions have empty accessories list
                    is_main_position=False,
                    parent_id=position_id,
                    color="#64d2ff",  # Different color for sub-positions
                    is_selected=False,
                    status="Ausstehend"
                )
                
                # Save sub-position
                self.data_service.save_position(sub_position)
            
            # Emit signal for UI update
            self.position_details_updated.emit(main_position)
            
            logger.info(f"Created position: {name} with {len(selected_products)} products")
            return position_id
        except Exception as e:
            self._handle_error("Failed to create position", str(e))
            return None
    
    @pyqtSlot(str, str, str, str, str, str, list)
    def update_position(self, position_id: str, name: str, floor: str,
                      existing_window_type: str, roller_shutter_type: str,
                      notes: str, selected_products: List[str]) -> None:
        """Update an existing position with the provided details."""
        try:
            # Get the position
            position = self.data_service.get_position(position_id)
            if not position:
                raise ValueError(f"Position with ID {position_id} not found")
            
            # Update fields
            position.name = name
            position.floor = floor
            position.existing_window_type = existing_window_type
            position.roller_shutter_type = roller_shutter_type
            position.notes = notes
            position.updated_at = datetime.now()
            
            # Handle product changes
            if position.is_main_position and selected_products:
                # Find main product (window)
                main_product = None
                for product in selected_products:
                    if "fenster" in product.lower():
                        main_product = product
                        break
                
                if not main_product and selected_products:
                    main_product = selected_products[0]
                
                position.product = main_product
                
                # Get all sub-positions that still exist
                sub_positions = []
                accessories = [p for p in selected_products if p != main_product]
                
                # Get existing sub-positions
                all_positions = self.data_service.get_positions(position.project_id)
                existing_sub_positions = [p for p in all_positions if p.parent_id == position_id]
                
                # Update or create sub-positions
                for i, accessory in enumerate(accessories):
                    sub_id = f"{position_id}.{i+1}"
                    
                    # Find existing sub-position with matching id
                    existing_sub = next((p for p in existing_sub_positions if p.id == sub_id), None)
                    
                    if existing_sub:
                        # Update existing sub-position
                        existing_sub.name = name
                        existing_sub.floor = floor
                        existing_sub.existing_window_type = existing_window_type
                        existing_sub.roller_shutter_type = roller_shutter_type
                        existing_sub.notes = notes
                        existing_sub.product = accessory
                        existing_sub.updated_at = datetime.now()
                        self.data_service.save_position(existing_sub)
                    else:
                        # Create new sub-position
                        new_sub = Position(
                            id=sub_id,
                            project_id=position.project_id,
                            name=name,
                            floor=floor,
                            existing_window_type=existing_window_type,
                            roller_shutter_type=roller_shutter_type,
                            notes=notes,
                            product=accessory,
                            accessories=[],
                            is_main_position=False,
                            parent_id=position_id,
                            color="#64d2ff",
                            is_selected=False,
                            status="Ausstehend"
                        )
                        self.data_service.save_position(new_sub)
                
                # Delete sub-positions that are no longer needed
                for sub in existing_sub_positions:
                    sub_id_parts = sub.id.split('.')
                    if len(sub_id_parts) > 1:
                        sub_idx = int(sub_id_parts[1])
                        if sub_idx > len(accessories):  # This sub-position is no longer needed
                            self.data_service.delete_position(sub.id)
            
            # Save position
            self.data_service.save_position(position)
            
            # Emit signal for UI update
            self.position_details_updated.emit(position)
            
            logger.info(f"Updated position: {name} (ID: {position_id})")
        except Exception as e:
            self._handle_error("Failed to update position", str(e))
    
    @pyqtSlot(str, str)
    def update_position_status(self, position_id: str, new_status: str) -> None:
        """Update the status of a position."""
        try:
            position = self.data_service.get_position(position_id)
            if not position:
                raise ValueError(f"Position with ID {position_id} not found")
            
            position.update_status(new_status)
            self.data_service.save_position(position)
            
            # Emit signal for UI update
            self.position_status_changed.emit(position)
            
            logger.info(f"Updated position status: {position.name} -> {new_status}")
        except Exception as e:
            self._handle_error("Failed to update position status", str(e))
    
    @pyqtSlot(str, int, int, int, int, int, str, list)
    def save_measurement(self, position_id: str, inner_width: int, inner_height: int,
                       outer_width: int, outer_height: int, diagonal: int,
                       special_notes: str, photos: List[str]) -> None:
        """Save measurement data for a position."""
        try:
            # Get the position to access project_id
            position = self.data_service.get_position(position_id)
            if not position:
                raise ValueError(f"Position with ID {position_id} not found")
            
            # Check if measurement already exists
            existing_measurement = self.data_service.get_measurement(position_id)
            
            if existing_measurement:
                # Update existing measurement
                existing_measurement.inner_width = inner_width
                existing_measurement.inner_height = inner_height
                existing_measurement.outer_width = outer_width
                existing_measurement.outer_height = outer_height
                existing_measurement.diagonal = diagonal
                existing_measurement.special_notes = special_notes
                existing_measurement.photos = photos
                existing_measurement.updated_at = datetime.now()
                
                measurement = existing_measurement
            else:
                # Create new measurement
                measurement = AufmassItem(
                    position_id=position_id,
                    project_id=position.project_id,
                    inner_width=inner_width,
                    inner_height=inner_height,
                    outer_width=outer_width,
                    outer_height=outer_height,
                    diagonal=diagonal,
                    special_notes=special_notes,
                    photos=photos
                )
            
            # Save measurement
            measurement_id = self.data_service.save_measurement(measurement)
            if measurement.id == 0:
                measurement.id = measurement_id
            
            # Update position status to indicate measurement is complete
            if position.status == "Ausstehend":
                position.update_status("Aufgemessen")
                self.data_service.save_position(position)
                self.position_status_changed.emit(position)
            
            # Emit signal for UI update
            self.measurement_updated.emit(measurement)
            
            logger.info(f"Saved measurement for position {position_id}")
        except Exception as e:
            self._handle_error("Failed to save measurement", str(e))
    
    @pyqtSlot(list)
    def set_selected_products(self, products: List[str]) -> None:
        """Set the currently selected products."""
        self.selected_products = products
        self.products_selected.emit(products)
        logger.info(f"Selected {len(products)} products")
    
    @pyqtSlot()
    def get_selected_products(self) -> List[str]:
        """Get the currently selected products."""
        return self.selected_products
    
    def get_positions(self, project_id: int) -> List[Position]:
        """Get all positions for a project."""
        try:
            positions = self.data_service.get_positions(project_id)
            return positions
        except Exception as e:
            self._handle_error("Failed to get positions", str(e))
            return []
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get a position by ID."""
        try:
            position = self.data_service.get_position(position_id)
            return position
        except Exception as e:
            self._handle_error("Failed to get position", str(e))
            return None
    
    def get_available_products(self) -> List[Dict[str, Any]]:
        """Get a list of available products."""
        # This would typically come from a product service or database
        # For this example, we'll return a static list
        return [
            {"id": 1, "name": "Kunststofffenster Standard", "price": 249.99},
            {"id": 2, "name": "Aluminium-Fenster Premium", "price": 499.99},
            {"id": 3, "name": "Holzfenster Natur", "price": 399.99},
            {"id": 4, "name": "Rolllade Standard", "price": 149.99},
            {"id": 5, "name": "Insektenschutz", "price": 89.99},
            {"id": 6, "name": "Fensterbrett innen", "price": 59.99},
            {"id": 7, "name": "Fensterbrett außen", "price": 79.99}
        ]
    
    @pyqtSlot(int)
    def get_next_position_number(self, project_id: int) -> str:
        """Get the next available position number for a project."""
        try:
            positions = self.data_service.get_positions(project_id)
            
            # Extract main position numbers (not sub-positions)
            main_position_numbers = []
            for position in positions:
                if position.is_main_position:
                    try:
                        # Handle position IDs that may be in format "1", "2", etc.
                        position_id = position.id.split('.')[0]  # Get main part before any dot
                        position_num = int(position_id)
                        main_position_numbers.append(position_num)
                    except (ValueError, IndexError):
                        # Ignore position IDs that can't be processed
                        logger.warning(f"Skipping non-standard position ID: {position.id}")
                        pass
            
            # Find the next available number
            if main_position_numbers:
                next_num = max(main_position_numbers) + 1
            else:
                next_num = 1
            
            self.next_position_id = next_num
            logger.info(f"Next position number for project {project_id}: {next_num}")
            return str(next_num)
        except Exception as e:
            self._handle_error("Failed to get next position number", str(e))
            return "1"  # Fallback to 1 if something goes wrong
    
    def _handle_error(self, message: str, details: str = None, 
                    severity: ErrorSeverity = ErrorSeverity.ERROR) -> None:
        """Handle errors through error handler service."""
        error_type = "position_error"
        error_handler.handle_error(error_type, message, severity, details)
