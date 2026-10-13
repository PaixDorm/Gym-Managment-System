from src.models.file_helper import read_lines
from src.member.enrollment_manager import EnrollmentManager
from src.coach.workout_manager import WorkoutManager
from src.member.subscription_manager import has_active_subscription

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
        pass

    def my_wallet(self):
        pass

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
            wanted_class = member_classes[index - 1]
        except (ValueError, IndexError):
            print("این گزینه نامعتبر است")
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