class InsufficientBalanceError(Exception):
    pass

def _validate_amount(amount):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("Amount must be a positive integer.")

class Wallet:
    def __init__(self, username, balance=0):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username must be a non-empty string.")
        username = username.strip()
        if "|" in username or "\n" in username or "\r" in username:
            raise ValueError("Username cannot contain separators or control characters.")
        if not isinstance(balance, int) or isinstance(balance, bool) or balance < 0:
            raise ValueError("Initial balance must be a non-negative integer.")
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
            raise InsufficientBalanceError(f"Insufficient balance. Current balance: {self.__balance}, requested amount: {amount}")
        self.__balance -= amount
        return self.__balance

    def to_dict(self):
        return {"username": self.username, "balance": self.__balance}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")
        if "username" not in data or "balance" not in data:
            raise ValueError("Input dictionary must contain username and balance keys.")
        return cls(username=data["username"], balance=data["balance"])