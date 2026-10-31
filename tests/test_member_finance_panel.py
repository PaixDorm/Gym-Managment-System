import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.member.member_panel import MemberPanel


class TestMemberFinancePanel(unittest.TestCase):
    def setUp(self):
        # Bypass file-manager initialization; dependencies are patched below.
        self.panel = MemberPanel.__new__(MemberPanel)
        self.panel.username = "member_test"

    def test_profile_without_subscription(self):
        user = SimpleNamespace(
            name="Test Member", username="member_test",
            email="member@example.com", is_active=True
        )
        with (
            patch("src.member.member_panel.find_username", return_value=user),
            patch("src.member.member_panel.get_subscription_state", return_value="none"),
            patch("src.member.member_panel.get_current_subscription", return_value=None),
            patch("builtins.print") as mock_print,
        ):
            self.panel.my_profile_and_subscription_status()
            mock_print.assert_any_call("No subscription")

    def test_view_wallet_balance(self):
        with (
            patch("src.member.member_panel.get_wallet", return_value=SimpleNamespace(balance=150000)) as mock_wallet,
            patch("builtins.print") as mock_print,
        ):
            self.panel.see_my_wallet()
            mock_wallet.assert_called_once_with("member_test")
            mock_print.assert_any_call("Balance: 150000")

    def test_view_no_transactions(self):
        with (
            patch("src.member.member_panel.get_transactions", return_value=[]) as mock_transactions,
            patch("builtins.print") as mock_print,
        ):
            self.panel.see_my_transactions()
            mock_transactions.assert_called_once_with("member_test")
            mock_print.assert_any_call("No transactions found.")

    def test_buy_subscription_calls_financial_module(self):
        with (
            patch("builtins.input", return_value="3"),
            patch("src.member.member_panel.get_plans", return_value={}),
            patch("src.member.member_panel.buy_subscription") as mock_buy,
            patch("builtins.print"),
        ):
            self.panel.buy_or_renewal_my_subscription()
            mock_buy.assert_called_once_with("member_test", 3)

    def test_charge_wallet_calls_financial_module(self):
        inputs = ["1111222233334444", "09", "1405", "012345", "123", "50000"]
        with (
            patch("builtins.input", side_effect=inputs),
            patch("src.member.member_panel.charge_wallet") as mock_charge,
        ):
            self.panel.charge_my_wallet()
            mock_charge.assert_called_once_with("member_test", *inputs)


if __name__ == "__main__":
    unittest.main()
