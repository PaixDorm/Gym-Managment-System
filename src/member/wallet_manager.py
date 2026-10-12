import os
import re
from src.models.wallet import Wallet
from src.models.transaction import Transaction
from Bank import API

# regex patterns for Bank and amount inputs validation
card_regex = re.compile(r"^\d{16}$")
month_regex = re.compile(r"^(?:0?[1-9]|1[0-2])$")
year_regex = re.compile(r"^\d{4}$")
password_regex = re.compile(r"^\d{6}$")
cvv2_regex = re.compile(r"^\d{3}$")
amount_regex = re.compile(r"^[1-9]\d*$")

# card validation
def validate_card_number(card_input):
    """بررسی و اعتبارسنجی شماره کارت (دقیقاً ۱۶ رقم)"""
    if not isinstance(card_input, str):
        raise ValueError("شماره کارت باید از نوع رشته باشد.")
    card_str = card_input.strip()
    if not card_regex.fullmatch(card_str):
        raise ValueError("شماره کارت باید دقیقاً ۱۶ رقم باشد.")
    return card_str

# expiration month validation (between 1 to 12)
def validate_exp_month(month_input):
    """بررسی و اعتبارسنجی ماه انقضا (بین ۱ تا ۱۲)"""
    if not isinstance(month_input, str):
        raise ValueError("ماه انقضا باید از نوع رشته باشد.")
    month_str = month_input.strip()
    if not month_regex.fullmatch(month_str):
        raise ValueError("ماه انقضا باید عددی بین ۱ تا ۱۲ باشد.")
    return int(month_str)

# expiration year validation (4 digits)
def validate_exp_year(year_input):
    """بررسی و اعتبارسنجی سال انقضا (چهار رقمی)"""
    if not isinstance(year_input, str):
        raise ValueError("سال انقضا باید از نوع رشته باشد.")
    year_str = year_input.strip()
    if not year_regex.fullmatch(year_str):
        raise ValueError("سال انقضا باید یک عدد چهار رقمی معتبر باشد.")
    return int(year_str)

# password validation (6 digits preciselt with 0s included)
def validate_card_password(password_input):
    """بررسی و اعتبارسنجی رمز دوم (دقیقاً ۶ رقم با حفظ صفرهای اولیه)"""
    if not isinstance(password_input, str):
        raise ValueError("رمز دوم باید از نوع رشته باشد.")
    pass_str = password_input.strip()
    if not password_regex.fullmatch(pass_str):
        raise ValueError("رمز دوم باید دقیقاً ۶ رقم باشد.")
    return pass_str

# cvv2 valiidation (precisely 3 digits)
def validate_cvv2(cvv2_input):
    """بررسی و اعتبارسنجی CVV2 (دقیقاً ۳ رقم)"""
    if not isinstance(cvv2_input, str):
        raise ValueError("کد CVV2 باید از نوع رشته باشد.")
    cvv2_str = cvv2_input.strip()
    if not cvv2_regex.fullmatch(cvv2_str):
        raise ValueError("کد CVV2 باید دقیقاً ۳ رقم باشد.")
    return cvv2_str

# amount validation
def validate_amount(amount_input):
    """بررسی و اعتبارسنجی مبلغ تراکنش"""
    if not isinstance(amount_input, str):
        raise ValueError("مبلغ باید از نوع رشته باشد.")
    amount_str = amount_input.strip()
    if not amount_regex.fullmatch(amount_str):
        raise ValueError("مبلغ وارد شده معتبر نیست؛ باید یک عدد صحیح و مثبت باشد.")
    return int(amount_str)

def validate_payment_inputs(card, month, year, password, cvv2, amount):
    """تابع ترکیبی بررسی تمامی فیلدهای پرداخت"""
    valid_card = validate_card_number(card)
    valid_month = validate_exp_month(month)
    valid_year = validate_exp_year(year)
    valid_pass = validate_card_password(password)
    valid_cvv2 = validate_cvv2(cvv2)
    valid_amount = validate_amount(amount)
    return (valid_card, valid_month, valid_year, valid_pass, valid_cvv2, valid_amount)

