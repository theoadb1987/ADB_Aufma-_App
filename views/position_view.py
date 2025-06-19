# position_view.py - PyQt5 zu PyQt6 migriert
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from ui.position_ui import PositionListUI, PositionDetailUI
from services.position_service import PositionService
from services.product_service import ProductService
from services.data_service import DataService
from viewmodels.position_viewmodel import PositionViewModel
from utils.logger import get_logger

logger = get_logger(__name__)


class PositionView(QWidget):
    """View for managing positions within a project."""
    
    # Signals
    position_selected = pyqtSignal(int)
    new_position_created = pyqtSignal(str)  # Signal emitted when a new position is created
    
    def __init__(self, parent=None, viewmodel=None):
        """Initialize the position view."""
        super().__init__(parent)
        
        # Set viewmodel
        self.viewmodel = viewmodel
        
        # Initialize services
        self._position_service = PositionService()
        self._product_service = ProductService()
        self._data_service = DataService()
        
        # Current state
        self._current_project_id = None
        self._current_position_id = None
        
        self._setup_ui()
        self._connect_signals()
        self._load_templates()
        self._load_products()
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Position list (left side)
        self.position_list_ui = PositionListUI()
        main_layout.addWidget(self.position_list_ui, 1)
        
        # Position details (right side)
        right_layout = QVBoxLayout()
        
        self.position_detail_ui = PositionDetailUI()
        right_layout.addWidget(self.position_detail_ui)
        
        # Buttons for the form
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Speichern")
        self.save_button.clicked.connect(self._save_position)
        
        self.new_button = QPushButton("Neu")
        self.new_button.clicked.connect(self._new_position)
        
        self.delete_button = QPushButton("Löschen")
        self.delete_button.clicked.connect(self._delete_position)
        
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        
        right_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout, 2)
        
    def _connect_signals(self):
        """Connect signals and slots."""
        # When a position is selected in the list
        self.position_list_ui.position_selected.connect(self._load_position)
        # Forward the position selection signal
        self.position_list_ui.position_selected.connect(self.position_selected)
        
        # When a product is selected in the details
        self.position_detail_ui.product_selected.connect(self._on_product_selected)
        
        # When a product type is selected in the details
        self.position_detail_ui.product_type_selected.connect(self._on_product_type_selected)
        
        # Connect to viewmodel signals for automatic refresh
        if self.viewmodel:
            self.viewmodel.position_details_updated.connect(self._on_position_updated)
            self.viewmodel.position_status_changed.connect(self._on_position_updated)
        
    def set_project(self, project_id):
        """Set the current project and load its positions."""
        self._current_project_id = project_id
        self._load_positions()
        
    def _load_positions(self):
        """Load positions for the current project."""
        if not self._current_project_id:
            return
            
        positions = self._position_service.get_positions_by_project(self._current_project_id)
        self.position_list_ui.set_positions(positions)
        
        # Clear the detail form
        self.position_detail_ui.clear()
        self._current_position_id = None
        
    def _load_position(self, position_id):
        """Load a position's details into the form."""
        self._current_position_id = position_id
        position_data = self._position_service.get_position(position_id)
        self.position_detail_ui.set_data(position_data)
        
    def _save_position(self):
        """Save the current position data."""
        if not self._current_project_id:
            QMessageBox.warning(self, "Fehler", "Kein Projekt ausgewählt.")
            return
            
        # Get data from the form
        position_data = self.position_detail_ui.get_data()
        
        try:
            if self._current_position_id:
                # Update existing position
                position_data['id'] = self._current_position_id
                self._position_service.update_position(position_data)
            else:
                # Create new position
                position_data['project_id'] = self._current_project_id
                new_id = self._position_service.create_position(position_data)
                self._current_position_id = new_id
                
                # Emit signal for new position creation
                if new_id:
                    self.new_position_created.emit(new_id)
                
            # Refresh the position list
            self._load_positions()
            
            # Select the current position in the list
            if self._current_position_id:
                self.position_list_ui.select_position(self._current_position_id)
                
            QMessageBox.information(self, "Erfolg", "Position gespeichert.")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {str(e)}")
            
    def _new_position(self):
        """Create a new position."""
        self._current_position_id = None
        self.position_detail_ui.clear()
        
    def _delete_position(self):
        """Delete the current position."""
        if not self._current_position_id:
            QMessageBox.warning(self, "Fehler", "Keine Position ausgewählt.")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Position löschen",
            "Möchten Sie diese Position wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete the position
                self._position_service.delete_position(self._current_position_id)
                
                # Clear the form and reset the current position
                self.position_detail_ui.clear()
                self._current_position_id = None
                
                # Refresh the position list
                self._load_positions()
                
                QMessageBox.information(self, "Erfolg", "Position gelöscht.")
                
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen: {str(e)}")
                
    def _on_product_selected(self, product_id):
        """Handle product selection."""
        product = self._product_service.get_product(product_id)
        
        if product:
            # Update price field with product price (optional)
            # This would require additional code to get the form data,
            # update the price, and set the data back
            pass
    
    def _on_product_type_selected(self, product_type):
        """Handle product type selection."""
        logger.info(f"Product type selected: {product_type.display_name}")
        # The product type is already set in the UI through the signal
        # Additional logic can be added here if needed
    
    @pyqtSlot(object)
    def _on_position_updated(self, position):
        """Handle position updates from viewmodel."""
        logger.info(f"Position updated via signal: {position.name}")
        # Refresh the position list to show the new/updated position
        self._load_positions()
        
        # If this is a new position, select it in the list and emit signal
        if position.id:
            self.position_list_ui.select_position(position.id)
            # Emit signal to notify other components (e.g., MainWindow for tab switching)
            self.new_position_created.emit(position.id)
            
    def refresh(self):
        """Refresh the view."""
        self._load_positions()
        
    def _load_products(self):
        """Load product data into the position detail UI."""
        try:
            products = self._product_service.get_all_products()
            self.position_detail_ui.set_products(products)
            logger.info(f"Loaded {len(products)} products")
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            # Fallback wird von der UI selbst gehandhabt
    
    def prepare_product_selection_dialog(self):
        """Prepare the product selection dialog with product data."""
        products = self._product_service.get_all_products()
        self.position_detail_ui.set_products(products)
    
    def _load_templates(self):
        """Load position templates into the UI."""
        try:
            templates = self._data_service.get_position_templates()
            self.position_detail_ui.set_templates(templates)
            logger.info(f"Loaded {len(templates)} position templates")
        except Exception as e:
            logger.error(f"Failed to load position templates: {e}")
            QMessageBox.warning(self, "Warnung", f"Vorlagen konnten nicht geladen werden: {str(e)}")