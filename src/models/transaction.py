from datetime import datetime
import random, re

valid_types = {"charge", "subscription"}
separator = " | "
forbidden_chars = ("|", "\n", "\r")
date_format = "%Y-%m-%d %H:%M:%S"
translations = {"charge":"شارژحساب", "subscription": "خرید اشتراک"}
traking_number_regex = re.compile(r"^TRX-[0-9]{14}-[0-9]{4}$")
amount_regex = re.compile(r"^[0-9]+$")

def generate_tracking_code():
    now = datetime.now()
    strtime = now.strftime("%Y%m%d%H%M%S")
    random_number = random.randint(1000, 9999)
    return f"TRX-{strtime}-{random_number}"

class Transaction:
    # step 3: (__init__) and validations
    def __init__(self, username, transaction_type, amount, description, date=None, tracking_code=None):
        # username validation
        if not isinstance(username, str) or not username.strip():
            raise ValueError("نام کاربری باید یک رشته معتبر و غیرخالی باشد.")
        username = username.strip()
        if any(ch in username for ch in forbidden_chars):
            raise ValueError("نام کاربری نمی‌تواند شامل کاراکتر جداکننده یا کاراکتر خط جدید باشد.")
        # transaction type validation
        if transaction_type not in valid_types:
            raise ValueError(f"نوع تراکنش نامعتبر است. موارد مجاز: {valid_types}")
        # amount validation
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("مبلغ باید یک عدد صحیح و مثبت باشد.")
        # description validation
        if not isinstance(description, str) or not description.strip():
            raise ValueError("توضیحات باید یک رشته معتبر و غیرخالی باشد.")
        description = description.strip()
        if any(ch in description for ch in forbidden_chars):
            raise ValueError("توضیحات نمی‌تواند شامل کاراکتر جداکننده یا کاراکتر خط جدید باشد.")
        # date validation
        if date is None:
            date = datetime.now().replace(microsecond=0)
        elif not isinstance(date, datetime):
            raise ValueError("تاریخ باید از نوع شیء datetime باشد.")
        # tracking number validation
        if tracking_code is None:
            tracking_code = generate_tracking_code()
        else:
            if not isinstance(tracking_code, str) or not traking_number_regex.fullmatch(tracking_code):
                raise ValueError("فرمت شماره پیگیری نامعتبر است.")

        # Attributions
        self.username = username
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.date = date
        self.tracking_code = tracking_code
    # step 4: convert to line
    def to_line(self):
        """تبدیل اطلاعات تراکنش به یک خط متنی جدا شده با جداکننده"""
        parts = [self.tracking_code, self.username, self.transaction_type, str(self.amount), self.date.strftime(date_format), self.description]
        return separator.join(parts)

    # step 5
    @classmethod
    def from_line(cls, line):
        """ساخت شیء تراکنش از روی یک خط متنی ذخیره‌شده"""
        if not isinstance(line, str):
            raise ValueError("خط ورودی باید از نوع رشته باشد.")
        line = line.strip()
        parts = line.split(separator)
        if len(parts) != 6:
            raise ValueError("تعداد اجزای خط نامعتبر است؛ باید دقیقاً ۶ بخش باشد.")
        tracking_code, username, transaction_type, amount_str, date_str, description = parts
        # amount validation before transforming to int
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
        return cls(username=username, transaction_type=transaction_type, amount=amount, description=description, date=date_obj, tracking_code=tracking_code)
    
    # 6: __str__
    def __str__(self):
        persian_type = translations.get(self.transaction_type, self.transaction_type)
        formatted_amount = f"{self.amount:,}"
        formatted_date = self.date.strftime(date_format)
        return f"تراکنش [{self.tracking_code}] | {persian_type} | مبلغ: {formatted_amount} تومان | کاربر: {self.username} | تاریخ: {formatted_date} | توضیحات: {self.description}"