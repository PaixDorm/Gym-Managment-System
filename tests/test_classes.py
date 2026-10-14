from datetime import time
from types import SimpleNamespace

import src.admin.class_manager as class_module
from src.admin.class_manager import ClassManager
from src.admin.hall_manager import HallManager
from src.models.hall import Hall
from src.models.gym_class import GymClass


def test_class_persistence(tmp_path, monkeypatch):

    monkeypatch.setattr(
        class_module,
        "CLASSES_FILE",
        tmp_path / "classes.txt"
    )

    import src.admin.hall_manager as hall_module

    monkeypatch.setattr(
        hall_module,
        "HALLS_FILE",
        tmp_path / "halls.txt"
    )

    fake_coach = SimpleNamespace(
        username="coach1",
        role="coach",
        is_active=True
    )

    monkeypatch.setattr(
        class_module,
        "find_username",
        lambda username: fake_coach if username == "coach1" else None
    )

    hall_manager = HallManager()
    hall_manager.add_hall(
        1,
        Hall("Yoga Hall", 20, ["Mat"], True)
    )

    manager = ClassManager(hall_manager)

    manager.add_class(
        1,
        GymClass(
            title="Yoga Beginners",
            sport="Yoga",
            coach="coach1",
            time=time(18, 30),
            day="Saturday",
            hall=1,
            capacity=15,
            status=True
        )
    )

    new_manager = ClassManager(hall_manager)

    assert 1 in new_manager.view_classes()
    assert new_manager.view_classes()[1].coach == "coach1"
    assert new_manager.view_classes()[1].time == time(18, 30)

    new_manager.deactivate_class(1)

    another_manager = ClassManager(hall_manager)

    assert another_manager.view_classes()[1].status is False