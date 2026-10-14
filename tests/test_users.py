import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.validation.validators import (
    validate_password,
    validate_email,
    validate_username,
    validate_name)
from src.models.user import User
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.admin.user_manager import (
    save_user,
    load_user
)
class TestValidators(unittest.TestCase):
    def test_password_valid(self):
        self.assertTrue(validate_password("Ali@123"))
    def test_password_no_letter(self):
        self.assertFalse(validate_password("123@"))
    def test_password_no_digit(self):
        self.assertFalse(validate_password("Ali@"))
    def test_password_no_special(self):
        self.assertFalse(validate_password("Ali123"))
    def test_password_empty(self):
        self.assertFalse(validate_password(""))
    def test_email_valid(self):
        self.assertTrue(validate_email("ali@test.com"))
    def test_email_valid_ir(self):
        self.assertTrue(validate_email("ali@test.ir"))
    def test_email_no_at(self):
        self.assertFalse(validate_email("ali.test.com"))
    def test_email_no_dot(self):
        self.assertFalse(validate_email("ali@test"))
    def test_email_empty(self):
        self.assertFalse(validate_email(""))
    def test_username_valid(self):
        self.assertTrue(validate_username("ali_123"))
    def test_username_too_short(self):
        self.assertFalse(validate_username("ab"))
    def test_username_invalid_char(self):
        self.assertFalse(validate_username("ali@123"))
    def test_username_empty(self):
        self.assertFalse(validate_username(""))
    def test_name_valid(self):
        self.assertTrue(validate_name("علی رضایی"))
    def test_name_english(self):
        self.assertTrue(validate_name("Sara"))
    def test_name_too_short(self):
        self.assertFalse(validate_name("ا"))
    def test_name_empty(self):
        self.assertFalse(validate_name(""))
class TestUserModel(unittest.TestCase):
    def test_to_dict(self):
        user = User("علی", "ali", "Ali@123", "ali@test.com", "member", True)
        data = user.to_dict()
        self.assertEqual(data["name"], "علی")
        self.assertEqual(data["username"], "ali")
        self.assertEqual(data["password"], "Ali@123")
        self.assertEqual(data["email"], "ali@test.com")
        self.assertEqual(data["role"], "member")
        self.assertEqual(data["is_active"], True)
    def test_from_dict(self):
        data = {
            "name": "سارا",
            "username": "sara",
            "password": "Sara@1",
            "email": "sara@test.com",
            "role": "coach",
            "is_active": True}
        user = User.from_dict(data)
        self.assertEqual(user.name, "سارا")
        self.assertEqual(user.username, "sara")
        self.assertEqual(user.role, "coach")
        self.assertTrue(user.is_active)
    def test_from_dict_defaults(self):
        data = {"name": "علی", "username": "ali"}
        user = User.from_dict(data)
        self.assertEqual(user.name, "علی")
        self.assertEqual(user.username, "ali")
        self.assertEqual(user.role, "member")
        self.assertTrue(user.is_active)
if __name__ == "__main__":
    unittest.main()
def test_inactive_user_stays_inactive(self):
    with tempfile.TemporaryDirectory() as folder:
        path = str(Path(folder) / "users.txt")

        with patch(
            "src.admin.user_manager.USERS_FILE",
            path
        ):
            user = User(
                "سارا",
                "sara",
                "Sara@123",
                "sara@test.com",
                "member",
                False
            )

            save_user([user])
            loaded_user = load_user()[0]

            self.assertIs(
                loaded_user.is_active,
                False
            )
