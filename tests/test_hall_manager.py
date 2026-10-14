import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.admin.hall_manager import HallManager
from src.models.hall import Hall


class TestHallManager(unittest.TestCase):

    def setUp(self):
        # برای هر تست، یک فایل سالن جداگانه می‌سازیم
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        test_file = Path(self.temp_dir.name) / "halls.txt"

        patcher = patch(
            "src.admin.hall_manager.HALLS_FILE",
            test_file
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        self.manager = HallManager()
        self.hall = Hall(
            "سالن شماره یک",
            20,
            ["دمبل"],
            True
        )

    def test_add_hall(self):
        self.manager.add_hall(1, self.hall)
        self.assertIn(1, self.manager.view_halls())

    def test_duplicate_id(self):
        self.manager.add_hall(1, self.hall)

        with self.assertRaises(ValueError):
            self.manager.add_hall(1, self.hall)

    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            Hall("سالن", -5, [], True)

    def test_deactivate_hall(self):
        self.manager.add_hall(1, self.hall)
        self.manager.deactivate_hall(1)
        self.assertFalse(self.hall.status)

    def test_activate_hall(self):
        self.manager.add_hall(1, self.hall)
        self.manager.deactivate_hall(1)
        self.manager.activate_hall(1)
        self.assertTrue(self.hall.status)

    def test_missing_hall(self):
        with self.assertRaises(ValueError):
            self.manager.activate_hall(99)


if __name__ == "__main__":
    unittest.main()