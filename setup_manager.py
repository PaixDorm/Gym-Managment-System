from src.admin.user_manager import load_user, save_user
from src.models.user import User
from getpass import getpass
from src.validation.validators import validate_username,validate_password,validate_email,validate_name
try:
    users = load_user()
except (OSError, ValueError, UnicodeError) as error:
    print("خطا در خواندن کاربران:", error)
    raise SystemExit(1)
manager_username = input("نام کاربری مدیر : ").strip()
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
    print("حساب مدیر از قبل وجود دارد")
elif username_exists:
    print("این نام کاربری قبلاً ثبت شده است")
else:
    print("امکان ساخت مدیر جدید وجود دارد")
    manager_name = input("نام مورد نظر را وارد کنید")
    manager_email = input("ایمیل را وارد کنید")
    manager_password = getpass("رمز عبور مدیر : ")
    has_forbidden_chars = any(char in manager_password for char in "\t\n\r")
    print("Name:", validate_name(manager_name))
    print("Username:", validate_username(manager_username))
    print("Email:", validate_email(manager_email))
    print("Password:", validate_password(manager_password))
    print("Forbidden chars:", has_forbidden_chars)
    if validate_name(manager_name) and validate_email(manager_email) and validate_username(manager_username) and validate_password(manager_password) and not has_forbidden_chars:
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
            print("خطا در ذخیره یا بررسی حساب مدیر:", error)
        else:
            if any(user.username == manager_username and user.role == "manager" and user.is_active
                   for user in saved_users):
                print("مدیر با موفقیت اضافه شد")
            else:
                print("حساب مدیر پس از ذخیره پیدا نشد")

    else:
        print("اطلاعات مدیر نامعتبر است")
