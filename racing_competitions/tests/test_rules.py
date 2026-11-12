import pytest
from fastapi import HTTPException
from app.rules import ensure_unique_driver, ensure_unique_position, ensure_valid_points, ensure_team_has_no_drivers

def test_driver_allowed():
    assert ensure_unique_driver(False) is None

def test_duplicate_driver_rejected():
    with pytest.raises(HTTPException) as exc:
        ensure_unique_driver(True)
    assert exc.value.status_code == 409

def test_position_allowed():
    assert ensure_unique_position(False) is None

def test_duplicate_position_rejected():
    with pytest.raises(HTTPException) as exc:
        ensure_unique_position(True)
    assert exc.value.status_code == 409

def test_points_allowed():
    assert ensure_valid_points(25) is None

def test_negative_points_rejected():
    with pytest.raises(HTTPException) as exc:
        ensure_valid_points(-1)
    assert exc.value.status_code == 422

def test_team_with_drivers_cannot_be_deleted():
    with pytest.raises(HTTPException) as exc:
        ensure_team_has_no_drivers(2)
    assert exc.value.status_code == 409
