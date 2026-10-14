import unittest
from unittest.mock import patch
from main import main
class TestMain(unittest.TestCase):
    def check_role(self, choice, role):
        with (
            patch("main.HallManager") as hall_manager, patch("main.ClassManager") as class_manager,
            patch("main.get_valid_choice", side_effect=[choice, "4"]),
            patch("main.load_user", return_value=[]),
            patch(
                "main.login",
                return_value={
                    "success": True,
                    "username": "test_user"
                }
            ) as login_mock,
            patch("main.admin_panel") as admin,
            patch("main.CoachPanel") as coach,
            patch("main.MemberPanel") as member,
            patch("builtins.print")
        ):
            main()
            login_mock.assert_called_once_with(role, [])
            if role == "manager":
                admin.assert_called_once_with(
                    "test_user",
                    hall_manager.return_value,
                    class_manager.return_value
                )
                coach.assert_not_called()
                member.assert_not_called()

            elif role == "coach":
                coach.assert_called_once_with("test_user")
                coach.return_value.runner.assert_called_once()
                admin.assert_not_called()
                member.assert_not_called()

            elif role == "member":
                member.assert_called_once_with("test_user")
                member.return_value.runner.assert_called_once()
                admin.assert_not_called()
                coach.assert_not_called()
    def test_manager_panel(self):
        self.check_role("1", "manager")
    def test_coach_panel(self):
        self.check_role("2", "coach")
    def test_member_panel(self):
        self.check_role("3", "member")
if __name__ == "__main__":
    unittest.main()