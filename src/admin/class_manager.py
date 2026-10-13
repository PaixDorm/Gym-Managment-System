from src.models.gym_class import GymClass
from src.admin.user_manager import find_username


class ClassManager:
    def __init__(self, hall_manager):
        self.classes = {}
        self.hall_manager = hall_manager

    def add_class(self, class_id, gym_class):
        if not isinstance(gym_class, GymClass):
            raise ValueError("ورودی باید یک شیء از کلاس GymClass باشد")

        if class_id in self.classes:
            raise ValueError("شناسه تکراری است")

        self.validate_class_resources(gym_class)
        self.classes[class_id] = gym_class

    def view_classes(self):
        return self.classes

    def deactivate_class(self, class_id):
        if class_id not in self.classes:
            raise ValueError("کلاس وجود ندارد")

        self.classes[class_id].status = False

    def activate_class(self, class_id):
        if class_id not in self.classes:
            raise ValueError("کلاس وجود ندارد")

        gym_class = self.classes[class_id]

        self.validate_class_resources(gym_class)

        gym_class.status = True

    def edit_class(self, class_id, new_class):
        if not isinstance(new_class, GymClass):
            raise ValueError("کلاس جدید باید شیء GymClass باشد")

        if class_id not in self.classes:
            raise ValueError("شناسه کلاس وجود ندارد")

        self.validate_class_resources(new_class)
        self.classes[class_id] = new_class

    def validate_class_resources(self, gym_class):
    
        if gym_class.hall not in self.hall_manager.halls:
            raise ValueError("سالن موردنظر پیدا نشد")

        selected_hall = self.hall_manager.halls[gym_class.hall]

        if not selected_hall.status:
            raise ValueError("سالن غیرفعال است")

        if selected_hall.capacity < gym_class.capacity:
            raise ValueError("ظرفیت کلاس از ظرفیت سالن بیشتر است")

        selected_coach = find_username(gym_class.coach)

        if selected_coach is None:
            raise ValueError("مربی موردنظر وجود ندارد")

        if selected_coach.role != "coach":
            raise ValueError("کاربر انتخاب‌شده مربی نیست")

        if not selected_coach.is_active:
            raise ValueError("مربی غیرفعال است")