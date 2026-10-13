"""تست‌های اشتراک (مدل‌ها و subscription_manager).
اجرا از ریشه‌ی پروژه:  python -m pytest tests/test_subscriptions.py
همه‌ی تست‌ها روی فایل موقت (tmp_path) اجرا می‌شوند و به data/ دست نمی‌زنند.
"""
from datetime import date, datetime

import pytest

from src.member import subscription_manager as sm
from src.member import wallet_manager as wm
from src.models.subscription import Subscription, SubscriptionPlan, next_start_date
from src.models.wallet import InsufficientBalanceError

TRK = "TRX-20261010080530-48391234"
D = date

@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(wm, "transactions_file_path", str(tmp_path / "transactions.txt"))
    monkeypatch.setattr(sm, "subscription_file_path", str(tmp_path / "subscriptions.txt"))
    monkeypatch.setattr(sm, "subscription_plans", dict(sm.subscription_plans))   # جدا از طرح‌های واقعی
    return tmp_path

def fund(username, amount):
    wm.record_transaction(wm.new_transaction(username, "charge", amount, "شارژ"))

def count(path):
    return len(path.read_text(encoding="utf-8").splitlines()) if path.exists() else 0

@pytest.mark.parametrize("months,end", [(1, D(2026, 11, 9)), (3, D(2027, 1, 8)), (6, D(2027, 4, 8))])
def test_end_dates(months, end):
    assert Subscription("sara_k", months, 1000, D(2026, 10, 10), TRK).end_date == end

def test_active_boundaries():
    s = Subscription("sara_k", 1, 1000, D(2026, 10, 10), TRK)
    assert not s.is_active(D(2026, 10, 9))
    assert s.is_active(D(2026, 10, 10)) and s.days_left(D(2026, 10, 10)) == 30
    assert s.is_active(D(2026, 11, 8)) and s.days_left(D(2026, 11, 8)) == 1
    assert not s.is_active(D(2026, 11, 9)) and s.days_left(D(2026, 11, 9)) == 0

def test_next_start_date_cases():
    s = Subscription("sara_k", 1, 1000, D(2026, 10, 10), TRK)
    assert next_start_date(None, D(2026, 10, 10)) == D(2026, 10, 10)
    assert next_start_date(s, D(2026, 10, 20)) == D(2026, 11, 9)     
    assert next_start_date(s, D(2026, 12, 1)) == D(2026, 12, 1)      

@pytest.mark.parametrize("args", [(2, 100), (0, 100), (True, 100), (1, 0), (1, -5), (1, "5"), ("1", 100), ([1], 100)])
def test_plan_validation(args):
    with pytest.raises(ValueError):
        SubscriptionPlan(*args)

@pytest.mark.parametrize("bad", [datetime(2026, 10, 10), "2026-10-10"])
def test_subscription_requires_date_not_datetime(bad):
    with pytest.raises(ValueError):
        Subscription("sara_k", 1, 1000, bad, TRK)

def test_subscription_line_roundtrip():
    s = Subscription("sara_k", 3, 250000, D(2026, 10, 10), TRK, payment_date=D(2026, 10, 10))
    back = Subscription.from_line(s.to_line())
    assert (back.username, back.months, back.amount, back.start_date, back.tracking_code, back.payment_date) == \
        ("sara_k", 3, 250000, D(2026, 10, 10), TRK, D(2026, 10, 10))

@pytest.mark.parametrize("bad", ["", "a | b | c", TRK + " | sara_k | abc | 100 | 2026-10-10 | 2026-10-10", TRK + " | sara_k | 1 | 100 | 2026/10/10 | 2026-10-10"])
def test_subscription_bad_lines(bad):
    with pytest.raises(ValueError):
        Subscription.from_line(bad)

@pytest.mark.parametrize("months,price,end", [(1, 100000, D(2026, 11, 9)), (3, 250000, D(2027, 1, 8)), (6, 450000, D(2027, 4, 8))])
def test_purchase_plans(env, months, price, end):
    fund("sara_k", 1000000)
    sub = sm.buy_subscription("sara_k", months, today=D(2026, 10, 10))
    assert sub.amount == price and sub.start_date == D(2026, 10, 10) and sub.end_date == end
    assert wm.get_balance("sara_k") == 1000000 - price
    assert count(env / "transactions.txt") == 2 and count(env / "subscriptions.txt") == 1

