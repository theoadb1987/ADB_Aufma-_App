import os
import sys
import tempfile
import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.aufmass_service import AufmassService
from services.data_service import DataService


@pytest.fixture
def aufmass_service(tmp_path):
    db_path = tmp_path / "aufmass_test.db"
    data_service = DataService(str(db_path))
    service = AufmassService(data_service=data_service)
    yield service
    data_service.shutdown()


def test_create_measurement_from_dict(aufmass_service):
    measurement_data = {
        "position_id": "pos1",
        "project_id": 1,
        "inner_width": 1200,
        "inner_height": 1000,
    }

    measurement_id = aufmass_service.create_measurement(measurement_data)
    assert isinstance(measurement_id, int) and measurement_id > 0

    measurement = aufmass_service.data_service.get_measurement("pos1")
    assert measurement is not None
    assert measurement.position_id == "pos1"


def test_update_measurement_from_dict(aufmass_service):
    measurement_data = {
        "position_id": "pos2",
        "project_id": 1,
        "inner_width": 1000,
        "inner_height": 800,
    }
    measurement_id = aufmass_service.create_measurement(measurement_data)

    measurement_data.update({"id": measurement_id, "inner_width": 1100})
    updated_id = aufmass_service.update_measurement(measurement_data)
    assert updated_id == measurement_id

    measurement = aufmass_service.data_service.get_measurement("pos2")
    assert measurement is not None
    assert measurement.inner_width == 1100
