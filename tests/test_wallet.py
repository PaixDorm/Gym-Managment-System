"""تست‌های کیف پول، تراکنش و شارژ (wallet_manager).
اجرا از ریشه‌ی پروژه:  python -m pytest tests/test_wallet.py
همه‌ی تست‌ها روی فایل موقت (tmp_path) اجرا می‌شوند و به data/ دست نمی‌زنند.
"""
import pytest
from src.member import wallet_manager as wm
from src.models.transaction import Transaction, generate_tracking_code, traking_number_regex
from src.models.wallet import Wallet, InsufficientBalanceError

CARD = "6037991234567890"
GOOD = (CARD, "9", "1405", "012345", "123", "200000")   # card, month, year, password, cvv2, amount

class FakeBankReject:
    """بانک جعلی که همیشه رد می‌کند"""
    def pay(self, *args):
        raise ValueError("Invalid payment details.")

class CountingBank:
    """بانک جعلی که تعداد فراخوانی‌ها را می‌شمارد"""
    calls = 0
    def pay(self, card, month, year, password, cvv2, amount):
        CountingBank.calls += 1
        return f"{card}{amount}123456"

@pytest.fixture
def files(tmp_path, monkeypatch):
    path = tmp_path / "transactions.txt"
    monkeypatch.setattr(wm, "transactions_file_path", str(path))
    return path

def lines(path):
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

def test_wallet_deposit_and_withdraw():
    w = Wallet("sara_k", 100000)
    assert w.deposit(50000) == 150000
    assert w.withdraw(150000) == 0

def test_wallet_insufficient_balance_keeps_balance():
    w = Wallet("sara_k", 1000)
    with pytest.raises(InsufficientBalanceError):
        w.withdraw(2000)
    assert w.balance == 1000

@pytest.mark.parametrize("bad", [0, -5, "100", 10.5, True, None])
def test_wallet_rejects_bad_amounts(bad):
    with pytest.raises(ValueError):
        Wallet("sara_k").deposit(bad)

def test_wallet_balance_is_read_only():
    w = Wallet("sara_k")
    with pytest.raises(AttributeError):
        w.balance = 5

def test_wallet_dict_roundtrip():
    w = Wallet("sara_k", 700)
    assert Wallet.from_dict(w.to_dict()).balance == 700

@pytest.mark.parametrize("bad_type", [["x"], None, 5, "", "refund"])
def test_transaction_type_never_raises_typeerror(bad_type):
    with pytest.raises(ValueError):
        Transaction("sara_k", bad_type, 100, "x")

def test_transaction_line_roundtrip_with_and_without_receipt():
    t = Transaction("sara_k", "charge", 200000, "شارژ کیف پول", receipt="6037********7890200000123456")
    back = Transaction.from_line(t.to_line())
    assert (back.tracking_code, back.amount, back.receipt) == (t.tracking_code, 200000, t.receipt)
    no_receipt = Transaction("sara_k", "subscription", 100, "x")
    assert no_receipt.to_line().endswith(" | -")
    assert Transaction.from_line(no_receipt.to_line()).receipt is None

def test_old_six_field_lines_still_load():
    old = "TRX-20261010080530-4839 | sara_k | charge | 500 | 2026-10-10 08:05:30 | x"
    assert Transaction.from_line(old).receipt is None

@pytest.mark.parametrize("bad", [CARD + "200000123456", "603********7890200000123456", 5, ""])
def test_transaction_rejects_unmasked_or_bad_receipt(bad):
    with pytest.raises(ValueError):
        Transaction("sara_k", "charge", 100, "x", receipt=bad)

@pytest.mark.parametrize("bad", ["TRX-1 | sara_k | charge", "", "garbage"])
def test_transaction_bad_lines(bad):
    with pytest.raises(ValueError):
        Transaction.from_line(bad)

def test_persian_digits_rejected_in_transaction_line():
    line = "TRX-20261010080530-4839 | sara_k | charge | ۵۰۰ | 2026-10-10 08:05:30 | x"
    with pytest.raises(ValueError):
        Transaction.from_line(line)

def test_new_tracking_code_format():
    assert traking_number_regex.fullmatch(generate_tracking_code())

def test_charge_with_real_bank_increases_balance(files):
    tx = wm.charge_wallet("sara_k", *GOOD)
    assert tx.transaction_type == "charge" and tx.amount == 200000
    assert wm.get_balance("sara_k") == 200000
    assert len(lines(files)) == 1
    assert len(wm.get_transactions("sara_k")) == 1

def test_receipt_is_masked_stored_and_survives_reload(files):
    tx = wm.charge_wallet("sara_k", *GOOD)
    content = files.read_text(encoding="utf-8")
    assert CARD not in content                      # شماره‌ی کامل کارت هرگز ذخیره نمی‌شود
    assert "6037********7890200000" in content
    stored = wm.get_transactions("sara_k")[0]
    assert stored.receipt == tx.receipt and stored.tracking_code == tx.tracking_code

