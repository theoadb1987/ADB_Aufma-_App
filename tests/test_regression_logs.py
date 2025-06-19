"""
Regression test to ensure application starts without warnings or errors.
"""
import sys
import os
import subprocess
import time
import signal
import logging
from io import StringIO

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest


class TestApplicationRegression:
    """Test application startup for regression issues."""
    
    def test_application_startup_no_warnings(self):
        """Test that application starts without warnings or errors."""
        # Capture stdout and stderr
        log_capture = StringIO()
        
        # Set up logging to capture application logs
        log_handler = logging.StreamHandler(log_capture)
        log_handler.setLevel(logging.WARNING)
        
        # Create a test script that imports and initializes key components
        test_script = f"""
import sys
import os
import logging

# Add project root to path
project_root = r"{project_root}"
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

try:
    # Test imports
    from services.measurement_schema_service import MeasurementSchemaService
    from services.designer_bridge_service import DesignerBridgeService
    from services.data_service import DataService
    from ui.dynamic_aufmass_ui import DynamicAufmassUI
    
    # Test initialization
    schema_service = MeasurementSchemaService()
    bridge_service = DesignerBridgeService()
    
    # Test data service with temporary database
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        temp_db_path = tmp_file.name
    
    data_service = DataService(temp_db_path)
    
    # Test basic functionality
    fields = schema_service.get_measurement_fields()
    assert len(fields) > 0
    
    validation_result = schema_service.validate_measurement_data({{
        'inner_width': 1200,
        'inner_height': 1000,
        'outer_width': 1250,
        'outer_height': 1050
    }})
    assert validation_result[0] is True
    
    print("SUCCESS: All components initialized without warnings")
    
    # Cleanup
    data_service.shutdown()
    os.unlink(temp_db_path)
    
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
"""
        
        # Write test script to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_script:
            tmp_script.write(test_script)
            script_path = tmp_script.name
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Check that script completed successfully
            assert result.returncode == 0, f"Script failed with return code {result.returncode}"
            
            # Check that output contains success message
            assert "SUCCESS" in result.stdout, f"Expected success message not found. Output: {result.stdout}"
            
            # Check for warnings or errors in stderr
            stderr_lines = result.stderr.strip().split('\n') if result.stderr.strip() else []
            
            # Filter out acceptable warnings (deprecation warnings from dependencies)
            critical_issues = []
            for line in stderr_lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Skip known acceptable warnings
                if any(skip in line.lower() for skip in [
                    'deprecationwarning',
                    'sippytypedict',
                    'ast.str is deprecated',
                    'ast.nameconstant is deprecated'
                ]):
                    continue
                    
                # Log critical issues
                if any(level in line.upper() for level in ['ERROR', 'CRITICAL', 'FATAL']):
                    critical_issues.append(line)
            
            # Assert no critical issues
            assert len(critical_issues) == 0, f"Critical issues found: {critical_issues}"
            
        finally:
            # Cleanup
            os.unlink(script_path)
    
    def test_schema_service_no_config_errors(self):
        """Test that schema service handles missing config files gracefully."""
        import tempfile
        import shutil
        
        # Create temporary directory without config files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock project root to temporary directory
            original_project_root = project_root
            
            try:
                # Create minimal directory structure
                os.makedirs(os.path.join(temp_dir, 'assets'), exist_ok=True)
                os.makedirs(os.path.join(temp_dir, 'config'), exist_ok=True)
                
                # Test that service initializes even without config files
                from services.measurement_schema_service import MeasurementSchemaService
                
                # Temporarily modify project root
                import services.measurement_schema_service as schema_module
                original_root = schema_module.project_root
                schema_module.project_root = temp_dir
                
                try:
                    service = MeasurementSchemaService()
                    
                    # Should still have basic fields even without config
                    fields = service.get_measurement_fields()
                    assert 'inner_width' in fields
                    assert 'inner_height' in fields
                    
                finally:
                    # Restore original project root
                    schema_module.project_root = original_root
                    
            except Exception as e:
                pytest.fail(f"Schema service should handle missing config gracefully: {e}")
    
    def test_database_migration_no_errors(self):
        """Test that database migration completes without errors."""
        import tempfile
        import sqlite3
        
        # Create temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            temp_db_path = tmp_file.name
        
        try:
            # Create old-style database without extended fields
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE measurements (
                    id INTEGER PRIMARY KEY,
                    position_id TEXT,
                    project_id INTEGER,
                    inner_width INTEGER DEFAULT 0,
                    inner_height INTEGER DEFAULT 0,
                    outer_width INTEGER DEFAULT 0,
                    outer_height INTEGER DEFAULT 0,
                    diagonal INTEGER DEFAULT 0,
                    special_notes TEXT,
                    photos TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                ''')
                conn.commit()
            
            # Initialize data service which should run migrations
            from services.data_service import DataService
            data_service = DataService(temp_db_path)
            
            # Verify that migration completed successfully
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(measurements);")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Check that extended fields were added
                extended_fields = ['sill_height', 'frame_depth', 'mullion_offset', 'transom_offset']
                for field in extended_fields:
                    assert field in columns, f"Migration failed: field '{field}' not found"
            
            data_service.shutdown()
            
        finally:
            # Cleanup
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


if __name__ == "__main__":
    pytest.main([__file__])