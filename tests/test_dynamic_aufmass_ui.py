import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from PyQt6.QtWidgets import QApplication

from ui.dynamic_aufmass_ui import DynamicAufmassUI

@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_designer_requested_emits_string(qapp):
    ui = DynamicAufmassUI()
    ui.current_position_id = 123  # intentionally int
    ui.measurement_data = {
        'inner_width': 1200,
        'inner_height': 1000,
        'outer_width': 1250,
        'outer_height': 1050
    }

    captured = {}
    def handler(pos_id, data):
        captured['pos_id'] = pos_id
        captured['data'] = data

    ui.designer_requested.connect(handler)
    ui._open_designer()

    assert captured['pos_id'] == '123'
    assert isinstance(captured['pos_id'], str)

