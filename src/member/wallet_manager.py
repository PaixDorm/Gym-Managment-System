import os
import re
from src.models.wallet import Wallet
from src.models.transaction import Transaction, generate_tracking_code
from Bank import API

card_regex = re.compile(r"^[0-9]{16}$")
month_regex = re.compile(r"^(?:0?[1-9]|1[0-2])$")
year_regex = re.compile(r"^[0-9]{4}$")
password_regex = re.compile(r"^[0-9]{6}$")
cvv2_regex = re.compile(r"^[0-9]{3}$")
amount_regex = re.compile(r"^[1-9][0-9]*$")


def validate_card_number(card_input):
    """Validate a card number containing exactly 16 digits."""
    if not isinstance(card_input, str):
        raise ValueError("Card number must be a string.")
    card_str = card_input.strip()
    if not card_regex.fullmatch(card_str):
        raise ValueError("Card number must contain exactly 16 digits.")
    return card_str

def validate_exp_month(month_input):
    """Validate an expiration month between 1 and 12."""
    if not isinstance(month_input, str):
        raise ValueError("Expiration month must be a string.")
    month_str = month_input.strip()
    if not month_regex.fullmatch(month_str):
        raise ValueError("Expiration month must be between 1 and 12.")
    return int(month_str)

def validate_exp_year(year_input):
    """Validate a four-digit expiration year."""
    if not isinstance(year_input, str):
        raise ValueError("Expiration year must be a string.")
    year_str = year_input.strip()
    if not year_regex.fullmatch(year_str):
        raise ValueError("Expiration year must be a valid four-digit number.")
    return int(year_str)

def validate_card_password(password_input):
    """Validate a six-digit payment password, preserving leading zeros."""
    if not isinstance(password_input, str):
        raise ValueError("Card payment password must be a string.")
    pass_str = password_input.strip()
    if not password_regex.fullmatch(pass_str):
        raise ValueError("Card payment password must contain exactly 6 digits.")
    return pass_str

def validate_cvv2(cvv2_input):
    """Validate a three-digit CVV2."""
    if not isinstance(cvv2_input, str):
        raise ValueError("CVV2 must be a string.")
    cvv2_str = cvv2_input.strip()
    if not cvv2_regex.fullmatch(cvv2_str):
        raise ValueError("CVV2 must contain exactly 3 digits.")
    return cvv2_str

def validate_amount(amount_input):
    """Validate a transaction amount."""
    if not isinstance(amount_input, str):
        raise ValueError("Amount must be a string.")
    amount_str = amount_input.strip()
    if not amount_regex.fullmatch(amount_str):
        raise ValueError("Amount must be a positive integer.")
    return int(amount_str)

def validate_payment_inputs(card, month, year, password, cvv2, amount):
    """Validate all payment fields together."""
    valid_card = validate_card_number(card)
    valid_month = validate_exp_month(month)
    valid_year = validate_exp_year(year)
    valid_pass = validate_card_password(password)
    valid_cvv2 = validate_cvv2(cvv2)
    valid_amount = validate_amount(amount)
    return (valid_card, valid_month, valid_year, valid_pass, valid_cvv2, valid_amount)

current_dir = os.path.abspath(os.path.dirname(__file__))
transactions_file_path = os.path.normpath(os.path.join(current_dir, "../../data/transactions.txt"))

class StorageError(Exception):
    """Raised when reading or writing transaction files fails."""
    pass

def _append_line(line):
    """Append a transaction record using UTF-8."""
    try:
        directory = os.path.dirname(transactions_file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(transactions_file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        raise StorageError("Failed to save data to disk.") from None

def _read_lines():
    """Read transaction records; return an empty list if missing."""
    if not os.path.exists(transactions_file_path):
        return []
    try:
        with open(transactions_file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        raise StorageError("Failed to read data from disk.") from None

def _load_transactions(strict=False):
    """Load transactions, optionally rejecting malformed records."""
    lines = _read_lines()
    transactions = []
    for idx, line in enumerate(lines, start=1):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        try:
            tx = Transaction.from_line(line_stripped)
            transactions.append(tx)
        except ValueError:
            if strict:
                raise StorageError(f"Invalid stored transaction data on line {idx}: invalid record format.") from None
            continue
    return transactions

def get_all_transactions(strict=False):
    """Return all transactions for reports and subscription reconciliation."""
    return _load_transactions(strict=strict)

def get_balance(username):
    """Calculate balance from transactions (charges positive, subscriptions negative)."""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Invalid username.")
    username = username.strip()
    all_transactions = _load_transactions(strict=True)
    balance = 0
    for tx in all_transactions:
        if tx.username == username:
            if tx.transaction_type == "charge":
                balance += tx.amount
            elif tx.transaction_type == "subscription":
                balance -= tx.amount
    if balance < 0:
        raise StorageError("Negative wallet balance indicates inconsistent stored transaction data.")
    return balance

def get_wallet(username):
    """Return a wallet with its balance calculated from transactions."""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Invalid username.")
    username = username.strip()
    current_balance = get_balance(username)
    return Wallet(username, balance=current_balance)

def get_transactions(username):
    """Return user transactions, ignoring unrelated malformed records."""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Invalid username.")
    username = username.strip()
    all_transactions = _load_transactions(strict=False)
    return [tx for tx in all_transactions if tx.username == username]

def record_transaction(transaction):
    """Validate and record a transaction without duplicate tracking codes."""
    if not isinstance(transaction, Transaction):
        raise ValueError("Input must be a Transaction instance.")
    existing_transactions = _load_transactions(strict=False)
    if any(tx.tracking_code == transaction.tracking_code for tx in existing_transactions):
        return
    _append_line(transaction.to_line())

def _mask_receipt(card, payment_id):
    """Mask receipt: first four digits, eight stars, last four, then payment suffix."""
    if not (isinstance(card, str) and isinstance(payment_id, str)
            and len(card) == 16 and payment_id.startswith(card) and len(payment_id) > 16):
        raise ValueError("Bank receipt cannot be masked.")
    return card[:4] + "*" * 8 + card[-4:] + payment_id[16:]

def new_transaction(username, transaction_type, amount, description, when=None):
    """Create a transaction with a unique tracking code."""
    existing_codes = {tx.tracking_code for tx in _load_transactions(strict=True)}
    for _ in range(10):
        code = generate_tracking_code()
        if code not in existing_codes:
            return Transaction(username=username, transaction_type=transaction_type, amount=amount,
                               description=description, date=when, tracking_code=code)
    raise StorageError("Could not generate a unique tracking code.")

def charge_wallet(username, card, month, year, password, cvv2, amount):
    """Top up wallet with input validation, bank payment, and file recording."""
    valid_card, valid_month, valid_year, valid_pass, valid_cvv2, valid_amount = validate_payment_inputs(card, month, year, password, cvv2, amount)
    transaction = new_transaction(username, "charge", valid_amount, "Wallet top-up")
    try:
        payment_result = API().pay(valid_card, valid_month, valid_year, valid_pass, valid_cvv2, valid_amount)
    except ValueError:
        raise ValueError("Bank rejected the card details.") from None
    if not payment_result:
        raise ValueError("Bank transaction failed.")
    try:
        transaction.attach_receipt(_mask_receipt(valid_card, payment_result))
    except ValueError:
        pass
    for attempt in range(2):
        try:
            record_transaction(transaction)
            break
        except StorageError:
            if attempt == 1:
                reference = transaction.receipt or transaction.tracking_code
                raise StorageError(f"Payment succeeded but could not be recorded. Do not pay again; give this receipt to the manager: {reference}") from None
    return transaction