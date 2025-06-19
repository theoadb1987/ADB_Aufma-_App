"""
Service for bridging measurement data to the Element Designer.
"""
import sys
import os
from typing import Dict, Any, Optional

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

from views.element_designer_view import ElementDesignerView
from models.window_element import WindowType
from utils.logger import get_logger

logger = get_logger(__name__)


class DesignerBridgeService(QObject):
    """Service for launching Element Designer with measurement data."""
    
    # Signals
    designer_opened = pyqtSignal(str)  # position_id
    designer_closed = pyqtSignal(str)  # position_id
    
    def __init__(self, parent=None):
        """Initialize the designer bridge service."""
        super().__init__(parent)
        self.active_designers = {}  # position_id -> dialog
        
    def open_designer(self, position_id: str, measurement_data: Dict[str, Any], 
                     parent_widget=None) -> bool:
        """Open Element Designer with measurement data."""
        try:
            # Check if designer is already open for this position
            if position_id in self.active_designers:
                existing_dialog = self.active_designers[position_id]
                if existing_dialog.isVisible():
                    existing_dialog.raise_()
                    existing_dialog.activateWindow()
                    return True
                else:
                    # Remove stale reference
                    del self.active_designers[position_id]
            
            # Create designer dialog
            dialog = self._create_designer_dialog(position_id, measurement_data, parent_widget)
            
            # Store reference
            self.active_designers[position_id] = dialog
            
            # Show dialog
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()
            
            # Emit signal
            self.designer_opened.emit(position_id)
            
            logger.info(f"Opened Element Designer for position: {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open Element Designer: {e}")
            if parent_widget:
                QMessageBox.critical(parent_widget, "Fehler", 
                                   f"Element Designer konnte nicht geöffnet werden: {e}")
            return False
            
    def _create_designer_dialog(self, position_id: str, measurement_data: Dict[str, Any],
                               parent_widget=None) -> QDialog:
        """Create a designer dialog with measurement data pre-loaded."""
        
        # Create dialog
        dialog = QDialog(parent_widget)
        dialog.setWindowTitle(f"Element Designer - Position {position_id}")
        dialog.setModal(False)  # Allow interaction with main window
        dialog.resize(1200, 800)
        
        # Layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create designer view
        designer_view = ElementDesignerView(dialog)
        layout.addWidget(designer_view)
        
        # Configure designer with measurement data
        self._configure_designer(designer_view, measurement_data)
        
        # Handle dialog close
        def on_dialog_finished():
            if position_id in self.active_designers:
                del self.active_designers[position_id]
            self.designer_closed.emit(position_id)
            logger.info(f"Closed Element Designer for position: {position_id}")
            
        dialog.finished.connect(on_dialog_finished)
        
        return dialog
        
    def _configure_designer(self, designer_view: ElementDesignerView, 
                           measurement_data: Dict[str, Any]):
        """Configure the designer view with measurement data."""
        try:
            # Extract key measurements
            inner_width = measurement_data.get('inner_width', 0)
            inner_height = measurement_data.get('inner_height', 0)
            mullion_offset = measurement_data.get('mullion_offset', 50)
            transom_offset = measurement_data.get('transom_offset', 50)
            
            # Set window dimensions in designer
            if hasattr(designer_view, 'set_window_dimensions'):
                designer_view.set_window_dimensions(inner_width, inner_height)
            
            # Set mullion and transom offsets
            if hasattr(designer_view, 'mullion_offset'):
                designer_view.mullion_offset = mullion_offset
            if hasattr(designer_view, 'transom_offset'):
                designer_view.transom_offset = transom_offset
                
            # Update any parameter sliders/controls
            if hasattr(designer_view, 'update_parameters'):
                designer_view.update_parameters({
                    'width': inner_width,
                    'height': inner_height,
                    'mullion_offset': mullion_offset,
                    'transom_offset': transom_offset
                })
                
            # Select appropriate window type based on measurements
            window_type = self._suggest_window_type(measurement_data)
            if window_type and hasattr(designer_view, 'set_window_type'):
                designer_view.set_window_type(window_type)
                
            logger.info(f"Configured designer with dimensions: {inner_width}x{inner_height}mm")
            
        except Exception as e:
            logger.error(f"Failed to configure designer: {e}")
            
    def _suggest_window_type(self, measurement_data: Dict[str, Any]) -> Optional[WindowType]:
        """Suggest appropriate window type based on measurements."""
        try:
            inner_width = measurement_data.get('inner_width', 0)
            inner_height = measurement_data.get('inner_height', 0)
            
            # Simple heuristics for window type selection
            if inner_width <= 0 or inner_height <= 0:
                return None
                
            # Large windows -> suggest two-panel
            if inner_width > 1500:
                return WindowType.FT_DKD  # 2-flg. Dreh-Kipp
            
            # Standard size -> suggest dreh-kipp
            elif inner_width > 600 and inner_height > 800:
                return WindowType.FT_DK  # Dreh-Kipp
            
            # Small windows -> suggest fixed or simple opening
            elif inner_width < 600 or inner_height < 600:
                return WindowType.FT_F  # Festverglasung
            
            # Default to dreh-kipp
            return WindowType.FT_DK
            
        except Exception as e:
            logger.error(f"Failed to suggest window type: {e}")
            return WindowType.FT_DK
            
    def close_designer(self, position_id: str):
        """Close designer for a specific position."""
        if position_id in self.active_designers:
            dialog = self.active_designers[position_id]
            dialog.close()
            
    def close_all_designers(self):
        """Close all open designers."""
        for dialog in list(self.active_designers.values()):
            dialog.close()
        self.active_designers.clear()
        
    def is_designer_open(self, position_id: str) -> bool:
        """Check if designer is open for a position."""
        if position_id not in self.active_designers:
            return False
        return self.active_designers[position_id].isVisible()
        
    def get_open_designers(self) -> list:
        """Get list of position IDs with open designers."""
        return [pos_id for pos_id, dialog in self.active_designers.items() 
                if dialog.isVisible()]