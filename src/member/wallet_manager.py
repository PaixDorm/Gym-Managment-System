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
    """بررسی و اعتبارسنجی شماره کارت (دقیقاً ۱۶ رقم)"""
    if not isinstance(card_input, str):
        raise ValueError("شماره کارت باید از نوع رشته باشد.")
    card_str = card_input.strip()
    if not card_regex.fullmatch(card_str):
        raise ValueError("شماره کارت باید دقیقاً ۱۶ رقم باشد.")
    return card_str

def validate_exp_month(month_input):
    """بررسی و اعتبارسنجی ماه انقضا (بین ۱ تا ۱۲)"""
    if not isinstance(month_input, str):
        raise ValueError("ماه انقضا باید از نوع رشته باشد.")
    month_str = month_input.strip()
    if not month_regex.fullmatch(month_str):
        raise ValueError("ماه انقضا باید عددی بین ۱ تا ۱۲ باشد.")
    return int(month_str)

def validate_exp_year(year_input):
    """بررسی و اعتبارسنجی سال انقضا (چهار رقمی)"""
    if not isinstance(year_input, str):
        raise ValueError("سال انقضا باید از نوع رشته باشد.")
    year_str = year_input.strip()
    if not year_regex.fullmatch(year_str):
        raise ValueError("سال انقضا باید یک عدد چهار رقمی معتبر باشد.")
    return int(year_str)

def validate_card_password(password_input):
    """بررسی و اعتبارسنجی رمز دوم (دقیقاً ۶ رقم با حفظ صفرهای اولیه)"""
    if not isinstance(password_input, str):
        raise ValueError("رمز دوم باید از نوع رشته باشد.")
    pass_str = password_input.strip()
    if not password_regex.fullmatch(pass_str):
        raise ValueError("رمز دوم باید دقیقاً ۶ رقم باشد.")
    return pass_str

def validate_cvv2(cvv2_input):
    """بررسی و اعتبارسنجی CVV2 (دقیقاً ۳ رقم)"""
    if not isinstance(cvv2_input, str):
        raise ValueError("کد CVV2 باید از نوع رشته باشد.")
    cvv2_str = cvv2_input.strip()
    if not cvv2_regex.fullmatch(cvv2_str):
        raise ValueError("کد CVV2 باید دقیقاً ۳ رقم باشد.")
    return cvv2_str

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

current_dir = os.path.abspath(os.path.dirname(__file__))
transactions_file_path = os.path.normpath(os.path.join(current_dir, "../../data/transactions.txt"))

class StorageError(Exception):
    """خطای اختصاصی برای مشکلات مربوط به ذخیره‌سازی و خواندن فایل‌ها"""
    pass

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

def get_all_transactions(strict=False):
    """دریافت همه‌ی تراکنش‌ها (برای گزارش‌ها و تطبیق اشتراک‌ها)"""
    return _load_transactions(strict=strict)

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

def get_wallet(username):
    """دریافت شیء کیف پول حاوی موجودی به‌دست‌آمده از تراکنش‌ها"""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
    username = username.strip()
    current_balance = get_balance(username)
    return Wallet(username, balance=current_balance)

def get_transactions(username):
    """دریافت لیست تراکنش‌های متعلق به کاربر بدون حساسیت به خطوط مخدوش احتمالی دیگر"""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
    username = username.strip()
    all_transactions = _load_transactions(strict=False)
    return [tx for tx in all_transactions if tx.username == username]

def record_transaction(transaction):
    """بررسی نوع تراکنش و افزودن آن به فایل با جلوگیری از ثبت تکراری"""
    if not isinstance(transaction, Transaction):
        raise ValueError("ورودی باید از نوع شیء Transaction باشد.")
    existing_transactions = _load_transactions(strict=False)
    if any(tx.tracking_code == transaction.tracking_code for tx in existing_transactions):
        return
    _append_line(transaction.to_line())

def _mask_receipt(card, payment_id):
    """رسید ماسک‌شده: ۴ رقم اول کارت، ۸ ستاره، ۴ رقم آخر، سپس بقیه‌ی شناسه (مبلغ و عدد تصادفی)"""
    if not (isinstance(card, str) and isinstance(payment_id, str)
            and len(card) == 16 and payment_id.startswith(card) and len(payment_id) > 16):
        raise ValueError("رسید بانکی قابل ماسک‌ شدن نیست.")
    return card[:4] + "*" * 8 + card[-4:] + payment_id[16:]
 
def new_transaction(username, transaction_type, amount, description, when=None):
    """ساخت تراکنش با شماره پیگیری یکتا (غیرتکراری نسبت به تراکنش‌های موجود)"""
    existing_codes = {tx.tracking_code for tx in _load_transactions(strict=True)}
    for _ in range(10):
        code = generate_tracking_code()
        if code not in existing_codes:
            return Transaction(username=username, transaction_type=transaction_type, amount=amount,
                               description=description, date=when, tracking_code=code)
    raise StorageError("ساخت شماره پیگیری یکتا ممکن نشد.")

def charge_wallet(username, card, month, year, password, cvv2, amount):
    """شارژ کیف پول با اعتبارسنجی ورودی، تراکنش بانکی و ثبت در فایل"""
    valid_card, valid_month, valid_year, valid_pass, valid_cvv2, valid_amount = validate_payment_inputs(card, month, year, password, cvv2, amount)
    transaction = new_transaction(username, "charge", valid_amount, "شارژ کیف پول")
    try:
        payment_result = API().pay(valid_card, valid_month, valid_year, valid_pass, valid_cvv2, valid_amount)
    except ValueError:
        raise ValueError("اطلاعات کارت توسط بانک تأیید نشد.") from None
    if not payment_result:
        raise ValueError("تراکنش بانکی ناموفق بود.")
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
                raise StorageError(f"پرداخت انجام شد ولی ثبت نشد. دوباره پرداخت نکنید و این رسید را به مدیر اعلام کنید: {reference}") from None
    return transaction