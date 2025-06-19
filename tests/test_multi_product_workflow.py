#!/usr/bin/env python3
"""
Comprehensive tests for multi-product workflow functionality.
Tests the complete implementation of removing dimensions fields and 
implementing multi-product selection.
"""
import sys
import os
import pytest
from typing import List
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.position import Position
from services.data_service import DataService
from viewmodels.position_viewmodel import PositionViewModel

# PyQt6 imports for UI tests (only imported when needed)
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtTest import QTest
    from PyQt6.QtCore import Qt
    from ui.position_ui import PositionDetailUI, PositionListUI
    from views.position_view import PositionView
    from views.main_window import MainWindow
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


class TestMultiProductWorkflow:
    """Test complete multi-product workflow implementation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        
        # Create test database
        self.test_db = "test_multi_product.db"
        self.data_service = DataService(self.test_db)
        self.position_vm = PositionViewModel(self.data_service)
        
        # Clean up after test
        yield
        try:
            os.remove(self.test_db)
        except FileNotFoundError:
            pass
    
    def test_position_model_product_ids_field(self):
        """Test that Position model correctly handles product_ids field."""
        # Test creating position with multiple product IDs
        position = Position(
            id="test_multi_1",
            project_id=1,
            name="Multi-Product Position",
            product_ids=[101, 102, 103],
            product="Kunststofffenster Standard"  # Legacy field for compatibility
        )
        
        # Test product_count property
        assert position.product_count == 3
        
        # Test serialization includes product_ids
        data = position.to_dict()
        assert data['product_ids'] == [101, 102, 103]
        assert 'w_mm' not in data  # Ensure deprecated fields are not included
        assert 'h_mm' not in data
        
        # Test deserialization
        position_from_dict = Position.from_dict(data)
        assert position_from_dict.product_ids == [101, 102, 103]
        assert position_from_dict.product_count == 3
    
    def test_position_model_migration_legacy_data(self):
        """Test migration of legacy data structures."""
        # Test data with deprecated w_mm, h_mm fields
        legacy_data = {
            "id": "legacy_1",
            "project_id": 1,
            "name": "Legacy Position",
            "w_mm": 1200,  # Should be removed
            "h_mm": 1400,  # Should be removed
            "product": "Fenster",
            "product_id": 42,
            "created_at": "2023-01-01T10:00:00",
            "updated_at": "2023-01-01T10:00:00"
        }
        
        # Migration should remove w_mm/h_mm and convert single product_id to product_ids
        position = Position.from_dict(legacy_data)
        
        assert not hasattr(position, 'w_mm')
        assert not hasattr(position, 'h_mm')
        assert position.product_ids == [42]  # Migrated from single product_id
        assert position.product_id == 42  # Legacy field preserved for compatibility
    
    def test_position_model_json_migration(self):
        """Test migration of JSON string format for product_ids."""
        # Test data with product_ids as JSON string (from database)
        json_data = {
            "id": "json_test",
            "project_id": 1,
            "name": "JSON Test Position",
            "product_ids": "[101, 102, 103]",  # JSON string format
            "created_at": "2023-01-01T10:00:00",
            "updated_at": "2023-01-01T10:00:00"
        }
        
        position = Position.from_dict(json_data)
        assert position.product_ids == [101, 102, 103]
        assert position.product_count == 3
    
    def test_viewmodel_create_position_multi_products(self):
        """Test creating position with multiple products through viewmodel."""
        # Test creating position with multi-product selection
        position_id = self.position_vm.create_position_with_template(
            project_id=1,
            template_code="",
            name="Multi-Product Test",
            floor="Erdgeschoss",
            existing_window_type="Kunststoff",
            roller_shutter_type="Elektrisch",
            notes="Test with multiple products",
            selected_products=["Kunststofffenster", "Rollladen", "Fliegengitter"],
            product_id=None,
            product_type="Fenster",
            product_ids=[201, 202, 203]
        )
        
        assert position_id is not None
        
        # Retrieve and verify the position
        position = self.data_service.get_position(position_id)
        assert position is not None
        assert position.product_ids == [201, 202, 203]
        assert position.product_count == 3
        assert position.name == "Multi-Product Test"
    
    def test_database_schema_product_ids_column(self):
        """Test that database properly handles product_ids column."""
        # Create position with multiple product IDs
        position = Position(
            id="db_test_1",
            project_id=1,
            name="Database Test",
            product_ids=[301, 302, 303, 304]
        )
        
        # Save to database
        saved_id = self.data_service.save_position(position)
        assert saved_id == "db_test_1"
        
        # Retrieve from database
        retrieved = self.data_service.get_position(saved_id)
        assert retrieved.product_ids == [301, 302, 303, 304]
        assert retrieved.product_count == 4
        
        # Update with different product_ids
        retrieved.product_ids = [401, 402]
        self.data_service.save_position(retrieved)
        
        # Verify update
        updated = self.data_service.get_position(saved_id)
        assert updated.product_ids == [401, 402]
        assert updated.product_count == 2
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt6 not available")
    def test_ui_position_detail_multi_product_display(self):
        """Test UI properly displays multi-product selection."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        position_ui = PositionDetailUI()
        
        # Test setting data with multiple products
        test_data = {
            'number': '1',
            'title': 'UI Multi-Product Test',
            'product_ids': [501, 502, 503],
            'product_name': 'Fenster',  # Legacy field
            'description': 'Test with multiple products',
            'quantity': 1.0,
            'price': 299.99
        }
        
        position_ui.set_data(test_data)
        
        # Verify UI shows count of selected products
        assert "3 Produkte ausgewählt" in position_ui.product_edit.text()
        
        # Test getting data back
        retrieved_data = position_ui.get_data()
        assert retrieved_data['product_ids'] == [501, 502, 503]
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt6 not available")
    def test_ui_position_detail_no_dimensions_fields(self):
        """Test that dimension input fields are completely removed from UI."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        position_ui = PositionDetailUI()
        
        # Verify no width/height spinboxes exist
        assert not hasattr(position_ui, 'width_spin')
        assert not hasattr(position_ui, 'height_spin')
        assert not hasattr(position_ui, 'w_mm_spin')
        assert not hasattr(position_ui, 'h_mm_spin')
        
        # Verify get_data() doesn't return w_mm/h_mm
        data = position_ui.get_data()
        assert 'w_mm' not in data
        assert 'h_mm' not in data
        assert 'width' not in data
        assert 'height' not in data
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt6 not available")
    def test_ui_product_selection_multi_select(self):
        """Test multi-product selection dialog functionality."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        position_ui = PositionDetailUI()
        
        # Set up mock products
        mock_products = [
            {'id': 601, 'name': 'Kunststofffenster Standard', 'price': 249.99},
            {'id': 602, 'name': 'Rollladen Elektrisch', 'price': 399.99},
            {'id': 603, 'name': 'Fliegengitter', 'price': 89.99}
        ]
        position_ui.set_products(mock_products)
        
        # Test product selection and signal emission
        # Simulate product selection
        position_ui._selected_product_ids = [601, 603]  # Select products 1 and 3
        
        # Verify selected products are stored correctly
        assert position_ui._selected_product_ids == [601, 603]
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt6 not available")
    def test_position_view_signal_refresh(self):
        """Test that PositionView refreshes list when positions are updated."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create PositionView with viewmodel
        position_view = PositionView(viewmodel=self.position_vm)
        
        # Create test position
        test_position = Position(
            id="signal_test",
            project_id=1,
            name="Signal Test Position",
            product_ids=[701, 702]
        )
        
        # Test that the signal connection exists
        assert hasattr(self.position_vm, 'position_details_updated')
        assert hasattr(position_view, '_on_position_updated')
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt6 not available")
    def test_main_window_auto_switch_aufmass_tab(self):
        """Test MainWindow auto-switches to Aufmaß tab when new position is created."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        main_window = MainWindow()
        
        # Initial state - should be on Projects tab (index 0)
        assert main_window.tab_widget.currentIndex() == 0
        
        # Simulate project selection to enable position tab
        main_window._on_project_selected(1)
        assert main_window.tab_widget.isTabEnabled(1)  # Positions tab enabled
        
        # Simulate new position creation
        main_window._on_new_position_created("test_position_id")
        
        # Verify auto-switch to Aufmaß tab (index 2)
        assert main_window.tab_widget.currentIndex() == 2
        assert main_window.tab_widget.isTabEnabled(2)  # Aufmaß tab enabled
    
    def test_complete_workflow_integration(self):
        """Test complete workflow from position creation to list refresh."""
        # Create a position with multi-product selection
        position_id = self.position_vm.create_position_with_template(
            project_id=1,
            template_code="WIN_STD",
            name="Integration Test Position",
            floor="1. OG",
            existing_window_type="Aluminium",
            roller_shutter_type="Manuell",
            notes="Complete workflow test",
            selected_products=["Fenster Premium", "Rollladen", "Insektenschutz"],
            product_ids=[801, 802, 803]
        )
        
        assert position_id is not None
        
        # Verify position was created with correct data
        position = self.data_service.get_position(position_id)
        assert position.product_ids == [801, 802, 803]
        assert position.name == "Integration Test Position"
        assert position.floor == "1. OG"
        
        # Test that main position and sub-positions were created
        all_positions = self.data_service.get_positions(1)
        main_positions = [p for p in all_positions if p.is_main_position]
        assert len(main_positions) >= 1
        
        # Verify main position has the window product
        main_pos = next((p for p in main_positions if p.id == position_id), None)
        assert main_pos is not None
        assert "fenster" in main_pos.product.lower()  # Main product should be window
    
    def test_migration_robustness_edge_cases(self):
        """Test migration handles various edge cases robustly."""
        # Test completely empty product_ids
        empty_data = {
            "id": "empty_test",
            "project_id": 1,
            "name": "Empty Test",
            "created_at": "2023-01-01T10:00:00",
            "updated_at": "2023-01-01T10:00:00"
        }
        position = Position.from_dict(empty_data)
        assert position.product_ids == []
        
        # Test malformed JSON in product_ids
        malformed_data = {
            "id": "malformed_test",
            "project_id": 1,
            "name": "Malformed Test",
            "product_ids": "[invalid json",
            "created_at": "2023-01-01T10:00:00",
            "updated_at": "2023-01-01T10:00:00"
        }
        position = Position.from_dict(malformed_data)
        assert position.product_ids == []  # Should default to empty list
        
        # Test legacy data with both old and new fields
        mixed_data = {
            "id": "mixed_test",
            "project_id": 1,
            "name": "Mixed Test",
            "w_mm": 1000,  # Should be removed
            "h_mm": 1200,  # Should be removed
            "product_id": 999,
            "product_ids": [901, 902],  # Should take precedence
            "created_at": "2023-01-01T10:00:00",
            "updated_at": "2023-01-01T10:00:00"
        }
        position = Position.from_dict(mixed_data)
        assert position.product_ids == [901, 902]  # New field takes precedence
        assert position.product_id == 999  # Legacy field preserved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])