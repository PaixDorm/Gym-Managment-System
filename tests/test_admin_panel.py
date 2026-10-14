import unittest
from unittest.mock import patch, Mock

from src.admin.admin_panel import admin_panel


class TestAdminPanel(unittest.TestCase):

    def test_hall_menu(self):
        hall_manager = Mock()
        class_manager = Mock()

        with (
            patch(
                "src.admin.admin_panel.get_valid_choice",
                side_effect=["6", "5"]
            ),
            patch(
                "src.admin.admin_panel.hall_panel"
            ) as mock_hall_panel
        ):
            admin_panel(
                "admin_test",
                hall_manager,
                class_manager
            )

            mock_hall_panel.assert_called_once_with(
                hall_manager
            )

    def test_class_menu(self):
        hall_manager = Mock()
        class_manager = Mock()

        with (
            patch(
                "src.admin.admin_panel.get_valid_choice",
                side_effect=["7", "5"]
            ),
            patch(
                "src.admin.admin_panel.class_panel"
            ) as mock_class_panel
        ):
            admin_panel(
                "admin_test",
                hall_manager,
                class_manager
            )

            mock_class_panel.assert_called_once_with(
                class_manager
            )

    def test_revenue_report(self):
        with (
            patch(
                "src.admin.admin_panel.get_valid_choice",
                side_effect=["8", "5"]
            ),
            patch(
                "src.admin.admin_panel.get_revenue_by_type",
                return_value={
                    1: 100000,
                    3: 250000
                }
            ) as mock_revenue
        ):
            admin_panel(
                "admin_test",
                Mock(),
                Mock()
            )

            mock_revenue.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()