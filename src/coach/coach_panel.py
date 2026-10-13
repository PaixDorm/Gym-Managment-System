from src.models.file_helper import read_lines
from src.coach.workout_manager import WorkoutManager
from src.models.workout import Exercise

CLASSES_FILE = "classes.txt"

def get_all_classes_by_coach(coach_username):
    result = []

    for information in read_lines(CLASSES_FILE):
        information = information.split(" | ")

        if information[3] == coach_username:
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

class CoachPanel:
    def __init__(self, coach_username):
        self.coach = coach_username
        self.workouts = WorkoutManager()

    def runner(self):
        while True:
            print("\n===== پنل مربی =====")
            print("1. مشاهدۀ کلاس های من")
            print("2. مدیریت برنامۀ تمرینی اعضا")
            print("3. خروج")

            choice = input("گزینۀ موردنظر: ").strip()

            if choice == "1":
                self.view_my_classes()
            elif choice == "2":
                self.manage_workouts()
            elif choice == "3":
                print("خروج از پنل مربی")
                return
            else:
                print("این گزینه نامعتبر است")

    def view_my_classes(self):
        classes = get_all_classes_by_coach(self.coach)

        if not classes:
            print("شما هیچ کلاسی ندارید")
            return

        for cls in classes:
            count = len(cls["enrolled"])

            print(f"\n[{cls['id']}] {cls['title']} ({cls['sport']})")
            print(f"   سالن: {cls['hall']}")
            print(f"   روز و ساعت: {cls['day']} {cls['time']}")
            print(f"   ظرفیت پر شده: {count} از {cls['capacity']}")

            if cls["enrolled"]:
                print(f"   اعضای ثبت نام شده: {', '.join(cls['enrolled'])}")
            else:
                print("   اعضای ثبت نام شده: ---")

    def manage_workouts(self):
        classes = get_all_classes_by_coach(self.coach)

        if not classes:
            print("شما هیچ کلاسی برای مدیریت ندارید")
            return

        for cls in classes:
            print(f"[{cls['id']}] {cls['title']}")

        class_id = input("شناسۀ کلاس (یا back برای بازگشت): ").strip()
        if class_id == "back":
            return

        chosen = None
        for cls in classes:
            if cls["id"] == class_id:
                chosen = cls
                break

        if chosen is None:
            print("کلاس موردنظر شما پیدا نشد")
            return
        if not chosen["enrolled"]:
            print("هیچ عضوی در این کلاس ثبت نام نکرده است")
            return

        for index, member in enumerate(chosen["enrolled"], start = 1):
            print(f"{index}. {member}")

        try:
            index = int(input("شمارۀ عضو: "))
            member = chosen["enrolled"][index - 1]
        except (ValueError, IndexError):
            print("شمارۀ وارد شده نامعتبر است")
            return

        self.edit_workout(class_id, member)

    def edit_workout(self, class_id, member):
        current = self.workouts.get_exercises(class_id, member)

        if current:
            print("\nبرنامۀ فعلی:")
            for exercise in current:
                print("  -", exercise)
        else:
            print("\nهنوز برنامه ای ثبت نشده است")

        while True:
            print("\n1. افزودن حرکت   2. جایگزینی کامل   3. بازگشت")

            choice = input("گزینۀ موردنظر: ").strip()

            if choice == "1":
                self.add_one_exercise(class_id, member)
            elif choice == "2":
                self.replace_all(class_id, member)
            elif choice == "3":
                return
            else:
                print("این گزینه نامعتبر است")

    def add_one_exercise(self, class_id, member):
        try:
            exercise_name = input("نام حرکت: ").strip()
            number_of_sets = int(input("تعداد ست های موردنظر: "))
            number_of_repeats = int(input("تعداد تکرارهای موردنظر: "))
            rest_time = int(input("مدت زمان استراحت موردنظر (برحسب ثانیه): "))
            exercise_description = input("توضیحات مربوطه (اختیاری): ").strip()

            if exercise_description == "":
                exercise_description = "---"

            exercise = Exercise(exercise_name, number_of_sets, number_of_repeats, rest_time, exercise_description)
            self.workouts.add_exercise(class_id, member, self.coach, exercise)
            print("حرکت اضافه شد")
        except ValueError as exception:
            print(f"ورودی نامعتبر: {exception}")

    def replace_all(self, class_id, member):
        print("نام هر حرکت را وارد کرده و سپس برای پایان عملیات، نام حرکت را خالی بگذارید")

        exercises = []
        while True:
            try:
                exercise_name = input("نام حرکت: ").strip()
                if exercise_name == "":
                    break

                number_of_sets = int(input("تعداد ست های موردنظر: "))
                number_of_repeats = int(input("تعداد تکرارهای موردنظر: "))
                rest_time = int(input("مدت زمان استراحت موردنظر (برحسب ثانیه): "))
                exercise_description = input("توضیحات مربوطه (اختیاری): ").strip()

                if exercise_description == "":
                    exercise_description = "---"

                exercises.append(Exercise(exercise_name, number_of_sets, number_of_repeats, rest_time, exercise_description))
            except ValueError as exception:
                print(f"ورودی نامعتبر: {exception}")

        self.workouts.save_exercises(class_id, member, self.coach, exercises)
        print("برنامه ذخیره شد")