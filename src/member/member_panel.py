from src.models.file_helper import read_lines
from src.member.enrollment_manager import EnrollmentManager
from src.coach.workout_manager import WorkoutManager
from src.admin.user_manager import find_username
from src.member.subscription_manager import (
    has_active_subscription,
    get_subscription_state,
    get_current_subscription,
    get_days_left,
    get_plans,
    buy_subscription
)
from src.member.wallet_manager import (
    get_wallet,
    get_transactions,
    charge_wallet,
    StorageError
)
from src.models.wallet import InsufficientBalanceError
CLASSES_FILE = "classes.txt"

def get_all_classes():
    result = []
    enrollmentmanager = EnrollmentManager()

    for information in read_lines(CLASSES_FILE):
        information = information.split(" | ")

        if len(information) != 9:
            raise ValueError("Invalid class data format.")

        cls = {
            "id": information[0],
            "title": information[1],
            "sport": information[2],
            "coach": information[3],
            "hall": information[4],
            "day": information[5],
            "time": information[6],
            "capacity": int(information[7]),
            "status": information[8],
            "enrolled": enrollmentmanager.get_active_members(information[0])
            }
        result.append(cls)

    return result

def get_class_by_id(class_id):
    for cls in get_all_classes():
        if str(cls["id"]) == str(class_id):
            return cls
        
    return None

class MemberPanel:
    def __init__(self, username):
        self.username = username
        self.enrollments = EnrollmentManager()
        self.workouts = WorkoutManager()

    def runner(self):
        while True:
            print("\n===== Member Panel =====")
            print("1. My profile and subscription status")
            print("2. My wallet")
            print("3. Available classes")
            print("4. My classes")
            print("5. My workout plan")
            print("6. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.my_profile_and_subscription_status()
            elif choice == "2":
                self.my_wallet()
            elif choice == "3":
                self.view_available_classes()
            elif choice == "4":
                self.my_classes()
            elif choice == "5":
                self.my_workout()
            elif choice == "6":
                return
            else:
                print("Invalid option.")

    def my_profile_and_subscription_status(self):
        user = find_username(self.username)
        user_subscription_state = get_subscription_state(self.username)
        user_subscription = get_current_subscription(self.username)

        if user is None:
            print("User not found.")
            return

        print(f"Name: {user.name}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Account active: {user.is_active}")
        if user_subscription_state == "none" or user_subscription is None:
            print("No subscription")
        else:
            print(f"Subscription duration: {user_subscription.months} months")
            print(f"Subscription start date: {user_subscription.start_date}")
            print(f"Subscription end date: {user_subscription.end_date}")
            if user_subscription_state == "active":
                print(f"Days remaining: {get_days_left(self.username)}")
            print(f"Subscription status: {user_subscription_state}")

    def see_my_wallet(self):
        wallet = get_wallet(self.username)
        print(f"Balance: {wallet.balance}")

    def charge_my_wallet(self):
        my_card = input("Card number (16 digits): ").strip()
        my_card_month = input("Card expiration month (1-12): ").strip()
        my_card_year = input("Card expiration year (4 digits): ").strip()
        my_card_password = input("Card payment password (6 digits): ").strip()
        my_card_cvv2 = input("Card CVV2 (3 digits): ").strip()
        my_amount = input("Amount to add (positive integer, Toman): ").strip()

        charge_wallet(self.username, my_card, my_card_month, my_card_year, my_card_password, my_card_cvv2, my_amount)

    def see_my_transactions(self):
        transactions = get_transactions(self.username)

        if not transactions:
            print("No transactions found.")
            return

        for transaction in transactions:
            print(f"{transaction.transaction_type} | {transaction.amount} | {transaction.date} | {transaction.tracking_code}")

    def buy_or_renewal_my_subscription(self):
        for months, plan in get_plans().items():
            print(f"{months} months - {plan.price:,} Toman")

        choice = input("Subscription duration (1, 3, or 6 months): ").strip()
        if choice not in ("1", "3", "6"):
            print("Invalid option.")
            return
        buy_subscription(self.username, int(choice))

    def my_wallet(self):
        while True:
            print("\n===== My Wallet =====")
            print("1. View balance")
            print("2. Add funds to wallet")
            print("3. View transactions")
            print("4. Purchase or renew subscription")
            print("5. Back")
            choice = input("Choose an option: ").strip()
            try:
                if choice == "1":
                    self.see_my_wallet()

                elif choice == "2":
                    self.charge_my_wallet()

                elif choice == "3":
                    self.see_my_transactions()

                elif choice == "4":
                    self.buy_or_renewal_my_subscription()

                elif choice == "5":
                    return

                else:
                    print("Invalid option.")
            except (
                ValueError,
                InsufficientBalanceError,
                StorageError,
                OSError
            ) as error:
                print("Financial operation failed:", error)
    def view_available_classes(self):
        classes = get_all_classes()

        available_classes = []
        for cls in classes:
            remaining_capacity = cls["capacity"] - len(cls["enrolled"])

            if cls["status"] == "active" and remaining_capacity > 0:
                available_classes.append(cls)

        if not available_classes:
            print("No active classes are available.")
            return

        for cls in available_classes:
            remaining_capacity = cls["capacity"] - len(cls["enrolled"])

            print(f"\n[{cls['id']}] {cls['title']} ({cls['sport']})")
            print(f"   Coach: {cls['coach']}")
            print(f"   Hall: {cls['hall']}")
            print(f"   Day and time: {cls['day']} {cls['time']}")
            print(f"   Places remaining: {remaining_capacity} of {cls['capacity']}")


        class_id = input("\nClass ID to enroll (or 'back' to return): ").strip()
        if class_id == "back":
            return

        cls = get_class_by_id(class_id)
        if cls is None:
            print("Class not found.")
            return

        if self.username in cls["enrolled"]:
            print("You are already enrolled in this class. See 'My classes'.")
            return

        try:
            is_subscription_active = has_active_subscription(self.username)
            enrollment = self.enrollments.enroll(self.username, class_id, cls, is_subscription_active)
            print("Enrollment successful. Tracking number:", enrollment.tracking_number)
        except PermissionError as error:
            print("Cannot enroll:", error)

    def my_classes(self):
        member_classes = self.enrollments.get_member_enrollments(self.username)

        if not member_classes:
            print("You have no active enrollments.")
            return

        for index, member_class in enumerate(member_classes, start = 1):
            cls = get_class_by_id(member_class.class_id)

            if cls:
                print(f"{index}. [{cls['id']}] {cls['title']} ({cls['sport']})")
                print(f"   Your tracking number: {member_class.tracking_number})")

        try:
            index = int(input("Which enrollment would you like to cancel? (0 to return): "))
            if index == 0:
                return
            elif 1 <= index <= len(member_classes):
                wanted_class = member_classes[index - 1]
            else:
                raise IndexError
        except (ValueError, IndexError):
            print("Invalid number.")
            return

        if self.enrollments.cancel(self.username, wanted_class.class_id):
            print("Enrollment cancelled successfully.")
        else:
            print("Could not cancel enrollment.")

    def my_workout(self):
        member_classes = self.enrollments.get_member_enrollments(self.username)

        if not member_classes:
            print("You are not enrolled in any classes.")
            return

        for member_class in member_classes:
            exercises = self.workouts.get_exercises(member_class.class_id, self.username)
            print(f"\n===== Workout plan for class {member_class.class_id} =====")

            if not exercises:
                print("You do not have a workout plan yet.")
                continue

            for exercise in exercises:
                print(" -", exercise)

                if exercise.exercise_description:
                    print(f"   Description: {exercise.exercise_description}")