def test_subscription_and_transaction_share_tracking_code(env):
    fund("sara_k", 500000)
    sub = sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    payments = sm.get_all_subscription_payments()
    assert len(payments) == 1 and payments[0].tracking_code == sub.tracking_code

def test_insufficient_balance_changes_nothing(env):
    fund("sara_k", 100000)
    with pytest.raises(InsufficientBalanceError):
        sm.buy_subscription("sara_k", 3, today=D(2026, 10, 10))
    assert wm.get_balance("sara_k") == 100000
    assert count(env / "transactions.txt") == 1 and count(env / "subscriptions.txt") == 0

def test_renewal_chains_without_overlap(env):
    fund("sara_k", 1000000)
    a = sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    b = sm.buy_subscription("sara_k", 1, today=D(2026, 10, 20))
    c = sm.buy_subscription("sara_k", 1, today=D(2026, 10, 25))
    assert (a.end_date, b.start_date) == (D(2026, 11, 9), D(2026, 11, 9))
    assert (b.end_date, c.start_date) == (D(2026, 12, 9), D(2026, 12, 9))
    assert wm.get_balance("sara_k") == 1000000 - 300000

def test_buying_after_expiry_starts_today(env):
    fund("sara_k", 500000)
    sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    again = sm.buy_subscription("sara_k", 1, today=D(2026, 12, 1))
    assert again.start_date == D(2026, 12, 1)

def test_payment_date_matches_transaction_date(env):
    fund("sara_k", 500000)
    sub = sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    tx = sm.get_all_subscription_payments()[0]
    assert tx.date.date() == sub.payment_date == D(2026, 10, 10)

@pytest.mark.parametrize("months", [2, 0, True, "1", None, [1]])
def test_invalid_plan_or_months(env, months):
    fund("sara_k", 500000)
    with pytest.raises(ValueError):
        sm.buy_subscription("sara_k", months, today=D(2026, 10, 10))
    assert count(env / "subscriptions.txt") == 0

@pytest.mark.parametrize("user", ["a|b", "", None, 5])
def test_invalid_username(env, user):
    with pytest.raises(ValueError):
        sm.buy_subscription(user, 1, today=D(2026, 10, 10))

def test_today_must_be_date(env):
    fund("sara_k", 500000)
    with pytest.raises(ValueError):
        sm.buy_subscription("sara_k", 1, today=datetime(2026, 10, 10))

def test_two_members_do_not_affect_each_other(env):
    fund("sara_k", 500000)
    fund("arash", 500000)
    sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    assert wm.get_balance("arash") == 500000
    assert sm.get_subscription_state("arash", D(2026, 10, 15)) == "none"
    assert sm.has_active_subscription("sara_k", D(2026, 10, 15))

def test_subscription_write_failure_charges_nothing(env, monkeypatch):
    fund("sara_k", 500000)
    def boom(sub):
        raise wm.StorageError("disk")
    monkeypatch.setattr(sm, "_append_subscription", boom)
    with pytest.raises(wm.StorageError) as info:
        sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    assert "مبلغی کسر نشد" in str(info.value)
    assert wm.get_balance("sara_k") == 500000
    assert sm.get_user_subscriptions("sara_k") == []

def test_transaction_write_failure_charges_nothing_and_pending_row_is_ignored(env, monkeypatch):
    fund("sara_k", 500000)
    def boom(tx):
        raise wm.StorageError("disk")
    monkeypatch.setattr(sm, "record_transaction", boom)
    with pytest.raises(wm.StorageError):
        sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    assert wm.get_balance("sara_k") == 500000
    assert count(env / "subscriptions.txt") == 1                      
    assert sm.get_user_subscriptions("sara_k") == []              
    assert sm.get_subscription_state("sara_k", D(2026, 10, 12)) == "none"
    assert sm.get_total_revenue() == 0

