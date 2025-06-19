"""
Test database schema for regression testing.
"""
import sys
import os
import sqlite3
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
from services.data_service import DataService


class TestDatabaseSchema:
    """Test database schema integrity and migrations."""
    
    def test_product_id_column_exists_in_main_db(self):
        """Test that product_id column exists in the main database."""
        db_path = os.path.join(project_root, "aufmass.db")
        if not os.path.exists(db_path):
            pytest.skip("Main database file does not exist")
            
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(positions);")
            columns = [row[1] for row in cursor.fetchall()]
            assert "product_id" in columns, "product_id column should exist in positions table"
    
    def test_positions_table_required_columns(self):
        """Test that positions table has all required columns."""
        # Create a temporary database to test schema creation
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            temp_db_path = tmp_file.name
        
        try:
            # Initialize data service which creates tables
            data_service = DataService(temp_db_path)
            
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(positions);")
                columns = [row[1] for row in cursor.fetchall()]
                
                required_columns = [
                    'id', 'project_id', 'name', 'floor', 'existing_window_type',
                    'roller_shutter_type', 'notes', 'product', 'product_id', 
                    'product_type', 'product_ids', 'is_main_position', 
                    'parent_id', 'color', 'status', 'accessories', 
                    'has_measurement_data', 'created_at', 'updated_at', 'template_code'
                ]
                
                for column in required_columns:
                    assert column in columns, f"Required column '{column}' should exist in positions table"
                    
            data_service.shutdown()
        finally:
            # Cleanup
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_migration_function_creates_product_id(self):
        """Test that the migration function properly creates product_id column."""
        # Create a temporary database without product_id column
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            temp_db_path = tmp_file.name
        
        try:
            # Create old schema without product_id
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE positions (
                    id TEXT PRIMARY KEY,
                    project_id INTEGER,
                    name TEXT NOT NULL,
                    product_type TEXT DEFAULT '',
                    product_ids TEXT DEFAULT '[]'
                )
                ''')
                conn.commit()
                
                # Verify product_id doesn't exist yet
                cursor.execute("PRAGMA table_info(positions);")
                columns = [row[1] for row in cursor.fetchall()]
                assert "product_id" not in columns
            
            # Initialize data service which should run migrations
            data_service = DataService(temp_db_path)
            
            # Verify product_id was added by migration
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(positions);")
                columns = [row[1] for row in cursor.fetchall()]
                assert "product_id" in columns, "Migration should have added product_id column"
                
            data_service.shutdown()
        finally:
            # Cleanup
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_column_exists_helper_function(self):
        """Test the column existence checking functionality."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            temp_db_path = tmp_file.name
        
        try:
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                
                # Create a test table
                cursor.execute('''
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    existing_column TEXT
                )
                ''')
                
                # Test the column exists function
                def _column_exists(table, column):
                    cursor.execute(f"PRAGMA table_info({table});")
                    return any(row[1] == column for row in cursor.fetchall())
                
                # Test existing column
                assert _column_exists("test_table", "existing_column") is True
                
                # Test non-existing column
                assert _column_exists("test_table", "non_existing_column") is False
                
        finally:
            # Cleanup
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


if __name__ == "__main__":
    pytest.main([__file__])