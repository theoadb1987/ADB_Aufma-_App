"""
Test dynamic measurement schema service and field extraction.
"""
import sys
import os
import tempfile
import sqlite3

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
from services.measurement_schema_service import MeasurementSchemaService, MeasurementField
from services.data_service import DataService


class TestMeasurementSchemaService:
    """Test measurement schema service functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.schema_service = MeasurementSchemaService()
    
    def test_schema_service_initialization(self):
        """Test that schema service initializes correctly."""
        assert self.schema_service is not None
        assert isinstance(self.schema_service.measurement_fields, dict)
        assert len(self.schema_service.measurement_fields) > 0
    
    def test_core_measurement_fields_exist(self):
        """Test that core measurement fields are extracted."""
        required_core_fields = [
            'inner_width', 'inner_height', 'outer_width', 'outer_height', 'diagonal'
        ]
        
        for field_key in required_core_fields:
            assert field_key in self.schema_service.measurement_fields
            field = self.schema_service.measurement_fields[field_key]
            assert isinstance(field, MeasurementField)
            assert field.key == field_key
    
    def test_extended_measurement_fields_exist(self):
        """Test that extended measurement fields for ElementDesigner are extracted."""
        extended_fields = [
            'sill_height', 'frame_depth', 'mullion_offset', 'transom_offset',
            'glazing_thickness', 'reveal_left', 'reveal_right', 'reveal_top', 'reveal_bottom'
        ]
        
        for field_key in extended_fields:
            assert field_key in self.schema_service.measurement_fields
            field = self.schema_service.measurement_fields[field_key]
            assert isinstance(field, MeasurementField)
            assert field.key == field_key
    
    def test_field_categories(self):
        """Test that field categories are properly defined."""
        categories = self.schema_service.get_field_categories()
        assert 'basic' in categories
        assert 'advanced' in categories
        
        basic_fields = self.schema_service.get_measurement_fields('basic')
        assert 'inner_width' in basic_fields
        assert 'inner_height' in basic_fields
        
        advanced_fields = self.schema_service.get_measurement_fields('advanced')
        assert 'mullion_offset' in advanced_fields
        assert 'transom_offset' in advanced_fields
    
    def test_required_fields(self):
        """Test required field identification."""
        required_fields = self.schema_service.get_required_fields()
        
        # Core dimensions should be required
        assert 'inner_width' in required_fields
        assert 'inner_height' in required_fields
        assert 'outer_width' in required_fields
        assert 'outer_height' in required_fields
        
        # Extended fields should not be required
        assert 'sill_height' not in required_fields
        assert 'mullion_offset' not in required_fields
    
    def test_measurement_validation(self):
        """Test measurement data validation."""
        # Valid data
        valid_data = {
            'inner_width': 1200,
            'inner_height': 1000,
            'outer_width': 1250,
            'outer_height': 1050
        }
        
        is_valid, errors = self.schema_service.validate_measurement_data(valid_data)
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid data - missing required fields
        invalid_data = {
            'inner_width': 1200
            # Missing other required fields
        }
        
        is_valid, errors = self.schema_service.validate_measurement_data(invalid_data)
        assert is_valid is False
        assert len(errors) > 0
        
        # Invalid data - out of range
        out_of_range_data = {
            'inner_width': 10000,  # Too large
            'inner_height': 1000,
            'outer_width': 1250,
            'outer_height': 1050
        }
        
        is_valid, errors = self.schema_service.validate_measurement_data(out_of_range_data)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_calculated_values(self):
        """Test calculation of derived values."""
        data = {
            'inner_width': 1200,
            'inner_height': 1000
        }
        
        calculated = self.schema_service.calculate_derived_values(data)
        
        # Check diagonal calculation
        assert 'diagonal' in calculated
        diagonal = calculated['diagonal']
        expected_diagonal = (1200**2 + 1000**2)**0.5
        assert abs(diagonal - expected_diagonal) < 1.0
        
        # Check area calculation
        assert 'area' in calculated
        area = calculated['area']
        expected_area = (1200 * 1000) / 1000000  # mm² to m²
        assert abs(area - expected_area) < 0.01
        
        # Check perimeter calculation
        assert 'perimeter' in calculated
        perimeter = calculated['perimeter']
        expected_perimeter = 2 * (1200 + 1000) / 1000  # mm to m
        assert abs(perimeter - expected_perimeter) < 0.01
    
    def test_database_columns(self):
        """Test database column generation."""
        columns = self.schema_service.get_database_columns()
        
        # Check base columns
        assert 'id' in columns
        assert 'position_id' in columns
        assert 'project_id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
        
        # Check measurement columns
        assert 'inner_width' in columns
        assert 'inner_height' in columns
        assert 'mullion_offset' in columns
        assert 'transom_offset' in columns
        
        # Check calculated columns
        assert 'area' in columns
        assert 'perimeter' in columns


class TestDatabaseMigration:
    """Test database migration for measurement fields."""
    
    def test_measurement_table_migration(self):
        """Test that measurement table is properly migrated with new fields."""
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            temp_db_path = tmp_file.name
        
        try:
            # Initialize data service which should run migrations
            data_service = DataService(temp_db_path)
            
            # Check that all extended measurement fields exist
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(measurements);")
                columns = [row[1] for row in cursor.fetchall()]
                
                expected_new_fields = [
                    'sill_height', 'frame_depth', 'mullion_offset', 'transom_offset',
                    'glazing_thickness', 'reveal_left', 'reveal_right', 'reveal_top',
                    'reveal_bottom', 'area', 'perimeter'
                ]
                
                for field in expected_new_fields:
                    assert field in columns, f"Field '{field}' should exist in measurements table"
                    
            data_service.shutdown()
            
        finally:
            # Cleanup
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_foreign_key_constraint(self):
        """Test that foreign key constraints are properly set up."""
        # This would test FK constraints if implemented
        # For now, just ensure the position_id column exists
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            temp_db_path = tmp_file.name
        
        try:
            data_service = DataService(temp_db_path)
            
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(measurements);")
                columns = [row[1] for row in cursor.fetchall()]
                
                assert 'position_id' in columns
                
            data_service.shutdown()
            
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


if __name__ == "__main__":
    pytest.main([__file__])