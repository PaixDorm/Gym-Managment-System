import unittest
from unittest.mock import patch
from src.auth.authentication import authenticate_user


class AuthenticationTests(unittest.TestCase):

    def setUp(self):
        self.users = [
            {
                "username": "amir",
                "password": "Test@123",
                "role": "coach",
                "is_active": True
            },
            {
                "username": "ali",
                "password": "Test@456",
                "role": "member",
                "is_active": False
            }
        ]

    @patch("src.logging.activity_logger.save_log")
    def test_successful_login(self, mock_log):
        result = authenticate_user(
            "amir", "Test@123", "coach", self.users
        )
        self.assertTrue(result["success"])

    @patch("src.logging.activity_logger.save_log")
    def test_wrong_password(self, mock_log):
        result = authenticate_user(
            "amir", "wrong", "coach", self.users
        )
        self.assertFalse(result["success"])

    @patch("src.logging.activity_logger.save_log")
    def test_inactive_user(self, mock_log):
        result = authenticate_user(
            "ali", "Test@456", "member", self.users
        )
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()