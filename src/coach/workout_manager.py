from src.models.file_helper import read_lines, write_lines
from src.models.workout import Exercise

WORKOUTS_FILE = "workouts.txt"

class WorkoutManager:
    def get_exercises(self, class_id, member_username):
        result = []

        for information in read_lines(WORKOUTS_FILE):
            information = information.split(" | ")

            if len(information) == 8:
                exercise_description = information[7]
            else:
                exercise_description = ""

            if information[0] == class_id and information[1] == member_username:
                exercise = Exercise(
                    exercise_name = information[3],
                    number_of_sets = int(information[4]),
                    number_of_repeats = int(information[5]),
                    rest_time = int(information[6]),
                    exercise_description = exercise_description
                )
                result.append(exercise)

        return result

    def save_exercises(self, class_id, member_username, coach_username, exercises):
        result = []

        for information in read_lines(WORKOUTS_FILE):
            separated_information = information.split(" | ")

            if separated_information[0] != class_id or separated_information[1] != member_username:
                result.append(information)

        for exercise in exercises:
            new_text = (f"{class_id} | {member_username} | {coach_username} | {exercise.exercise_name} | {exercise.number_of_sets} | {exercise.number_of_repeats} | {exercise.rest_time} | {exercise.exercise_description}")
            result.append(new_text)

        write_lines(WORKOUTS_FILE, result)

    def add_exercise(self, class_id, member_username, coach_username, exercise):
        before = self.get_exercises(class_id, member_username)
        before.append(exercise)

        self.save_exercises(class_id, member_username, coach_username, before)