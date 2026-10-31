from datetime import date, timedelta
from src.models.transaction import traking_number_regex

valid_months = {1, 3, 6}
days_per_month = 30
month_to_persian = {1: "یک‌ماهه", 3: "سه‌ماهه", 6: "شش‌ماهه"}  # Legacy labels for compatibility.
month_to_english = {1: "1-month", 3: "3-month", 6: "6-month"}

class SubscriptionPlan:
    def __init__(self, months, price):
        if not isinstance(months, int) or isinstance(months, bool) or months not in valid_months:
            raise ValueError(f"Subscription duration must be one of {valid_months} months.")
        if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
            raise ValueError("Subscription plan price must be a positive integer.")
        self.months = months
        self.price = price

    @property
    def duration_days(self):
        return self.months * days_per_month

    @property
    def title(self):
        return month_to_english.get(self.months, "")

    def to_dict(self):
        return {"months": self.months, "price": self.price}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")
        if "months" not in data or "price" not in data:
            raise ValueError("Input dictionary must contain months and price keys.")
        return cls(months=data["months"], price=data["price"])

class Subscription:
    def __init__(self, username, months, amount, start_date, tracking_code, payment_date=None):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username must be a non-empty string.")
        username = username.strip()
        if "|" in username or "\n" in username or "\r" in username:
            raise ValueError("Username cannot contain separators or control characters.")
        if not isinstance(months, int) or isinstance(months, bool) or months not in valid_months:
            raise ValueError(f"Subscription duration must be one of {valid_months} months.")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("Amount must be a positive integer.")
        if type(start_date) is not date:
            raise ValueError("Start date must be a date object.")
        if payment_date is None:
            payment_date = date.today()
        elif type(payment_date) is not date:
            raise ValueError("Payment date must be a date object.")
        if not isinstance(tracking_code, str) or not traking_number_regex.fullmatch(tracking_code):
            raise ValueError("Invalid tracking code format.")

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
            raise ValueError("Today must be a date object.")
        return self.start_date <= today < self.end_date

    def days_left(self, today=None):
        if today is None:
            today = date.today()
        elif type(today) is not date:
            raise ValueError("Today must be a date object.")
        if not self.is_active(today):
            return 0
        delta = self.end_date - today
        return max(0, delta.days)

    def to_dict(self):
        """Convert subscription to a dictionary with ISO-formatted dates."""
        return {"username": self.username, "months": self.months, "amount": self.amount, "start_date": self.start_date.isoformat(), "tracking_code": self.tracking_code, "payment_date": self.payment_date.isoformat()}

    def to_line(self):
        """Serialize subscription as a delimited line, excluding the end date."""
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
        """Parse a subscription from a stored line."""
        if not isinstance(line, str):
            raise ValueError("Input line must be a string.")
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
                raise ValueError("Invalid numeric or date fields in subscription record.") from None
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
                raise ValueError("Invalid numeric or date fields in subscription record.") from None
            expected_end_date = start_date_obj + timedelta(days=months * days_per_month)
            if end_date_obj != expected_end_date:
                raise ValueError("Stored end date does not match subscription duration.")
            return cls(
                username=username,
                months=months,
                amount=amount,
                start_date=start_date_obj,
                tracking_code=tracking_code,
                payment_date=payment_date_obj)
        else:
            raise ValueError("Invalid subscription record: expected 6 or 7 fields.")

def next_start_date(latest_subscription, today=None):
    """Determine the start date for a renewed subscription."""
    if today is None:
        today = date.today()
    elif type(today) is not date:
        raise ValueError("Today must be a date object.")
    if latest_subscription is None:
        return today
    if latest_subscription.is_active(today) or latest_subscription.start_date > today:
        return latest_subscription.end_date
    return today