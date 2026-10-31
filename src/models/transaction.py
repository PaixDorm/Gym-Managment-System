from datetime import datetime
import re, secrets

valid_types = {"charge", "subscription"}
separator = " | "
forbidden_chars = ("|", "\n", "\r")
date_format = "%Y-%m-%d %H:%M:%S"
translations = {"charge": "Wallet top-up", "subscription": "Subscription purchase"}
traking_number_regex = re.compile(r"^TRX-[0-9]{14}-[0-9]{4,8}$")
amount_regex = re.compile(r"^[0-9]+$")
receipt_regex = re.compile(r"^[0-9]{4}\*{8}[0-9]{4}[0-9]{7,}$")

def generate_tracking_code():
    now = datetime.now()
    strtime = now.strftime("%Y%m%d%H%M%S")
    random_number = f"{secrets.randbelow(10**8):08d}"
    return f"TRX-{strtime}-{random_number}"

def _validate_receipt(receipt):
    """Require a masked receipt or None; never store a full card number."""
    if receipt is not None and (not isinstance(receipt, str) or not receipt_regex.fullmatch(receipt)):
        raise ValueError("Invalid bank receipt format; only masked receipts are accepted.")

class Transaction:
    def __init__(self, username, transaction_type, amount, description, date=None, tracking_code=None, receipt=None):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username must be a non-empty string.")
        username = username.strip()
        if any(ch in username for ch in forbidden_chars):
            raise ValueError("Username cannot contain '|' or newline characters.")
        if not isinstance(transaction_type, str) or transaction_type not in valid_types:
            raise ValueError(f"Invalid transaction type. Allowed types: {valid_types}")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("Amount must be a positive integer.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Description must be a non-empty string.")
        description = description.strip()
        if any(ch in description for ch in forbidden_chars):
            raise ValueError("Description cannot contain '|' or newline characters.")
        if date is None:
            date = datetime.now().replace(microsecond=0)
        elif not isinstance(date, datetime):
            raise ValueError("Date must be a datetime object.")
        if tracking_code is None:
            tracking_code = generate_tracking_code()
        else:
            if not isinstance(tracking_code, str) or not traking_number_regex.fullmatch(tracking_code):
                raise ValueError("Invalid tracking code format.")

        _validate_receipt(receipt)

        self.username = username
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.date = date
        self.tracking_code = tracking_code
        self.receipt = receipt

    def attach_receipt(self, receipt):
        """Validate and attach the masked receipt after bank approval."""
        _validate_receipt(receipt)
        self.receipt = receipt

    def to_line(self):
        """Serialize as seven fields; the last is the receipt or a dash."""
        parts = [self.tracking_code, self.username, self.transaction_type, str(self.amount),
                 self.date.strftime(date_format), self.description, self.receipt or "-"]
        return separator.join(parts)

    @classmethod
    def from_line(cls, line):
        """Parse a transaction from a stored line."""
        if not isinstance(line, str):
            raise ValueError("Input line must be a string.")
        line = line.strip()
        parts = line.split(separator)
        if len(parts) not in (6, 7):
            raise ValueError("Invalid transaction record: expected 6 or 7 fields.")
        tracking_code, username, transaction_type, amount_str, date_str, description = parts[:6]
        receipt = parts[6] if len(parts) == 7 and parts[6] != "-" else None
        if not amount_regex.fullmatch(amount_str):
            raise ValueError("Invalid amount in transaction record.")
        try:
            amount = int(amount_str)
        except ValueError:
            raise ValueError("Invalid amount in transaction record.") from None
        try:
            date_obj = datetime.strptime(date_str, date_format)
        except ValueError:
            raise ValueError("Invalid date format in transaction record.") from None
        return cls(username=username, transaction_type=transaction_type, amount=amount, description=description,
                   date=date_obj, tracking_code=tracking_code, receipt=receipt)

    def __str__(self):
        persian_type = translations.get(self.transaction_type, self.transaction_type)
        formatted_amount = f"{self.amount:,}"
        formatted_date = self.date.strftime(date_format)
        text = (f"Transaction [{self.tracking_code}] | {persian_type} | Amount: {formatted_amount} Toman | "
                f"User: {self.username} | Date: {formatted_date} | Description: {self.description}")
        if self.receipt:
            text += f" | Bank receipt: {self.receipt}"
        return text