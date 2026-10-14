from datetime import time
from types import SimpleNamespace

import pytest

import src.admin.hall_manager as hall_module
import src.admin.class_manager as class_module
from src.admin.hall_manager import HallManager
from src.admin.class_manager import ClassManager
from src.models.hall import Hall
from src.models.gym_class import GymClass


@pytest.fixture
def env(tmp_path, monkeypatch):
    # All writes use test-only files, never real project data.
    monkeypatch.setattr(hall_module, "HALLS_FILE", tmp_path / "halls.txt")
    monkeypatch.setattr(class_module, "CLASSES_FILE", tmp_path / "classes.txt")

    coach = SimpleNamespace(username="coach1", role="coach", is_active=True)
    monkeypatch.setattr(
        class_module,
        "find_username",
        lambda username: coach if username == "coach1" else None,
    )

    halls = HallManager()
    halls.add_hall(1, Hall("Yoga Hall", 20, ["Mat"], True))
    classes = ClassManager(halls)
    return halls, classes, coach, tmp_path


def new_class(**changes):
    data = dict(
        title="Yoga", sport="Yoga", coach="coach1",
        time=time(18, 30), day="Saturday",
        hall=1, capacity=15, status=True,
    )
    data.update(changes)
    return GymClass(**data)


def test_hall_survives_restart(env):
    halls, _, _, _ = env
    restored = HallManager().view_halls()[1]
    assert restored.name == "Yoga Hall"
    assert restored.capacity == 20
    assert restored.equipment == ["Mat"]
    assert restored.status is True


def test_hall_edit_survives_restart(env):
    halls, _, _, _ = env
    halls.edit_hall(1, Hall("New Hall", 25, ["Ball"], True))
    restored = HallManager().view_halls()[1]
    assert (restored.name, restored.capacity, restored.equipment) == (
        "New Hall", 25, ["Ball"]
    )


def test_hall_status_survives_restart(env):
    halls, _, _, _ = env
    halls.deactivate_hall(1)
    assert HallManager().view_halls()[1].status is False
    halls.activate_hall(1)
    assert HallManager().view_halls()[1].status is True


def test_hall_duplicate_id_rejected(env):
    halls, _, _, _ = env
    with pytest.raises(ValueError):
        halls.add_hall(1, Hall("Other", 10, [], True))


@pytest.mark.parametrize("bad_id", [0, -1, "2", True])
def test_hall_invalid_id_rejected(env, bad_id):
    halls, _, _, _ = env
    with pytest.raises(ValueError):
        halls.add_hall(bad_id, Hall("Other", 10, [], True))


def test_hall_bad_file_rejected(env):
    _, _, _, root = env
    (root / "halls.txt").write_text("invalid hall record\n", encoding="utf-8")
    with pytest.raises(ValueError):
        HallManager()


def test_class_survives_restart(env):
    halls, classes, _, root = env
    classes.add_class(1, new_class())
    restored = ClassManager(halls).view_classes()[1]
    assert restored.title == "Yoga"
    assert restored.coach == "coach1"
    assert restored.time == time(18, 30)
    assert restored.hall == 1
    assert restored.capacity == 15
    assert restored.status is True
    assert (root / "classes.txt").exists()


def test_class_edit_survives_restart(env):
    halls, classes, _, _ = env
    classes.add_class(1, new_class())
    classes.edit_class(1, new_class(title="Pilates", capacity=12))
    restored = ClassManager(halls).view_classes()[1]
    assert restored.title == "Pilates"
    assert restored.capacity == 12


def test_class_status_survives_restart(env):
    halls, classes, _, _ = env
    classes.add_class(1, new_class())
    classes.deactivate_class(1)
    assert ClassManager(halls).view_classes()[1].status is False
    classes.activate_class(1)
    assert ClassManager(halls).view_classes()[1].status is True


def test_class_duplicate_id_rejected(env):
    _, classes, _, _ = env
    classes.add_class(1, new_class())
    with pytest.raises(ValueError):
        classes.add_class(1, new_class())


def test_class_missing_coach_rejected(env):
    _, classes, _, _ = env
    with pytest.raises(ValueError):
        classes.add_class(2, new_class(coach="not_exist"))


def test_class_inactive_coach_rejected(env):
    _, classes, coach, _ = env
    coach.is_active = False
    with pytest.raises(ValueError):
        classes.add_class(2, new_class())


def test_class_too_large_rejected(env):
    _, classes, _, _ = env
    with pytest.raises(ValueError):
        classes.add_class(2, new_class(capacity=21))


def test_class_inactive_hall_rejected(env):
    halls, classes, _, _ = env
    halls.deactivate_hall(1)
    with pytest.raises(ValueError):
        classes.add_class(2, new_class())


def test_class_reactivation_checks_coach(env):
    _, classes, coach, _ = env
    classes.add_class(1, new_class())
    classes.deactivate_class(1)
    coach.is_active = False
    with pytest.raises(ValueError):
        classes.activate_class(1)
    assert classes.view_classes()[1].status is False


def test_class_bad_file_rejected(env):
    halls, _, _, root = env
    (root / "classes.txt").write_text("invalid class record\n", encoding="utf-8")
    with pytest.raises(ValueError):
        ClassManager(halls)
