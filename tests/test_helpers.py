import unittest
from unittest.mock import patch

from src.utils.helpers import (
    get_valid_choice,
    get_non_empty_input,
    confirm_action
)


class TestHelpers(unittest.TestCase):

    @patch("builtins.input", return_value="2")
    def test_valid_choice(self, mock_input):
        result = get_valid_choice("انتخاب: ", ["1", "2", "3"])
        self.assertEqual(result, "2")

    @patch("builtins.input", side_effect=["9", "1"])
    def test_invalid_choice_retry(self, mock_input):
        result = get_valid_choice("انتخاب: ", ["1", "2"])
        self.assertEqual(result, "1")
        self.assertEqual(mock_input.call_count, 2)

    @patch("builtins.input", return_value="  Ali  ")
    def test_non_empty_input(self, mock_input):
        result = get_non_empty_input("نام: ")
        self.assertEqual(result, "Ali")

    @patch("builtins.input", side_effect=["", "   ", "Sara"])
    def test_empty_input_retry(self, mock_input):
        result = get_non_empty_input("نام: ")
        self.assertEqual(result, "Sara")

    @patch("builtins.input", return_value="Y")
    def test_confirm_yes(self, mock_input):
        result = confirm_action("تأیید؟ ")
        self.assertTrue(result)

    @patch("builtins.input", side_effect=["maybe", "n"])
    def test_confirm_no_after_invalid(self, mock_input):
        result = confirm_action("تأیید؟ ")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()