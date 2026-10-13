import pytest
from src.models.workout import Exercise


def test_exercise_valid():
    e = Exercise("Squat", 3, 10, 60)
    assert e.number_of_sets == 3


def test_exercise_zero_sets():
    with pytest.raises(ValueError):
        Exercise("Squat", 0, 10, 60)


def test_exercise_zero_reps():
    with pytest.raises(ValueError):
        Exercise("Squat", 3, 0, 60)


def test_exercise_empty_name():
    with pytest.raises(ValueError):
        Exercise("", 3, 10, 60)


def test_to_line_and_from_parts():
    e = Exercise("Push-up", 3, 12, 45, "آرام")
    line = e.to_text()
    parts = line.split(" | ")
    e2 = Exercise.exercise_information(parts)
    assert e2.name == "Push-up"
    assert e2.sets == 3