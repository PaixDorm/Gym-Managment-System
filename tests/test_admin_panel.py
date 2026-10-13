import unittest
from unittest.mock import patch, Mock
from src.admin.admin_panel import admin_panel


class TestAdminPanel(unittest.TestCase):

    @patch("src.admin.admin_panel.hall_panel")
    @patch("src.admin.admin_panel.get_valid_choice", side_effect=["6", "5"])
    def test_hall_menu(self, mock_choice, mock_hall_panel):
        manager = Mock()
        admin_panel("admin_test", manager)
        mock_hall_panel.assert_called_once_with(manager)


if __name__ == "__main__":
    unittest.main()