class InsufficientBalanceError(Exception):
    pass

def _validate_amount(amount):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("مبلغ باید یک عدد صحیح و مثبت باشد.")

class Wallet:
    def __init__(self, username, balance=0):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("نام کاربری باید یک رشته معتبر و غیرخالی باشد.")
        username = username.strip()
        if "|" in username or "\n" in username or "\r" in username:
            raise ValueError("نام کاربری نمی‌تواند شامل جداکننده یا کاراکترهای کنترلی باشد.")
        if not isinstance(balance, int) or isinstance(balance, bool) or balance < 0:
            raise ValueError("موجودی اولیه باید یک عدد صحیح و نامنفی باشد.")
        self.username = username
        self.__balance = balance

    @property
    def balance(self):
        return self.__balance

    def has_enough(self, amount):
        _validate_amount(amount)
        return self.__balance >= amount

    def deposit(self, amount):
        _validate_amount(amount)
        self.__balance += amount
        return self.__balance

    def withdraw(self, amount):
        _validate_amount(amount)
        if not self.has_enough(amount):
            raise InsufficientBalanceError(f"موجودی ناکافی. موجودی فعلی: {self.__balance}, مبلغ درخواستی: {amount}")
        self.__balance -= amount
        return self.__balance

    def to_dict(self):
        return {"username": self.username, "balance": self.__balance}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("داده ورودی باید از نوع دیکشنری باشد.")
        if "username" not in data or "balance" not in data:
            raise ValueError("دیکشنری ورودی باید دارای کلیدهای username و balance باشد.")
        return cls(username=data["username"], balance=data["balance"])