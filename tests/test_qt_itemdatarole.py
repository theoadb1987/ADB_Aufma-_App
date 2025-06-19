"""
Test PyQt6 ItemDataRole flags for regression testing.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
from PyQt6.QtCore import Qt


def test_itemdatarole_flags_exist():
    """Test that PyQt6 ItemDataRole enum has the required role flags."""
    assert hasattr(Qt.ItemDataRole, "UserRole"), "Qt.ItemDataRole.UserRole should exist"
    assert hasattr(Qt.ItemDataRole, "DisplayRole"), "Qt.ItemDataRole.DisplayRole should exist"
    assert hasattr(Qt.ItemDataRole, "EditRole"), "Qt.ItemDataRole.EditRole should exist"
    assert hasattr(Qt.ItemDataRole, "CheckStateRole"), "Qt.ItemDataRole.CheckStateRole should exist"


def test_itemdatarole_flags_are_valid():
    """Test that ItemDataRole flags have valid values."""
    # Test individual flags
    assert Qt.ItemDataRole.UserRole.value > 0
    assert Qt.ItemDataRole.DisplayRole.value >= 0
    assert Qt.ItemDataRole.EditRole.value > 0
    assert Qt.ItemDataRole.CheckStateRole.value > 0


def test_deprecated_itemroles_not_available():
    """Test that deprecated Qt.Role attributes don't exist in PyQt6."""
    deprecated_attrs = [
        "UserRole", "DisplayRole", "EditRole", "CheckStateRole",
        "ToolTipRole", "StatusTipRole", "WhatsThisRole"
    ]
    
    for attr in deprecated_attrs:
        assert not hasattr(Qt, attr), f"Qt.{attr} should not exist in PyQt6, use Qt.ItemDataRole.{attr}"


def test_itemdatarole_usage_example():
    """Test that ItemDataRole can be used properly in PyQt6."""
    from PyQt6.QtWidgets import QApplication, QTableWidgetItem
    
    # Ensure QApplication exists for widget creation
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create a table item and test setting/getting data with ItemDataRole
    item = QTableWidgetItem("Test")
    
    # Test setting custom data with UserRole
    test_data = {"id": 123, "name": "test"}
    item.setData(Qt.ItemDataRole.UserRole, test_data)
    
    # Test retrieving the data
    retrieved_data = item.data(Qt.ItemDataRole.UserRole)
    assert retrieved_data == test_data, "ItemDataRole.UserRole should store and retrieve data correctly"
    
    # Test default display text
    display_text = item.data(Qt.ItemDataRole.DisplayRole)
    assert display_text == "Test", "ItemDataRole.DisplayRole should return the display text"


if __name__ == "__main__":
    pytest.main([__file__])