class Exercise:
    def __init__(self, exercise_name, number_of_sets, number_of_repeats, rest_time, exercise_description = "---"):
        if exercise_name.strip() == "":
            raise ValueError("نام حرکت نمی تواند خالی باشد")
        if not number_of_sets > 0:
            raise ValueError("تعداد ست های تمرین باید بزرگتر از صفر باشد")
        if not number_of_repeats > 0:
            raise ValueError("تعداد تکرارهای تمرین باید بزرگتر از صفر باشد")
        if not rest_time > 0:
            raise ValueError("زمان استراحت تمرین باید بزرگتر از صفر باشد")

        self.exercise_name = exercise_name
        self.number_of_sets = number_of_sets
        self.number_of_repeats = number_of_repeats
        self.rest_time = rest_time
        self.exercise_description = exercise_description

    @staticmethod
    def exercise_information(information: list):
        if len(information) == 5:
            exercise_description = information[4]
        else:
            exercise_description = "---"

        return Exercise(
            exercise_name = information[0],
            number_of_sets = int(information[1]),
            number_of_repeats = int(information[2]),
            rest_time = int(information[3]),
            exercise_description = exercise_description
        )

    def to_text(self):
        return f"{self.exercise_name} | {self.number_of_sets} | {self.number_of_repeats} | {self.rest_time} | {self.exercise_description}"

    def __str__(self):
        return f"exercise name: {self.exercise_name} , number of sets: {self.number_of_sets} , number of repeats: {self.number_of_repeats} , rest time (in seconds): {self.rest_time} , description (might be empty): {self.exercise_description}"