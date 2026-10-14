from types import SimpleNamespace
from unittest.mock import patch

from src.admin.subscription_panel import subscription_panel


def test_member_status():
    member = SimpleNamespace(name="Sara", username="sara", role="member")
    with (
        patch("src.admin.subscription_panel.get_valid_choice", side_effect=["1", "4"]),
        patch("src.admin.subscription_panel.load_user", return_value=[member]),
        patch("src.admin.subscription_panel.get_members_status", return_value={"sara": "none"}) as status,
        patch("builtins.print") as output,
    ):
        subscription_panel()
        status.assert_called_once_with(["sara"])
        output.assert_any_call("Sara (sara): بدون اشتراک")


def test_purchase_uses_finance():
    member = SimpleNamespace(username="sara", role="member", is_active=True)
    plan = SimpleNamespace(price=100000)
    sub = SimpleNamespace(start_date="2026-10-14", end_date="2026-11-13", tracking_code="TRX-TEST")
    with (
        patch("src.admin.subscription_panel.get_valid_choice", side_effect=["3", "1", "4"]),
        patch("src.admin.subscription_panel.get_non_empty_input", return_value="sara"),
        patch("src.admin.subscription_panel.find_username", return_value=member),
        patch("src.admin.subscription_panel.get_plans", return_value={1: plan}),
        patch("src.admin.subscription_panel.get_wallet", return_value=SimpleNamespace(balance=150000)),
        patch("src.admin.subscription_panel.confirm_action", return_value=True),
        patch("src.admin.subscription_panel.buy_subscription", return_value=sub) as buy,
    ):
        subscription_panel()
        buy.assert_called_once_with("sara", 1)


def test_payment_report_shows_receipt():
    item = {"username":"sara", "months":1,"amount":100000,"payment_date":"2026-10-14","start_date":"2026-10-14","end_date":"2026-11-13","tracking_code":"TRX-TEST"}
    with (
        patch("src.admin.subscription_panel.get_valid_choice", side_effect=["2", "4"]),
        patch("src.admin.subscription_panel.get_payments_report", return_value=[item]),
        patch("src.admin.subscription_panel.load_user", return_value=[SimpleNamespace(username="sara", name="Sara")]),
        patch("builtins.print") as output,
    ):
        subscription_panel()
        assert any("TRX-TEST" in str(call) for call in output.call_args_list)
