from datetime import datetime
import re, secrets

valid_types = {"charge", "subscription"}
separator = " | "
forbidden_chars = ("|", "\n", "\r")
date_format = "%Y-%m-%d %H:%M:%S"
translations = {"charge": "شارژ حساب", "subscription": "خرید اشتراک"}
traking_number_regex = re.compile(r"^TRX-[0-9]{14}-[0-9]{4,8}$")
amount_regex = re.compile(r"^[0-9]+$")
receipt_regex = re.compile(r"^[0-9]{4}\*{8}[0-9]{4}[0-9]{7,}$")

def generate_tracking_code():
    now = datetime.now()
    strtime = now.strftime("%Y%m%d%H%M%S")
    random_number = f"{secrets.randbelow(10**8):08d}"
    return f"TRX-{strtime}-{random_number}"

def _validate_receipt(receipt):
    """رسید باید None یا رسید ماسک‌ شده باشد (شماره‌ی کامل کارت هرگز ذخیره نمی‌شود)"""
    if receipt is not None and (not isinstance(receipt, str) or not receipt_regex.fullmatch(receipt)):
        raise ValueError("فرمت رسید بانکی نامعتبر است؛ فقط رسید ماسک‌شده پذیرفته می‌شود.")

class Transaction:
    def __init__(self, username, transaction_type, amount, description, date=None, tracking_code=None, receipt=None):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("نام کاربری باید یک رشته معتبر و غیرخالی باشد.")
        username = username.strip()
        if any(ch in username for ch in forbidden_chars):
            raise ValueError("نام کاربری نمی‌تواند شامل کاراکتر | یا کاراکتر خط جدید باشد.")
        if not isinstance(transaction_type, str) or transaction_type not in valid_types:
            raise ValueError(f"نوع تراکنش نامعتبر است. موارد مجاز: {valid_types}")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("مبلغ باید یک عدد صحیح و مثبت باشد.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("توضیحات باید یک رشته معتبر و غیرخالی باشد.")
        description = description.strip()
        if any(ch in description for ch in forbidden_chars):
            raise ValueError("توضیحات نمی‌تواند شامل کاراکتر | یا کاراکتر خط جدید باشد.")
        if date is None:
            date = datetime.now().replace(microsecond=0)
        elif not isinstance(date, datetime):
            raise ValueError("تاریخ باید از نوع شیء datetime باشد.")
        if tracking_code is None:
            tracking_code = generate_tracking_code()
        else:
            if not isinstance(tracking_code, str) or not traking_number_regex.fullmatch(tracking_code):
                raise ValueError("فرمت شماره پیگیری نامعتبر است.")

        _validate_receipt(receipt)

        self.username = username
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.date = date
        self.tracking_code = tracking_code
        self.receipt = receipt

    def attach_receipt(self, receipt):
        """افزودن رسید ماسک‌شده‌ی بانک پس از تأیید پرداخت (با اعتبارسنجی)"""
        _validate_receipt(receipt)
        self.receipt = receipt

    def to_line(self):
        """تبدیل تراکنش به یک خط متنی با ۷ فیلد (فیلد آخر: رسید یا «-» اگر رسیدی نیست)"""
        parts = [self.tracking_code, self.username, self.transaction_type, str(self.amount),
                 self.date.strftime(date_format), self.description, self.receipt or "-"]
        return separator.join(parts)

    @classmethod
    def from_line(cls, line):
        """ساخت تراکنش از یک خط ذخیره‌شده"""
        if not isinstance(line, str):
            raise ValueError("خط ورودی باید از نوع رشته باشد.")
        line = line.strip()
        parts = line.split(separator)
        if len(parts) not in (6, 7):
            raise ValueError("تعداد اجزای خط نامعتبر است؛ باید ۶ یا ۷ بخش باشد.")
        tracking_code, username, transaction_type, amount_str, date_str, description = parts[:6]
        receipt = parts[6] if len(parts) == 7 and parts[6] != "-" else None
        if not amount_regex.fullmatch(amount_str):
            raise ValueError("مبلغ موجود در خط ورودی معتبر نیست.")
        try:
            amount = int(amount_str)
        except ValueError:
            raise ValueError("مبلغ موجود در خط ورودی معتبر نیست.") from None
        try:
            date_obj = datetime.strptime(date_str, date_format)
        except ValueError:
            raise ValueError("فرمت تاریخ موجود در خط ورودی نامعتبر است.") from None
        return cls(username=username, transaction_type=transaction_type, amount=amount, description=description,
                   date=date_obj, tracking_code=tracking_code, receipt=receipt)

    def __str__(self):
        persian_type = translations.get(self.transaction_type, self.transaction_type)
        formatted_amount = f"{self.amount:,}"
        formatted_date = self.date.strftime(date_format)
        text = (f"تراکنش [{self.tracking_code}] | {persian_type} | مبلغ: {formatted_amount} تومان | "
                f"کاربر: {self.username} | تاریخ: {formatted_date} | توضیحات: {self.description}")
        if self.receipt:
            text += f" | رسید بانک: {self.receipt}"
        return text