"""
Test PyQt6 alignment flags for regression testing.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
from PyQt6.QtCore import Qt


def test_alignment_flags_exist():
    """Test that PyQt6 AlignmentFlag enum has the required alignment flags."""
    assert hasattr(Qt.AlignmentFlag, "AlignRight"), "Qt.AlignmentFlag.AlignRight should exist"
    assert hasattr(Qt.AlignmentFlag, "AlignVCenter"), "Qt.AlignmentFlag.AlignVCenter should exist"
    assert hasattr(Qt.AlignmentFlag, "AlignLeft"), "Qt.AlignmentFlag.AlignLeft should exist"
    assert hasattr(Qt.AlignmentFlag, "AlignCenter"), "Qt.AlignmentFlag.AlignCenter should exist"


def test_alignment_flags_are_valid():
    """Test that alignment flags have valid values and can be combined."""
    # Test individual flags
    assert Qt.AlignmentFlag.AlignRight.value > 0
    assert Qt.AlignmentFlag.AlignVCenter.value > 0
    
    # Test combination (this is what was failing before)
    combined = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    assert combined is not None
    
    # Test that the old Qt.AlignRight doesn't exist (this was the bug)
    assert not hasattr(Qt, "AlignRight"), "Qt.AlignRight should not exist in PyQt6"


def test_deprecated_alignment_not_available():
    """Test that deprecated Qt.Align* attributes don't exist in PyQt6."""
    deprecated_attrs = [
        "AlignRight", "AlignLeft", "AlignCenter", "AlignVCenter", 
        "AlignTop", "AlignBottom", "AlignHCenter"
    ]
    
    for attr in deprecated_attrs:
        assert not hasattr(Qt, attr), f"Qt.{attr} should not exist in PyQt6"


if __name__ == "__main__":
    pytest.main([__file__])