"""
Test Element Designer bridge functionality.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QTimer

from services.designer_bridge_service import DesignerBridgeService
from models.window_element import WindowType


@pytest.fixture
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def bridge_service(qapp):
    """Create designer bridge service for testing."""
    return DesignerBridgeService()


class TestDesignerBridgeService:
    """Test designer bridge service functionality."""
    
    def test_service_initialization(self, bridge_service):
        """Test that bridge service initializes correctly."""
        assert bridge_service is not None
        assert hasattr(bridge_service, 'active_designers')
        assert isinstance(bridge_service.active_designers, dict)
        assert len(bridge_service.active_designers) == 0
    
    def test_window_type_suggestion(self, bridge_service):
        """Test window type suggestion based on measurements."""
        # Large window should suggest two-panel
        large_data = {'inner_width': 2000, 'inner_height': 1500}
        window_type = bridge_service._suggest_window_type(large_data)
        assert window_type == WindowType.FT_DKD
        
        # Standard window should suggest dreh-kipp
        standard_data = {'inner_width': 1200, 'inner_height': 1000}
        window_type = bridge_service._suggest_window_type(standard_data)
        assert window_type == WindowType.FT_DK
        
        # Small window should suggest fixed
        small_data = {'inner_width': 400, 'inner_height': 400}
        window_type = bridge_service._suggest_window_type(small_data)
        assert window_type == WindowType.FT_F
        
        # Invalid data should return default
        invalid_data = {'inner_width': 0, 'inner_height': 0}
        window_type = bridge_service._suggest_window_type(invalid_data)
        assert window_type is None
    
    @patch('services.designer_bridge_service.ElementDesignerView')
    @patch('services.designer_bridge_service.QDialog')
    def test_open_designer(self, mock_dialog_class, mock_designer_view_class, bridge_service, qapp):
        """Test opening Element Designer dialog."""
        # Mock dialog and view
        mock_dialog = Mock()
        mock_dialog.isVisible.return_value = True
        mock_dialog_class.return_value = mock_dialog
        
        mock_view = Mock()
        mock_designer_view_class.return_value = mock_view
        
        # Test data
        position_id = "test_position_001"
        measurement_data = {
            'inner_width': 1200,
            'inner_height': 1000,
            'mullion_offset': 50,
            'transom_offset': 50
        }
        
        # Open designer
        result = bridge_service.open_designer(position_id, measurement_data)
        
        # Verify result
        assert result is True
        assert position_id in bridge_service.active_designers
        
        # Verify dialog was created and shown
        mock_dialog_class.assert_called_once()
        mock_dialog.show.assert_called_once()
        mock_dialog.raise_.assert_called_once()
        mock_dialog.activateWindow.assert_called_once()
        
        # Verify designer view was created
        mock_designer_view_class.assert_called_once()
    
    def test_designer_already_open(self, bridge_service):
        """Test behavior when designer is already open for a position."""
        position_id = "test_position_001"
        
        # Mock existing dialog
        mock_dialog = Mock()
        mock_dialog.isVisible.return_value = True
        bridge_service.active_designers[position_id] = mock_dialog
        
        # Try to open again
        with patch.object(bridge_service, '_create_designer_dialog') as mock_create:
            result = bridge_service.open_designer(position_id, {})
            
            # Should not create new dialog
            mock_create.assert_not_called()
            
            # Should raise existing dialog
            mock_dialog.raise_.assert_called_once()
            mock_dialog.activateWindow.assert_called_once()
            
            assert result is True
    
    def test_close_designer(self, bridge_service):
        """Test closing designer for a specific position."""
        position_id = "test_position_001"
        
        # Mock dialog
        mock_dialog = Mock()
        bridge_service.active_designers[position_id] = mock_dialog
        
        # Close designer
        bridge_service.close_designer(position_id)
        
        # Verify dialog was closed
        mock_dialog.close.assert_called_once()
    
    def test_close_all_designers(self, bridge_service):
        """Test closing all open designers."""
        # Mock multiple dialogs
        mock_dialog1 = Mock()
        mock_dialog2 = Mock()
        bridge_service.active_designers = {
            "pos1": mock_dialog1,
            "pos2": mock_dialog2
        }
        
        # Close all
        bridge_service.close_all_designers()
        
        # Verify all dialogs were closed
        mock_dialog1.close.assert_called_once()
        mock_dialog2.close.assert_called_once()
        
        # Verify active designers dict is empty
        assert len(bridge_service.active_designers) == 0
    
    def test_is_designer_open(self, bridge_service):
        """Test checking if designer is open for a position."""
        position_id = "test_position_001"
        
        # No designer open
        assert bridge_service.is_designer_open(position_id) is False
        
        # Mock open dialog
        mock_dialog = Mock()
        mock_dialog.isVisible.return_value = True
        bridge_service.active_designers[position_id] = mock_dialog
        
        assert bridge_service.is_designer_open(position_id) is True
        
        # Mock closed dialog
        mock_dialog.isVisible.return_value = False
        assert bridge_service.is_designer_open(position_id) is False
    
    def test_get_open_designers(self, bridge_service):
        """Test getting list of open designers."""
        # Mock dialogs
        mock_dialog1 = Mock()
        mock_dialog1.isVisible.return_value = True
        
        mock_dialog2 = Mock()
        mock_dialog2.isVisible.return_value = False
        
        mock_dialog3 = Mock()
        mock_dialog3.isVisible.return_value = True
        
        bridge_service.active_designers = {
            "pos1": mock_dialog1,  # Visible
            "pos2": mock_dialog2,  # Not visible
            "pos3": mock_dialog3   # Visible
        }
        
        open_designers = bridge_service.get_open_designers()
        
        # Should only return visible designers
        assert len(open_designers) == 2
        assert "pos1" in open_designers
        assert "pos3" in open_designers
        assert "pos2" not in open_designers


class TestDesignerConfiguration:
    """Test designer configuration with measurement data."""
    
    def test_configure_designer_with_measurements(self, bridge_service):
        """Test configuring designer view with measurement data."""
        # Mock designer view
        mock_designer = Mock()
        mock_designer.set_window_dimensions = Mock()
        mock_designer.update_parameters = Mock()
        mock_designer.set_window_type = Mock()
        mock_designer.mullion_offset = 50
        mock_designer.transom_offset = 50
        
        measurement_data = {
            'inner_width': 1200,
            'inner_height': 1000,
            'mullion_offset': 60,
            'transom_offset': 40
        }
        
        # Configure designer
        bridge_service._configure_designer(mock_designer, measurement_data)
        
        # Verify configuration calls
        mock_designer.set_window_dimensions.assert_called_once_with(1200, 1000)
        mock_designer.update_parameters.assert_called_once()
        mock_designer.set_window_type.assert_called_once()
        
        # Verify offsets were set
        assert mock_designer.mullion_offset == 60
        assert mock_designer.transom_offset == 40


if __name__ == "__main__":
    pytest.main([__file__])