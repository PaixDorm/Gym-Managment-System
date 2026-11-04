
import re
from uuid import uuid4


class API:
    """Simulated payment provider. No real payments are processed."""

    def validate(self, card, exp_month, exp_year, password, cvv2):
        if not re.fullmatch(r"[0-9]{16}", str(card)):
            return False

        try:
            month = int(exp_month)
            year = int(exp_year)
        except (TypeError, ValueError):
            return False

        if not 1 <= month <= 12:
            return False

        if not 1403 <= year <= 1408:
            return False

        if not re.fullmatch(r"[0-9]{6}", str(password)):
            return False

        if not re.fullmatch(r"[0-9]{3}", str(cvv2)):
            return False

        return True

    def generate_payment_id(self, amount, card):
        """Generate a unique reference without exposing card details."""
        return f"SIM-{uuid4().hex}"

    def pay(self, card, exp_month, exp_year, password, cvv2, amount):
        if not self.validate(
            card, exp_month, exp_year, password, cvv2
        ):
            raise ValueError("Invalid simulated payment details.")

        return self.generate_payment_id(amount, card)
