from src.models.file_helper import read_lines
from src.member.enrollment_manager import EnrollmentManager
from src.coach.workout_manager import WorkoutManager
from src.models.workout import Exercise

CLASSES_FILE = "classes.txt"

def get_all_classes_by_coach(coach_username):
    result = []
    enrollmentmanager = EnrollmentManager()

    for information in read_lines(CLASSES_FILE):
        information = information.split(" | ")

        if len(information) != 9:
            raise ValueError("Invalid class data format.")
        if information[3] == coach_username:
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

class CoachPanel:
    def __init__(self, coach_username):
        self.coach = coach_username
        self.workouts = WorkoutManager()

    def runner(self):
        while True:
            print("\n===== Coach Panel =====")
            print("1. View my classes")
            print("2. Manage member workout plans")
            print("3. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.view_my_classes()
            elif choice == "2":
                self.manage_workouts()
            elif choice == "3":
                print("Leaving the coach panel.")
                return
            else:
                print("Invalid option.")

    def view_my_classes(self):
        classes = get_all_classes_by_coach(self.coach)

        if not classes:
            print("You have no assigned classes.")
            return

        for cls in classes:
            count = len(cls["enrolled"])

            print(f"\n[{cls['id']}] {cls['title']} ({cls['sport']})")
            print(f"   Hall: {cls['hall']}")
            print(f"   Day and time: {cls['day']} {cls['time']}")
            print(f"   Occupied places: {count} of {cls['capacity']}")

            if cls["enrolled"]:
                print(f"   Enrolled members: {', '.join(cls['enrolled'])}")
            else:
                print("   Enrolled members: ---")

    def manage_workouts(self):
        classes = get_all_classes_by_coach(self.coach)

        if not classes:
            print("You have no classes to manage.")
            return

        for cls in classes:
            print(f"[{cls['id']}] {cls['title']}")

        class_id = input("Class ID (or 'back' to return): ").strip()
        if class_id == "back":
            return

        chosen = None
        for cls in classes:
            if cls["id"] == class_id:
                chosen = cls
                break

        if chosen is None:
            print("Class not found.")
            return
        if not chosen["enrolled"]:
            print("No members are enrolled in this class.")
            return

        for index, member in enumerate(chosen["enrolled"], start = 1):
            print(f"{index}. {member}")

        try:
            index = int(input("Member number: "))
            if 1 <= index <= len(chosen["enrolled"]):
                member = chosen["enrolled"][index - 1]
            else:
                raise IndexError
        except (ValueError, IndexError):
            print("Invalid number.")
            return

        self.edit_workout(class_id, member)

    def edit_workout(self, class_id, member):
        current = self.workouts.get_exercises(class_id, member, self.coach)

        if current:
            print("\nCurrent workout plan:")
            for exercise in current:
                print("  -", exercise)
        else:
            print("\nNo workout plan has been recorded yet.")

        while True:
            print("\n1. Add exercise   2. Replace entire plan   3. Back")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.add_one_exercise(class_id, member)
            elif choice == "2":
                self.replace_all(class_id, member)
            elif choice == "3":
                return
            else:
                print("Invalid option.")

    def add_one_exercise(self, class_id, member):
        try:
            exercise_name = input("Exercise name: ").strip()
            number_of_sets = int(input("Number of sets: "))
            number_of_repeats = int(input("Number of repetitions: "))
            rest_time = int(input("Rest time (seconds): "))
            exercise_description = input("Description (optional): ").strip()

            if exercise_description == "":
                exercise_description = "---"

            exercise = Exercise(exercise_name, number_of_sets, number_of_repeats, rest_time, exercise_description)
            self.workouts.add_exercise(class_id, member, self.coach, exercise)
            print("Exercise added successfully.")
        except ValueError as exception:
            print(f"Invalid input: {exception}")

    def replace_all(self, class_id, member):
        print("Enter each exercise name; leave it blank to finish.")

        exercises = []
        while True:
            try:
                exercise_name = input("Exercise name: ").strip()
                if exercise_name == "":
                    break

                number_of_sets = int(input("Number of sets: "))
                number_of_repeats = int(input("Number of repetitions: "))
                rest_time = int(input("Rest time (seconds): "))
                exercise_description = input("Description (optional): ").strip()

                if exercise_description == "":
                    exercise_description = "---"

                exercises.append(Exercise(exercise_name, number_of_sets, number_of_repeats, rest_time, exercise_description))
            except ValueError as exception:
                print(f"Invalid input: {exception}")

        self.workouts.save_exercises(class_id, member, self.coach, exercises)
        print("Workout plan saved successfully.")