def test_bank_rejection_changes_nothing(files, monkeypatch):
    monkeypatch.setattr(wm, "API", FakeBankReject)
    with pytest.raises(ValueError):
        wm.charge_wallet("sara_k", *GOOD)
    assert wm.get_balance("sara_k") == 0
    assert lines(files) == []

@pytest.mark.parametrize("bad", [
    (CARD, "13", "1405", "012345", "123", "200000"),         
    (CARD, "9", "1405", "012345", "123", "-5"),              
    (CARD, "9", "1405", "012345", "123", "0"),               
    ("603799123456789", "9", "1405", "012345", "123", "1000"),  
    (CARD, "9", "1405", "abcdef", "123", "1000"),            
    ("۶۰۳۷۹۹۱۲۳۴۵۶۷۸۹۰", "9", "1405", "012345", "123", "1000"), 
    (CARD, "9", "1405", "012345", "123", "1۲۳"),             
])
def test_invalid_payment_inputs_change_nothing(files, bad):
    with pytest.raises(ValueError):
        wm.charge_wallet("sara_k", *bad)
    assert wm.get_balance("sara_k") == 0
    assert lines(files) == []

@pytest.mark.parametrize("bad_user", ["a|b", "", "   ", None, 5])
def test_invalid_username_never_reaches_the_bank(files, monkeypatch, bad_user):
    CountingBank.calls = 0
    monkeypatch.setattr(wm, "API", CountingBank)
    with pytest.raises(ValueError):
        wm.charge_wallet(bad_user, *GOOD)
    assert CountingBank.calls == 0
    assert lines(files) == []

def test_username_with_spaces_uses_same_wallet(files):
    wm.charge_wallet(" sara_k ", *GOOD)
    assert wm.get_balance("sara_k") == 200000
    assert len(wm.get_transactions(" sara_k ")) == 1

def test_two_members_are_independent(files):
    wm.charge_wallet("sara_k", *GOOD)
    wm.charge_wallet("arash", CARD, "9", "1405", "012345", "123", "50000")
    assert wm.get_balance("sara_k") == 200000
    assert wm.get_balance("arash") == 50000
    assert len(wm.get_transactions("arash")) == 1

def test_get_wallet_is_a_snapshot_of_the_balance(files):
    wm.charge_wallet("sara_k", *GOOD)
    w = wm.get_wallet("sara_k")
    assert w.balance == 200000 and w.has_enough(200000) and not w.has_enough(200001)

def test_disk_failure_after_bank_gives_traceable_error(files, monkeypatch):
    monkeypatch.setattr(wm, "API", CountingBank)

    def boom(line):
        raise wm.StorageError("disk")
    monkeypatch.setattr(wm, "_append_line", boom)
    with pytest.raises(wm.StorageError) as info:
        wm.charge_wallet("sara_k", *GOOD)
    message = str(info.value)
    assert "6037********7890" in message and CARD not in message
    assert "دوباره پرداخت نکنید" in message


def test_transient_disk_failure_is_retried_once(files, monkeypatch):
    real_append = wm._append_line
    state = {"n": 0}

    def flaky(line):
        state["n"] += 1
        if state["n"] == 1:
            raise wm.StorageError("temporary")
        real_append(line)
    monkeypatch.setattr(wm, "_append_line", flaky)
    wm.charge_wallet("sara_k", *GOOD)
    assert len(lines(files)) == 1 and wm.get_balance("sara_k") == 200000

def test_missing_and_empty_file(files):
    assert wm.get_balance("sara_k") == 0 and wm.get_transactions("sara_k") == []
    files.write_text("", encoding="utf-8")
    assert wm.get_balance("sara_k") == 0

def test_corrupted_line_history_skips_but_balance_stops(files):
    wm.charge_wallet("sara_k", *GOOD)
    with open(files, "a", encoding="utf-8") as f:
        f.write("garbage\n\n")
    assert len(wm.get_transactions("sara_k")) == 1           
    with pytest.raises(wm.StorageError) as info:
        wm.get_balance("sara_k")                              
    assert "شماره خط" in str(info.value)

def test_negative_balance_in_data_is_reported(files):
    wm.record_transaction(Transaction("zed", "subscription", 100, "x"))
    with pytest.raises(wm.StorageError):
        wm.get_balance("zed")

def test_tracking_code_collision_is_skipped(files, monkeypatch):
    first = wm.charge_wallet("sara_k", *GOOD)
    seq = iter([first.tracking_code, first.tracking_code, "TRX-20261010080530-12345678"])
    monkeypatch.setattr(wm, "generate_tracking_code", lambda: next(seq))
    tx = wm.new_transaction("sara_k", "charge", 100, "x")
    assert tx.tracking_code == "TRX-20261010080530-12345678"

def test_many_transactions_have_unique_codes(files):
    codes = set()
    for _ in range(60):
        tx = wm.new_transaction("sara_k", "charge", 100, "x")
        wm.record_transaction(tx)
        codes.add(tx.tracking_code)
    assert len(codes) == 60

def test_record_transaction_rejects_other_types(files):
    with pytest.raises(ValueError):
        wm.record_transaction("not a transaction")