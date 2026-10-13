import pytest
from src.models.hall import Hall

def test_create_hall():
    hall1 = Hall("Yoga", 20, ["Mat"], True)
    assert hall1.capacity == 20

def test_invalid_capacity():
    with pytest.raises(ValueError):
        Hall("Yoga", -5, ["Mat"], True)


def test_invalid_name():
    with pytest.raises(ValueError):
        Hall("", 20, ["Mat"], True)

def test_invalid_equipment():
    with pytest.raises(ValueError):
        Hall("Yoga", 20, "Mat", True)