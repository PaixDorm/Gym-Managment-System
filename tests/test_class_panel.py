import unittest
from unittest.mock import Mock, patch

from src.admin.class_panel import class_panel


class TestClassPanel(unittest.TestCase):

    @patch("src.admin.class_panel.GymClass")
    @patch(
        "src.admin.class_panel.get_non_empty_input",
        side_effect=[
            "Yoga", "Yoga", "coach_test",
            "Saturday", "18:30"
        ]
    )
    @patch(
        "src.admin.class_panel.get_valid_choice",
        side_effect=["1", "4"]
    )
    @patch(
        "builtins.input",
        side_effect=["1", "2", "15"]
    )
    def test_add_class(
        self, mock_input, mock_choice,
        mock_text, mock_gym_class
    ):
        manager = Mock()

        class_panel(manager)

        manager.add_class.assert_called_once_with(
            1, mock_gym_class.return_value
        )

    @patch(
        "src.admin.class_panel.get_valid_choice",
        side_effect=["2", "4"]
    )
    def test_view_classes(self, mock_choice):
        manager = Mock()
        manager.view_classes.return_value = {}

        class_panel(manager)

        manager.view_classes.assert_called_once()

    @patch("builtins.input", return_value="1")
    @patch(
        "src.admin.class_panel.get_valid_choice",
        side_effect=["3", "2", "4"]
    )
    def test_deactivate_class(self, mock_choice, mock_input):
        manager = Mock()

        class_panel(manager)

        manager.deactivate_class.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()