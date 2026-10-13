from datetime import date, timedelta
from src.models.transaction import traking_number_regex

valid_months = {1, 3, 6}
days_per_month = 30
month_to_persian = {1: "یک‌ماهه", 3: "سه‌ماهه", 6: "شش‌ماهه"}

class SubscriptionPlan:
    def __init__(self, months, price):        
        if not isinstance(months, int) or isinstance(months, bool) or months not in valid_months:
            raise ValueError(f"مدت ماه اشتراک باید یکی از مقادیر مجاز {valid_months} باشد.")        
        if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
            raise ValueError("قیمت طرح اشتراک باید یک عدد صحیح و مثبت باشد.")
        self.months = months
        self.price = price
    
    @property
    def duration_days(self):
        return self.months * days_per_month
    
    @property
    def title(self):
        return month_to_persian.get(self.months, "")
    
    def to_dict(self):
        return {"months": self.months, "price": self.price}
    
    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("داده ورودی باید از نوع دیکشنری باشد.")
        if "months" not in data or "price" not in data:
            raise ValueError("دیکشنری ورودی باید دارای کلیدهای months و price باشد.")
        return cls(months=data["months"], price=data["price"])

class Subscription:
    def __init__(self, username, months, amount, start_date, tracking_code, payment_date=None):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("نام کاربری باید یک رشته معتبر و غیرخالی باشد.")
        username = username.strip()
        if "|" in username or "\n" in username or "\r" in username:
            raise ValueError("نام کاربری نمی‌تواند شامل جداکننده یا کاراکترهای کنترلی باشد.")
        if not isinstance(months, int) or isinstance(months, bool) or months not in valid_months:
            raise ValueError(f"مدت ماه اشتراک باید یکی از مقادیر مجاز {valid_months} باشد.")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("مبلغ باید یک عدد صحیح و مثبت باشد.")
        if type(start_date) is not date:
            raise ValueError("تاریخ شروع باید از نوع date باشد.")
        if payment_date is None:
            payment_date = date.today()
        elif type(payment_date) is not date:
            raise ValueError("تاریخ پرداخت باید از نوع date باشد.")
        if not isinstance(tracking_code, str) or not traking_number_regex.fullmatch(tracking_code):
            raise ValueError("فرمت شماره پیگیری نامعتبر است.")
        
        self.username = username
        self.months = months
        self.amount = amount
        self.start_date = start_date
        self.tracking_code = tracking_code
        self.payment_date = payment_date
    
    @property
    def end_date(self): 
        return self.start_date + timedelta(days=self.months * days_per_month)
    
    def is_active(self, today=None):
        if today is None:
            today = date.today()
        elif type(today) is not date:
            raise ValueError("تاریخ امروز باید از نوع date باشد.")
        return self.start_date <= today < self.end_date
    
    def days_left(self, today=None):
        if today is None:
            today = date.today()
        elif type(today) is not date:
            raise ValueError("تاریخ امروز باید از نوع date باشد.")
        if not self.is_active(today):
            return 0        
        delta = self.end_date - today
        return max(0, delta.days)
    
    def to_dict(self):
        """تبدیل اشتراک به دیکشنری با تبدیل تاریخ‌ها به رشته‌های ISO"""
        return {"username": self.username, "months": self.months, "amount": self.amount, "start_date": self.start_date.isoformat(), "tracking_code": self.tracking_code, "payment_date": self.payment_date.isoformat()}
        
    def to_line(self):
        """تبدیل اطلاعات اشتراک به یک خط متنی جدا شده با جداکننده (بدون ذخیره تاریخ پایان)"""
        parts = [
            self.tracking_code,
            self.username,
            str(self.months),
            str(self.amount),
            self.start_date.isoformat(),
            self.end_date.isoformat(),
            self.payment_date.isoformat()
        ]
        return " | ".join(parts)
    
    @classmethod
    def from_line(cls, line):
        """ساخت شیء اشتراک از روی یک خط متنی"""
        if not isinstance(line, str):
            raise ValueError("خط ورودی باید از نوع رشته باشد.")
        line = line.strip()
        parts = [part.strip() for part in line.split("|")]
        if len(parts) == 6:
            tracking_code, username, months_str, amount_str, start_date_str, payment_date_str = parts
            try:
                months = int(months_str)
                amount = int(amount_str)
                start_date_obj = date.fromisoformat(start_date_str)
                payment_date_obj = date.fromisoformat(payment_date_str)
            except (ValueError, TypeError):
                raise ValueError("مقادیر عددی یا تاریخ در خط ورودی اشتراک نامعتبر است.") from None
            return cls(
                username=username,
                months=months,
                amount=amount,
                start_date=start_date_obj,
                tracking_code=tracking_code,
                payment_date=payment_date_obj)
        elif len(parts) == 7:
            tracking_code, username, months_str, amount_str, start_date_str, end_date_str, payment_date_str = parts
            try:
                months = int(months_str)
                amount = int(amount_str)
                start_date_obj = date.fromisoformat(start_date_str)
                end_date_obj = date.fromisoformat(end_date_str)
                payment_date_obj = date.fromisoformat(payment_date_str)
            except (ValueError, TypeError):
                raise ValueError("مقادیر عددی یا تاریخ در خط ورودی اشتراک نامعتبر است.") from None
            expected_end_date = start_date_obj + timedelta(days=months * days_per_month)
            if end_date_obj != expected_end_date:
                raise ValueError("تاریخ پایان ثبت‌شده در فایل با مدت‌زمان اشتراک مغایرت دارد.")
            return cls(
                username=username,
                months=months,
                amount=amount,
                start_date=start_date_obj,
                tracking_code=tracking_code,
                payment_date=payment_date_obj)
        else:
            raise ValueError("تعداد اجزای خط اشتراک نامعتبر است؛ باید ۶ یا ۷ بخش باشد.")
        
def next_start_date(latest_subscription, today=None):
    """محاسبه تاریخ شروع اشتراک جدید برای تمدید"""
    if today is None:
        today = date.today()
    elif type(today) is not date:
        raise ValueError("تاریخ امروز باید از نوع date باشد.")
    if latest_subscription is None:
        return today
    if latest_subscription.is_active(today) or latest_subscription.start_date > today:
        return latest_subscription.end_date
    return today