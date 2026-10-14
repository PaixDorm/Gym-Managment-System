from src.admin.user_manager import load_user, find_username
from src.member.subscription_manager import (
    get_plans,
    get_payments_report,
    get_members_status,
    buy_subscription
)
from src.member.wallet_manager import get_wallet, StorageError
from src.models.wallet import InsufficientBalanceError
from src.utils.helpers import (
    get_valid_choice,
    get_non_empty_input,
    confirm_action
)


def subscription_panel():
    while True:
        print("\n--- مدیریت اشتراک‌ها و پرداخت‌ها ---")
        print("1. وضعیت اشتراک اعضا")
        print("2. مشاهده پرداخت‌های اشتراک")
        print("3. ثبت یا تمدید اشتراک برای عضو")
        print("4. بازگشت")

        choice = get_valid_choice(
            "انتخاب: ", ["1", "2", "3", "4"]
        )

        if choice == "4":
            return

        try:
            if choice == "1":
                members = [
                    user for user in load_user()
                    if user.role == "member"
                ]

                if not members:
                    print("عضوی ثبت نشده است")
                    continue

                usernames = [u.username for u in members]
                statuses = get_members_status(usernames)

                labels = {
                    "active": "فعال",
                    "expired": "منقضی‌شده",
                    "none": "بدون اشتراک"
                }

                for member in members:
                    state = statuses[member.username]
                    print(
                        f"{member.name} ({member.username}): "
                        f"{labels.get(state, state)}"
                    )

            elif choice == "2":
                payments = get_payments_report()

                if not payments:
                    print("پرداخت اشتراکی ثبت نشده است")
                    continue

                names = {
                    user.username: user.name
                    for user in load_user()
                }

                for item in payments:
                    print(
                        f"عضو: {names.get(item['username'], item['username'])}"
                        f" | اشتراک: {item['months']} ماهه"
                        f" | مبلغ: {item['amount']} تومان"
                        f" | تاریخ پرداخت: {item['payment_date']}"
                        f" | شروع: {item['start_date']}"
                        f" | پایان: {item['end_date']}"
                        f" | پیگیری: {item['tracking_code']}"
                    )

            elif choice == "3":
                username = get_non_empty_input("نام کاربری عضو: ")
                user = find_username(username)

                if (
                    user is None
                    or user.role != "member"
                    or not user.is_active
                ):
                    print("عضو معتبر و فعال پیدا نشد")
                    continue

                plans = get_plans()

                for months, plan in sorted(plans.items()):
                    print(f"{months} ماهه: {plan.price} تومان")

                months = int(get_valid_choice(
                    "مدت اشتراک: ",
                    [str(m) for m in plans]
                ))

                price = plans[months].price
                balance = get_wallet(username).balance

                print(f"موجودی عضو: {balance} تومان")
                print(f"مبلغ اشتراک: {price} تومان")

                if not confirm_action(
                    "مبلغ از کیف پول عضو کسر شود؟ (y/n): "
                ):
                    print("عملیات لغو شد")
                    continue

                sub = buy_subscription(username, months)

                print("اشتراک ثبت شد")
                print("تاریخ شروع:", sub.start_date)
                print("تاریخ پایان:", sub.end_date)
                print("شماره پیگیری:", sub.tracking_code)

        except (
            ValueError,
            OSError,
            UnicodeError,
            StorageError,
            InsufficientBalanceError
        ) as error:
            print("خطا در مدیریت اشتراک‌ها:", error)