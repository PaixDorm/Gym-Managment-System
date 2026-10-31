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
        print("\n--- Subscription and Payment Management ---")
        print("1. View member subscription statuses")
        print("2. View subscription payments")
        print("3. Purchase or renew a member subscription")
        print("4. Back")

        choice = get_valid_choice(
            "Choose an option: ", ["1", "2", "3", "4"]
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
                    print("No members have been registered.")
                    continue

                usernames = [u.username for u in members]
                statuses = get_members_status(usernames)

                labels = {
                    "active": "Active",
                    "expired": "Expired",
                    "none": "No subscription"
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
                    print("No subscription payments have been recorded.")
                    continue

                names = {
                    user.username: user.name
                    for user in load_user()
                }

                for item in payments:
                    print(
                        f"Member: {names.get(item['username'], item['username'])}"
                        f" | Subscription: {item['months']} months"
                        f" | Amount: {item['amount']} Toman"
                        f" | Payment date: {item['payment_date']}"
                        f" | Start: {item['start_date']}"
                        f" | End: {item['end_date']}"
                        f" | Tracking code: {item['tracking_code']}"
                    )

            elif choice == "3":
                username = get_non_empty_input("Member username: ")
                user = find_username(username)

                if (
                    user is None
                    or user.role != "member"
                    or not user.is_active
                ):
                    print("No valid active member was found.")
                    continue

                plans = get_plans()

                for months, plan in sorted(plans.items()):
                    print(f"{months} months: {plan.price} Toman")

                months = int(get_valid_choice(
                    "Subscription duration: ",
                    [str(m) for m in plans]
                ))

                price = plans[months].price
                balance = get_wallet(username).balance

                print(f"Member balance: {balance} Toman")
                print(f"Subscription price: {price} Toman")

                if not confirm_action(
                    "Deduct the amount from the member's wallet? (y/n): "
                ):
                    print("Operation cancelled.")
                    continue

                sub = buy_subscription(username, months)

                print("Subscription recorded successfully.")
                print("Start date:", sub.start_date)
                print("End date:", sub.end_date)
                print("Tracking code:", sub.tracking_code)

        except (
            ValueError,
            OSError,
            UnicodeError,
            StorageError,
            InsufficientBalanceError
        ) as error:
            print("Subscription management error:", error)