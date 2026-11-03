
import pytest

from src.auth.password_security import (
    hash_password,
    verify_password,
    needs_rehash,
)


def test_password_hashing():
    password = "Example@12345"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2id$")


def test_random_salt():
    password = "Example@12345"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2


def test_correct_password():
    password = "Example@12345"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_incorrect_password():
    hashed = hash_password("Example@12345")

    assert verify_password("Wrong@12345", hashed) is False


def test_plaintext_password_rejected():
    assert verify_password(
        "Example@12345",
        "Example@12345"
    ) is False


def test_persian_plaintext_password_rejected():
    password = "رمزTest@123"

    assert verify_password(password, password) is False

def test_rehash_detection():
    hashed = hash_password("Example@12345")

    assert needs_rehash(hashed) is False
    assert needs_rehash("Example@12345") is True


def test_empty_password_rejected():
    with pytest.raises(ValueError):
        hash_password("")
