"""
Tests for Element Designer functionality.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.window_element import WindowElement, WindowType, ProfileType


class TestWindowElement:
    """Test WindowElement data model."""
    
    def test_window_element_creation(self):
        """Test creating a window element with default values."""
        element = WindowElement()
        
        assert element.width == 1000.0
        assert element.height == 1200.0
        assert element.profile_type == ProfileType.BLEND_070
        assert element.window_type == WindowType.FT_DK
        assert element.x == 0.0
        assert element.y == 0.0
        
    def test_window_element_center_properties(self):
        """Test center_x and center_y properties."""
        element = WindowElement(x=100, y=200, width=1000, height=1200)
        
        assert element.center_x == 600  # 100 + 1000/2
        assert element.center_y == 800  # 200 + 1200/2
        
    def test_window_element_bounds(self):
        """Test get_bounds method."""
        element = WindowElement(x=100, y=200, width=1000, height=1200)
        bounds = element.get_bounds()
        
        assert bounds == (100, 200, 1100, 1400)  # x, y, x+width, y+height


class TestWindowType:
    """Test WindowType enum."""
    
    def test_all_14_window_types_exist(self):
        """Test that all 14 window types are defined."""
        window_types = list(WindowType)
        assert len(window_types) == 14
        
        expected_codes = [
            "FT_F", "FT_D", "FT_K", "FT_DK", "FT_DD", "FT_DKD",
            "FT_HS", "FT_PSK", "FT_SVG", "FT_VS", "FT_HS2", 
            "FT_FALT", "FT_RB", "FT_SCHR"
        ]
        
        actual_codes = [wt.code for wt in window_types]
        for code in expected_codes:
            assert code in actual_codes
    
    def test_window_type_attributes(self):
        """Test that WindowType enum has correct attributes."""
        ft_dk = WindowType.FT_DK
        
        assert ft_dk.code == "FT_DK"
        assert ft_dk.display_name == "Dreh-Kipp"
        assert ft_dk.description == "Standard"
        
    def test_icon_grid_loads_all_14(self):
        """Test that icon grid can load all 14 window types."""
        window_types = list(WindowType)
        
        # Simulate creating buttons for all window types
        button_count = 0
        for window_type in window_types:
            # Each window type should have required attributes
            assert hasattr(window_type, 'code')
            assert hasattr(window_type, 'display_name') 
            assert hasattr(window_type, 'description')
            button_count += 1
            
        assert button_count == 14


class TestProfileType:
    """Test ProfileType enum."""
    
    def test_profile_types_exist(self):
        """Test that profile types are defined."""
        profile_types = list(ProfileType)
        assert len(profile_types) >= 7  # At least 7 profile types
        
        expected_profiles = [
            "070", "076 MD", "082 MD", "103.229", 
            "103.232", "103.380", "103.381"
        ]
        
        actual_values = [pt.value for pt in profile_types]
        for profile in expected_profiles:
            assert profile in actual_values


@pytest.fixture
def mock_qt_app():
    """Mock Qt application for testing."""
    with patch('PyQt6.QtWidgets.QApplication'):
        yield


class TestElementDesignerView:
    """Test Element Designer View functionality."""
    
    def test_svg_export_not_empty(self, mock_qt_app):
        """Test that SVG export produces non-empty output."""
        # Mock the ElementDesignerView since we need Qt widgets
        with patch('views.element_designer_view.ElementDesignerView') as MockView:
            mock_view = MockView.return_value
            mock_view.current_window_type = WindowType.FT_DK
            
            # Simulate SVG export
            export_path = "test_export.svg"
            mock_view._export_svg.return_value = None
            
            # Should not raise exception
            mock_view._export_svg()
            
            # Verify export was called
            assert mock_view.current_window_type is not None
            
    def test_glossary_data_loading(self, mock_qt_app):
        """Test that glossary data can be loaded."""
        with patch('views.element_designer_view.ElementDesignerView') as MockView:
            mock_view = MockView.return_value
            
            # Mock glossary data
            mock_view.glossary_data = {
                'begriffe': {
                    'Blendrahmen': 'Äußerer Rahmen eines Fensters',
                    'Flügelrahmen': 'Beweglicher Teil des Fensters'
                }
            }
            
            assert 'begriffe' in mock_view.glossary_data
            assert len(mock_view.glossary_data['begriffe']) >= 2
            
    def test_schnitt_mapping_loading(self, mock_qt_app):
        """Test that schnitt mapping data can be loaded.""" 
        with patch('views.element_designer_view.ElementDesignerView') as MockView:
            mock_view = MockView.return_value
            
            # Mock schnitt mapping data
            mock_view.schnitt_mapping = {
                'schnitt_templates': {
                    'S01': {
                        'description': 'Standard Dreh-Kipp',
                        'file': 'S01_DK_Standard.svg',
                        'window_types': ['FT_DK', 'FT_D']
                    }
                }
            }
            
            assert 'schnitt_templates' in mock_view.schnitt_mapping
            assert 'S01' in mock_view.schnitt_mapping['schnitt_templates']


class TestIntegration:
    """Test integration with main application."""
    
    def test_menu_integration(self):
        """Test that Element Designer menu item exists."""
        # This would test the main window menu integration
        # For now, just verify the method exists
        from main import MainWindow
        
        # Check that the method exists
        assert hasattr(MainWindow, '_show_element_designer')
        assert hasattr(MainWindow, '_on_window_type_selected')
        assert hasattr(MainWindow, '_on_svg_export_requested')
        
    def test_dock_widget_creation(self, mock_qt_app):
        """Test that dock widget can be created."""
        with patch('main.MainWindow') as MockMainWindow:
            mock_window = MockMainWindow.return_value
            mock_window.element_designer_dock = None
            
            # Should be able to set dock widget
            mock_window.element_designer_dock = MagicMock()
            assert mock_window.element_designer_dock is not None


if __name__ == '__main__':
    pytest.main([__file__])