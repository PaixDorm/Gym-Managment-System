from src.admin.user_manager import (
    add_user,
    edit_user,
    toggle_active,
    view_user,
    load_user
)
from getpass import getpass
from src.utils.helpers import get_valid_choice,get_non_empty_input,confirm_action
from src.admin.hall_panel import hall_panel
from src.admin.class_panel import class_panel
from src.member.subscription_manager import get_revenue_by_type
def admin_panel(username, hall_manager, class_manager):
    while True :
        print("1.افزودن")
        print("2.نمایش")
        print("3.ویرایش")
        print("4.فعال/غیر فعال کردن")
        print("5.خروج")
        print("6.مدیریت سالن‌ها")
        print("7.مدیریت کلاس‌ها")
        print("8. گزارش درآمد اشتراک‌ها")
        print("9. گزارش آماری باشگاه")
        choice = get_valid_choice("عدد مورد نظر را وارد کنید : ",["1","2","3","4","5","6","7","8","9"])
        if choice == "1":
            name = get_non_empty_input("نام و نام خانوادگی: ")
            new_username = get_non_empty_input("نام کاربری: ")
            email = get_non_empty_input("ایمیل: ")
            password = getpass("رمز عبور: ")
            if any(c in password for c in "\t\n\r"):
                print("رمز عبور شامل کاراکتر غیرمجاز است")
                continue

            role = get_valid_choice(
                "نقش کاربر (coach/member): ",
                ["coach", "member"]
            )

            try:
                add_user(name, new_username, password, email, role)
            except (OSError, ValueError, UnicodeError) as error:
                print("خطا در افزودن کاربر:", error)
        elif choice == "2":
            try:
                view_user()
            except (OSError, UnicodeError) as error:
                print("خطا در نمایش کاربران:", error)
        elif choice == "3":
            target_username = get_non_empty_input("نام کاربری موردنظر: ")
            print("1. تغییر نام")
            print("2. تغییر ایمیل")
            print("3. تغییر رمز عبور")
            edit_choice = get_valid_choice(
                "گزینه ویرایش: ",
                ["1", "2", "3"]
            )
            try:
                if edit_choice == "1":
                    new_name = get_non_empty_input("نام جدید: ")
                    edit_user(target_username, new_name=new_name)

                elif edit_choice == "2":
                    new_email = get_non_empty_input("ایمیل جدید: ")
                    edit_user(target_username, new_email=new_email)

                elif edit_choice == "3":
                    new_password = getpass("رمز جدید: ")

                    if any(c in new_password for c in "\t\n\r"):
                        print("رمز شامل کاراکتر غیرمجاز است")
                    else:
                        edit_user(target_username, new_password=new_password)

            except (OSError, ValueError, UnicodeError) as error:
                print("خطا در ویرایش کاربر:", error)
        elif choice == "4":
            target_username = get_non_empty_input("نام کاربری موردنظر: ")

            if target_username == username:
                print("نمی‌توانید حساب مدیر خودتان را غیرفعال کنید")

            elif confirm_action("تغییر وضعیت کاربر؟ (y/n): "):
                try:
                    toggle_active(target_username)
                except (OSError, ValueError, UnicodeError) as error:
                    print("خطا در تغییر وضعیت:", error)
            else:
                print("عملیات لغو شد")
        elif choice == "5":
            break
        elif choice == "6":
            hall_panel(hall_manager)
        elif choice == "7":
            class_panel(class_manager)
        elif choice == "8":
            try:
                revenues = get_revenue_by_type()

                if not revenues:
                    print("هنوز درآمد اشتراکی ثبت نشده")
                else:
                    print("\n--- گزارش درآمد اشتراک‌ها ---")

                    for months, amount in sorted(revenues.items()):
                        print(f"اشتراک {months} ماهه: {amount} تومان")

                    print("درآمد کل:", sum(revenues.values()), "تومان")

            except (OSError, ValueError, UnicodeError) as error:
                print("خطا در دریافت گزارش:", error)
        elif choice == "9":
            try:
                users = load_user()

                active_members = sum(
                    1 for user in users
                    if user.role == "member"
                    and user.is_active is True
                )

                active_coaches = sum(
                    1 for user in users
                    if user.role == "coach"
                    and user.is_active is True
                )

                classes = class_manager.view_classes()

                active_classes = sum(
                    1 for gym_class in classes.values()
                    if gym_class.status is True
                )

                print("\n--- گزارش آماری باشگاه ---")
                print("اعضای فعال:", active_members)
                print("مربیان فعال:", active_coaches)
                print("کلاس‌های فعال:", active_classes)

            except (OSError, ValueError, UnicodeError) as error:
                print("خطا در دریافت گزارش:", error)
