import unittest
from unittest.mock import patch, Mock

from src.admin.admin_panel import admin_panel


class TestAdminPanel(unittest.TestCase):
    def test_subscription_menu(self):
        with (
            patch(
                "src.admin.admin_panel.get_valid_choice",
                side_effect=["10", "5"]
            ),
            patch(
                "src.admin.admin_panel.subscription_panel"
            ) as mock_panel
        ):
            admin_panel("admin_test", Mock(), Mock())
            mock_panel.assert_called_once_with()

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
    def test_statistics_report(self):
        from types import SimpleNamespace

        users = [
            SimpleNamespace(role="member", is_active=True),
            SimpleNamespace(role="member", is_active=False),
            SimpleNamespace(role="coach", is_active=True)
        ]

        class_manager = Mock()
        class_manager.view_classes.return_value = {
            1: SimpleNamespace(status=True),
            2: SimpleNamespace(status=False)
        }

        with (
            patch(
                "src.admin.admin_panel.get_valid_choice",
                side_effect=["9", "5"]
            ),
            patch(
                "src.admin.admin_panel.load_user",
                return_value=users
            ),
            patch("builtins.print") as mock_print
        ):
            admin_panel("manager_test", Mock(), class_manager)

            mock_print.assert_any_call("اعضای فعال:", 1)
            mock_print.assert_any_call("مربیان فعال:", 1)
            mock_print.assert_any_call("کلاس‌های فعال:", 1)

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