# Transaction file path constants and settings (using clean, absolute paths)
current_dir = os.path.abspath(os.path.dirname(__file__))
transactions_file_path = os.path.normpath(os.path.join(current_dir, "../../data/transactions.txt"))

class StorageError(Exception):
    """خطای اختصاصی برای مشکلات مربوط به ذخیره‌سازی و خواندن فایل‌ها"""
    pass

# Private file storage and reading functions
def _append_line(line):
    """افزودن یک خط به انتهای فایل تراکنش‌ها با رمزگذاری utf-8"""
    try:
        directory = os.path.dirname(transactions_file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(transactions_file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        raise StorageError("خطا در ذخیره‌سازی اطلاعات روی دیسک.") from None

def _read_lines():
    """خواندن تمام خطوط فایل؛ در صورت عدم وجود فایل، لیست خالی برمی‌گرداند"""
    if not os.path.exists(transactions_file_path):
        return []
    try:
        with open(transactions_file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        raise StorageError("خطا در خواندن فایل از روی دیسک.") from None

# loading transactions with a strict treatment to the corrupt lines
def _load_transactions(strict=False):
    """بارگذاری تمام تراکنش‌های فایل با قابلیت سخت‌گیری در برابر خطوط خراب"""
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
                raise StorageError(f"خطای داده‌های ذخیره‌شده در شماره خط {idx}: فرمت خط نامعتبر است.") from None
            continue
    return transactions

# Calculating user balance based on transactions (with a fix to strip the username)
def get_balance(username):
    """محاسبه موجودی فعلی کاربر از روی تاریخچه تراکنش‌ها (شارژ مثبت، اشتراک منفی)"""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
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
        raise StorageError("موجودی حساب منفی است که نشان‌دهنده ناسازگاری در داده‌های ذخیره‌شده است.")
    return balance

# Creating the wallet object (with the parameter name changed to 'balance')
def get_wallet(username):
    """دریافت شیء کیف پول حاوی موجودی به‌دست‌آمده از تراکنش‌ها"""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
    username = username.strip()
    current_balance = get_balance(username)
    return Wallet(username, balance=current_balance)

# Retrieve transactions for a specific user (with username stripping)
def get_transactions(username):
    """دریافت لیست تراکنش‌های متعلق به کاربر بدون حساسیت به خطوط مخدوش احتمالی دیگر"""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
    username = username.strip()
    all_transactions = _load_transactions(strict=False)
    return [tx for tx in all_transactions if tx.username == username]

# Public transaction record
def record_transaction(transaction):
    """بررسی نوع تراکنش و افزودن آن به فایل"""
    if not isinstance(transaction, Transaction):
        raise ValueError("ورودی باید از نوع شیء Transaction باشد.")
    _append_line(transaction.to_line())

# Wallet Top-up (Order adjusted: Transaction creation prior to bank communication)
def charge_wallet(username, card, month, year, password, cvv2, amount):
    """شارژ کیف پول با اعتبارسنجی ورودی، تراکنش بانکی و ثبت در فایل"""
    # Payment Input Validation
    valid_card, valid_month, valid_year, valid_pass, valid_cvv2, valid_amount = validate_payment_inputs(card, month, year, password, cvv2, amount)
    # Creating a top-up transaction (to verify the username before communicating with the bank)
    transaction = Transaction(username=username, transaction_type="charge", amount=valid_amount, description="شارژ کیف پول")
    # Connection to the bank gateway
    try:
        payment_result = API().pay(valid_card, valid_month, valid_year, valid_pass, valid_cvv2, valid_amount)
    except ValueError:
        raise ValueError("اطلاعات کارت توسط بانک تأیید نشد.") from None
    if not payment_result:
        raise ValueError("تراکنش بانکی ناموفق بود.")
    # Logging the transaction to a file (handling `from None` in case of a disk error)
    try:
        record_transaction(transaction)
    except StorageError:
        raise StorageError("پرداخت انجام شد ولی ثبت نشد، به مدیر اطلاع دهید.") from None
    return transaction