def test_retry_after_failure_charges_exactly_once(env, monkeypatch):
    fund("sara_k", 500000)
    real = sm.record_transaction
    monkeypatch.setattr(sm, "record_transaction", lambda tx: (_ for _ in ()).throw(wm.StorageError("disk")))
    with pytest.raises(wm.StorageError):
        sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    monkeypatch.setattr(sm, "record_transaction", real)
    sub = sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    assert wm.get_balance("sara_k") == 400000
    assert len(sm.get_user_subscriptions("sara_k")) == 1
    assert sm.get_total_revenue() == 100000 and sub.start_date == D(2026, 10, 10)

def test_corrupted_subscription_row_is_reported_not_ignored(env):
    fund("sara_k", 500000)
    sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    path = env / "subscriptions.txt"
    path.write_text(path.read_text(encoding="utf-8").replace(" | sara_k | ", " | sara_k | oops | "), encoding="utf-8")
    with pytest.raises(wm.StorageError) as info:
        sm.get_subscription_state("sara_k", D(2026, 10, 20))
    assert "شماره خط 1" in str(info.value)
    with pytest.raises(wm.StorageError):
        sm.buy_subscription("sara_k", 1, today=D(2026, 10, 20))        # خرید روی داده‌ی ناقص انجام نمی‌شود
    assert count(env / "transactions.txt") == 2

def test_state_current_subscription_and_days_left(env):
    assert sm.get_subscription_state("sara_k", D(2026, 10, 10)) == "none"
    assert sm.get_current_subscription("sara_k", D(2026, 10, 10)) is None
    assert sm.get_days_left("sara_k", D(2026, 10, 10)) == 0
    fund("sara_k", 500000)
    sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    assert sm.get_subscription_state("sara_k", D(2026, 10, 20)) == "active"
    assert sm.get_days_left("sara_k", D(2026, 10, 20)) == 20
    assert sm.get_current_subscription("sara_k", D(2026, 10, 20)).start_date == D(2026, 10, 10)
    assert sm.get_subscription_state("sara_k", D(2026, 11, 9)) == "expired"
    assert sm.has_active_subscription("sara_k", D(2026, 11, 9)) is False
    assert sm.get_current_subscription("sara_k", D(2026, 11, 9)).end_date == D(2026, 11, 9)   # برای منقضی: آخرین

def test_set_plan_changes_price_and_validates(env):
    sm.set_plan(1, 120000)
    assert sm.get_plan(1).price == 120000
    fund("sara_k", 500000)
    assert sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10)).amount == 120000
    for bad in [(2, 100), (1, 0), (1, -5), (True, 100)]:
        with pytest.raises(ValueError):
            sm.set_plan(*bad)

def test_reports(env):
    fund("sara_k", 1000000)
    fund("arash", 1000000)
    sm.buy_subscription("sara_k", 1, today=D(2026, 10, 10))
    sm.buy_subscription("sara_k", 3, today=D(2026, 10, 12))
    sm.buy_subscription("arash", 1, today=D(2026, 10, 15))
    assert sm.get_total_revenue() == 100000 + 250000 + 100000
    assert sm.get_revenue_by_type() == {1: 200000, 3: 250000}
    report = sm.get_payments_report()
    assert len(report) == 3
    assert report[0]["username"] == "arash" and report[0]["plan"] == "یک‌ماهه"          # جدیدترین اول
    assert set(report[0]) == {"username", "plan", "months", "amount", "payment_date", "start_date", "end_date", "tracking_code"}
    assert sm.get_members_status(["sara_k", "arash", "nobody"], D(2026, 10, 20)) == \
           {"sara_k": "active", "arash": "active", "nobody": "none"}
    assert sm.get_members_status(["sara_k", "arash"], D(2027, 6, 1)) == {"sara_k": "expired", "arash": "expired"}

def test_reports_on_empty_data(env):
    assert sm.get_total_revenue() == 0 and sm.get_revenue_by_type() == {} and sm.get_payments_report() == []
    with pytest.raises(ValueError):
        sm.get_members_status("sara_k")