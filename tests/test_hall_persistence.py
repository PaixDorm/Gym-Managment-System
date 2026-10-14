from src.admin.hall_manager import HallManager
from src.models.hall import Hall
import src.admin.hall_manager as hall_module


def test_hall_persistence(tmp_path, monkeypatch):
    monkeypatch.setattr(
        hall_module,
        "HALLS_FILE",
        tmp_path / "halls.txt"
    )

    manager = HallManager()
    manager.add_hall(
        1,
        Hall("Yoga", 20, ["Mat"], True)
    )

    new_manager = HallManager()

    assert 1 in new_manager.view_halls()
    assert new_manager.view_halls()[1].name == "Yoga"

    new_manager.deactivate_hall(1)

    another_manager = HallManager()

    assert another_manager.view_halls()[1].status is False