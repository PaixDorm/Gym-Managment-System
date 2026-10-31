from pathlib import Path
from datetime import time

from src.models.gym_class import GymClass
from src.admin.user_manager import find_username


CLASSES_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "classes.txt"
)


class ClassManager:
    def __init__(self, hall_manager):
        self.classes = {}
        self.hall_manager = hall_manager
        self._load()

    def _load(self):
        if not CLASSES_FILE.exists():
            return

        lines = CLASSES_FILE.read_text(
            encoding="utf-8"
        ).splitlines()

        for line in lines:
            if not line.strip():
                continue

            fields = line.split(" | ")

            if (
                len(fields) != 9
                or fields[8] not in ("active", "inactive")
            ):
                raise ValueError(
                    "Invalid class data format."
                )

            (
                class_id,
                title,
                sport,
                coach,
                hall,
                day,
                clock,
                capacity,
                status
            ) = fields

            gym_class = GymClass(
                title=title,
                sport=sport,
                coach=coach,
                time=time.fromisoformat(clock),
                day=day,
                hall=int(hall),
                capacity=int(capacity),
                status=(status == "active")
            )

            self.classes[int(class_id)] = gym_class

    def _save(self):
        CLASSES_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        lines = []

        for class_id, gym_class in self.classes.items():
            status = (
                "active"
                if gym_class.status
                else "inactive"
            )

            lines.append(
                f"{class_id} | {gym_class.title} | "
                f"{gym_class.sport} | {gym_class.coach} | "
                f"{gym_class.hall} | {gym_class.day} | "
                f"{gym_class.time.strftime('%H:%M')} | "
                f"{gym_class.capacity} | {status}"
            )

        CLASSES_FILE.write_text(
            "\n".join(lines) + ("\n" if lines else ""),
            encoding="utf-8"
        )

    def add_class(self, class_id, gym_class):
        if not isinstance(gym_class, GymClass):
            raise ValueError(
                "Input must be a GymClass instance."
            )

        if type(class_id) is not int or class_id <= 0:
            raise ValueError(
                "Class ID must be a positive integer."
            )

        if class_id in self.classes:
            raise ValueError("This ID already exists.")

        self.validate_class_resources(gym_class)

        self.classes[class_id] = gym_class
        self._save()

    def view_classes(self):
        return self.classes

    def deactivate_class(self, class_id):
        if class_id not in self.classes:
            raise ValueError("Class not found.")

        self.classes[class_id].status = False
        self._save()

    def activate_class(self, class_id):
        if class_id not in self.classes:
            raise ValueError("Class not found.")

        gym_class = self.classes[class_id]

        self.validate_class_resources(gym_class)

        gym_class.status = True
        self._save()

    def edit_class(self, class_id, new_class):
        if class_id not in self.classes:
            raise ValueError("Class not found.")

        if not isinstance(new_class, GymClass):
            raise ValueError(
                "Input must be a GymClass instance."
            )

        self.validate_class_resources(new_class)

        self.classes[class_id] = new_class
        self._save()

    def validate_class_resources(self, gym_class):
        if gym_class.hall not in self.hall_manager.halls:
            raise ValueError("Hall not found.")

        hall = self.hall_manager.halls[gym_class.hall]

        if not hall.status:
            raise ValueError("Hall is inactive.")

        if gym_class.capacity > hall.capacity:
            raise ValueError(
                "Class capacity exceeds hall capacity."
            )

        coach = find_username(gym_class.coach)

        if (
            coach is None
            or coach.role != "coach"
            or not coach.is_active
        ):
            raise ValueError(
                "Coach must be valid and active."
            )