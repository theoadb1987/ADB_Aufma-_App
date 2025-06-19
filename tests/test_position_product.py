#!/usr/bin/env python3
"""
Test for position-product integration functionality.
"""
import sys
import os
import pytest
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from models.product import ProductType
from models.position import Position
from services.data_service import DataService
from viewmodels.position_viewmodel import PositionViewModel
from ui.position_ui import PositionDetailUI

class TestPositionProductIntegration:
    """Test position-product integration."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        # Create test database
        self.data_service = DataService("test_position_product.db")
        self.position_vm = PositionViewModel(self.data_service)
        
        # Clean up after test
        yield
        try:
            os.remove("test_position_product.db")
        except FileNotFoundError:
            pass
    
    def test_product_type_field_in_position(self):
        """Test that position can store product_type."""
        position = Position(
            id="test_1",
            project_id=1,
            name="Test Position",
            product_type="Rollladen"
        )
        
        # Test serialization
        data = position.to_dict()
        assert data['product_type'] == "Rollladen"
        
        # Test deserialization
        position_from_dict = Position.from_dict(data)
        assert position_from_dict.product_type == "Rollladen"
    
    def test_create_position_with_product_type(self):
        """Test creating position with product type through viewmodel."""
        position_id = self.position_vm.create_position_with_template(
            project_id=1,
            template_code="",
            name="Test Position with Product",
            floor="Erdgeschoss",
            existing_window_type="Holz", 
            roller_shutter_type="Nicht vorhanden",
            notes="Test position with Rollladen",
            selected_products=["Rollladen Standard"],
            product_id=None,
            product_type="Rollladen",
            product_ids=[123]
        )
        
        assert position_id is not None
        
        # Retrieve and verify the position
        position = self.data_service.get_position(position_id)
        assert position is not None
        assert position.product_type == "Rollladen"
        assert position.product_ids == [123]
    
    def test_database_migration_product_type(self):
        """Test that product_type column is properly added to database."""
        # Create a position and save it
        position = Position(
            id="migration_test",
            project_id=1,
            name="Migration Test",
            product_type="Fliegengitter"
        )
        
        saved_id = self.data_service.save_position(position)
        assert saved_id == "migration_test"
        
        # Retrieve and verify
        retrieved = self.data_service.get_position(saved_id)
        assert retrieved.product_type == "Fliegengitter"
    
    @pytest.mark.skipif(not bool(os.environ.get('DISPLAY', '')), 
                       reason="No display available for UI test")
    def test_ui_product_type_selection(self):
        """Test UI product type selection and signal emission."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create UI component
        position_ui = PositionDetailUI()
        
        # Test setting product type
        product_type = ProductType.ROLLER_SHUTTER
        position_ui.set_product_type(product_type)
        
        # Verify product type is set
        assert position_ui.selected_product_type == product_type
        assert product_type.display_name in position_ui.product_edit.text()
        
        # Test getting data includes product type
        data = position_ui.get_data()
        assert data['product_type'] == product_type
    
    def test_product_type_enum_values(self):
        """Test all ProductType enum values work correctly."""
        test_cases = [
            (ProductType.WINDOW, "Fenster"),
            (ProductType.ROLLER_SHUTTER, "Rollladen"), 
            (ProductType.FLY_SCREEN, "Fliegengitter"),
            (ProductType.PLEATED_BLIND, "Plissee"),
            (ProductType.AWNING, "Markise")
        ]
        
        for product_type, expected_name in test_cases:
            position = Position(
                id=f"test_{product_type.code}",
                project_id=1,
                name=f"Test {expected_name}",
                product_type=expected_name
            )
            
            # Save and retrieve
            self.data_service.save_position(position)
            retrieved = self.data_service.get_position(position.id)
            
            assert retrieved.product_type == expected_name
            assert product_type.icon_exists()  # Verify icon exists

if __name__ == "__main__":
    pytest.main([__file__, "-v"])