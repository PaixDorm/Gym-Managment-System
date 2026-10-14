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
    charge_wallet
)

CLASSES_FILE = "classes.txt"

def get_all_classes():
    result = []

    for information in read_lines(CLASSES_FILE):
        information = information.split(" | ")

        if len(information) == 10:
            enrolled = information[9]
        else:
            enrolled = []

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
            "enrolled": enrolled
            }
        result.append(cls)

    return result

def get_class_by_id(class_id):
    for cls in get_all_classes():
        if cls["id"] == class_id:
            return cls
        
    return None

class MemberPanel:
    def __init__(self, username):
        self.username = username
        self.enrollments = EnrollmentManager()
        self.workouts = WorkoutManager()

    def runner(self):
        while True:
            print("\n===== پنل عضو =====")
            print("1. پروفایل و وضعیت اشتراک من")
            print("2. کیف پول من")
            print("3. کلاس های قابل ثبت نام")
            print("4. کلاس های من")
            print("5. برنامۀ تمرینی من")
            print("6. خروج")

            choice = input("گزینۀ موردنظر: ").strip()

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
                print("این گزینه نامعتبر است")

    def my_profile_and_subscription_status(self):
        user = find_username(self.username)
        user_subscription_state = get_subscription_state(self.username)
        user_subscription = get_current_subscription(self.username)

        if user is None:
            print("چنین کاربری بافت نشد")
            return

        print(f"نام: {user.name}")
        print(f"نام کاربری: {user.username}")
        print(f"ایمیل: {user.email}")
        print(f"وضعیت حساب کاربر: {user.is_active}")

        if user_subscription_state == "none":
            print("بدون اشتراک")
        else:
            print(f"نوع اشتراک کاربر: {user_subscription.months} ماهه")
            print(f"تاریخ شروع اشتراک کاربر: {user_subscription.start_date}")
            print(f"تاریخ پایان اشتراک کاربر: {user_subscription.end_date}")
            if user_subscription_state == "active":
                print(f"روزهای باقی‌مانده: {get_days_left(self.username)}")
            print(f"وضعیت اشتراک کاربر: {user_subscription_state}")

    def see_my_wallet(self):
        wallet = get_wallet(self.username)
        print(f"موجودی: {wallet.balance}")

    def charge_my_wallet(self):
        my_card = input("شمارۀ کارت موردنظر خود را وارد کنید (16 رقمی): ").strip()
        my_card_month = input("ماه انقضای کارت موردنظر خود را وارد کنید (از 1 تا 12): ").strip()
        my_card_year = input("سال انقضای کارت موردنظر خود را وارد کنید (4 رقمی): ").strip()
        my_card_password = input("رمز دوم کارت موردنظر خود را وارد کنید (6 رقمی): ").strip()
        my_card_cvv2 = input("cvv2 کارت موردنظر خود را وارد کنید (3 رقمی): ").strip()
        my_amount = input("مبلغ موردنظر خود را وارد کنید (مقداری طبیعی، به تومان): ").strip()

        charge_wallet(self.username, my_card, my_card_month, my_card_year, my_card_password, my_card_cvv2, my_amount)

    def see_my_transactions(self):
        transactions = get_transactions(self.username)

        if not transactions:
            print("تراکنشی وجود ندارد")
            return

        for transaction in transactions:
            print(f"{transaction.transaction_type} | {transaction.amount} | {transaction.date} | {transaction.tracking_code}")

    def buy_or_renewal_my_subscription(self):
        print(get_plans())

        choice = input("گزینۀ موردنظر (از میان اعداد 1، 3، 6): ").strip()
        if choice not in ("1", "3", "6"):
            print("این گزینه نامعتبر است")
            return
        
        buy_subscription(self.username, int(choice))

    def my_wallet(self):
        while True:
            print("\n===== کیف پول من =====")
            print("1. مشاهدۀ موجودی من")
            print("2. شارژ کیف پول من")
            print("3. مشاهدۀ تراکنش های من")
            print("4. پرداخت یا تمدید اشتراک من")
            print("5. بازگشت به پنل عضو")

            choice = input("گزینۀ موردنظر: ").strip()

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
                print("این گزینه نامعتبر است")

    def view_available_classes(self):
        classes = get_all_classes()

        available_classes = []
        for cls in classes:
            remaining_capacity = cls["capacity"] - len(cls["enrolled"])

            if cls["status"] == "active" and remaining_capacity > 0:
                available_classes.append(cls)

        if not available_classes:
            print("هیچ کلاس فعالی وجود ندارد")
            return

        for cls in available_classes:
            remaining_capacity = cls["capacity"] - len(cls["enrolled"])

            print(f"\n[{cls['id']}] {cls['title']} ({cls['sport']})")
            print(f"   مربی: {cls['coach']}")
            print(f"   سالن: {cls['hall']}")
            print(f"   روز و ساعت: {cls['day']} {cls['time']}")
            print(f"   ظرفیت باقی مانده: {remaining_capacity} از {cls['capacity']}")


        class_id = input("\nشناسۀ کلاس برای ثبت نام (یا back برای بازگشت): ").strip()
        if class_id == "back":
            return

        cls = get_class_by_id(class_id)
        if cls is None:
            print("چنین کلاسی پیدا نشد")
            return

        if self.username in cls["enrolled"]:
            print("شما قبلاً در این کلاس ثبت نام کرده اید؛ برای مشاهدۀ آن، به بخش *کلاس های من* مراجعه کنید")
            return

        try:
            is_subscription_active = has_active_subscription(self.username)
            enrollment = self.enrollments.enroll(self.username, class_id, cls, is_subscription_active)
            print("ثبت نام شما با موفقیت انجام شد. شماره پیگیری:", enrollment.tracking_number)
        except PermissionError as error:
            print("شما نمی توانید ثبت نام کنید:", error)

    def my_classes(self):
        member_classes = self.enrollments.get_member_enrollments(self.username)

        if not member_classes:
            print("شما هیچ ثبت نام فعالی ندارید")
            return

        for index, member_class in enumerate(member_classes, start = 1):
            cls = get_class_by_id(member_class.class_id)

            if cls:
                print(f"{index}. [{cls['id']}] {cls['title']} ({cls['sport']})")
                print(f"   شمارۀ پیگیری شما: {member_class.tracking_number})")

        try:
            index = int(input("می خواهید کدام ثبت نام خود را لغو کنید؟ (برای بازگشت عدد 0 را وارد کنید): "))
            if index == 0:
                return
            elif 1 <= index <= len(member_classes):
                wanted_class = member_classes[index - 1]
            else:
                raise IndexError
        except (ValueError, IndexError):
            print("شمارۀ وارد شده نامعتبر است")
            return

        if self.enrollments.cancel(self.username, wanted_class.class_id):
            print("عملیات لغو ثبت نام با موفقیت انجام شد")
        else:
            print("عملیات لغو ثبت نام انجام نشد")

    def my_workout(self):
        member_classes = self.enrollments.get_member_enrollments(self.username)

        if not member_classes:
            print("شما در هیچ کلاسی ثبت نام نکرده اید")
            return

        for member_class in member_classes:
            exercises = self.workouts.get_exercises(member_class.class_id, self.username)
            print(f"\n===== برنامۀ کلاس {member_class.class_id} =====")

            if not exercises:
                print("شما هنوز برنامۀ تمرینی ای ندارید")
                continue

            for exercise in exercises:
                print(" -", exercise)

                if exercise.exercise_description:
                    print(f"   توضیحات مربوطه: {exercise.exercise_description}")