from src.admin.user_manager import load_user, save_user
from src.models.user import User
from getpass import getpass
from src.validation.validators import (
    validate_username,
    validate_password,
    validate_email,
    validate_name
)
try:
    users = load_user()
except (OSError, ValueError, UnicodeError) as error:
    print("Error loading users:", error)
    raise SystemExit(1)
manager_username = input("Manager username: ").strip()
username_exists = False
for user in users:
    if user.username == manager_username:
        username_exists = True
        break
manager_exists = False
for user in users:
    if user.role == "manager":
        manager_exists = True
        break
if manager_exists:
    print("A manager account already exists.")
elif username_exists:
    print("This username is already registered.")
else:
    print("You can create a new manager account.")
    manager_name = input("Enter manager's full name: ")
    manager_email = input("Enter manager's email: ")
    manager_password = getpass("Manager password: ")
    has_forbidden_chars = any(
        char in manager_password for char in "\t\n\r"
    )
    print("Name:", validate_name(manager_name))
    print("Username:", validate_username(manager_username))
    print("Email:", validate_email(manager_email))
    print("Password:", validate_password(manager_password))
    print("Forbidden chars:", has_forbidden_chars)
    if (
        validate_name(manager_name)
        and validate_email(manager_email)
        and validate_username(manager_username)
        and validate_password(manager_password)
        and not has_forbidden_chars
    ):
        new_manager = User(
            name=manager_name,
            username=manager_username,
            password=manager_password,
            email=manager_email,
            role="manager",
            is_active=True
        )
        users.append(new_manager)
        try:
            save_user(users)
            saved_users = load_user()
        except (OSError, ValueError, UnicodeError) as error:
            print("Error saving or verifying manager account:", error)
        else:
            if any(
                user.username == manager_username
                and user.role == "manager"
                and user.is_active
                for user in saved_users
            ):
                print("Manager account created successfully.")
            else:
                print("Manager account was not found after saving.")
    else:
        print("Invalid manager information.")
