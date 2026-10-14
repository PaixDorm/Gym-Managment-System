import unittest
from unittest.mock import patch, Mock
from src.admin.admin_panel import admin_panel


class TestAdminPanel(unittest.TestCase):

    @patch("src.admin.admin_panel.hall_panel")
    @patch("src.admin.admin_panel.get_valid_choice", side_effect=["6", "5"])
    def test_hall_menu(self, mock_choice, mock_hall_panel):
        manager = Mock()
        admin_panel("admin_test", manager, Mock())
        mock_hall_panel.assert_called_once_with(manager)
    @patch("src.admin.admin_panel.class_panel")
    @patch(
        "src.admin.admin_panel.get_valid_choice",
        side_effect=["7", "5"]
    )
    @patch("src.admin.admin_panel.get_revenue_by_type")
    @patch(
        "src.admin.admin_panel.get_valid_choice",
        side_effect=["8", "5"]
    )
    def test_revenue_report(self, mock_choice, mock_revenue):
        mock_revenue.return_value = {
            1: 100000,
            3: 250000
        }

        admin_panel("admin_test", Mock(), Mock())

        mock_revenue.assert_called_once_with()
    def test_class_menu(self, mock_choice, mock_class_panel):
        hall_manager = Mock()
        class_manager = Mock()

        admin_panel("admin_test", hall_manager, class_manager)

        mock_class_panel.assert_called_once_with(class_manager)


if __name__ == "__main__":
    unittest.main()