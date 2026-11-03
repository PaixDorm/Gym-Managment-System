
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError


_password_hasher = PasswordHasher(type=Type.ID)


def hash_password(password: str) -> str:
    """Hash a password securely using Argon2id."""

    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    return _password_hasher.hash(password)


def verify_password(password: str, stored_password: str) -> bool:
    """Verify a password against an Argon2id hash."""

    if (
        not isinstance(password, str)
        or not password
        or not isinstance(stored_password, str)
        or not stored_password.startswith("$argon2id$")
    ):
        return False

    try:
        return _password_hasher.verify(stored_password, password)
    except (VerificationError, ValueError, TypeError):
        return False


def needs_rehash(stored_password: str) -> bool:
    """Check whether a stored hash needs updating."""

    if (
        not isinstance(stored_password, str)
        or not stored_password.startswith("$argon2id$")
    ):
        return True

    try:
        return _password_hasher.check_needs_rehash(stored_password)
    except (VerificationError, ValueError, TypeError):
        return True
