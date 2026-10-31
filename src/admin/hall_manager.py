from pathlib import Path
from src.models.hall import Hall

HALLS_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "halls.txt"
)


class HallManager:
    def __init__(self):
        self.halls = {}
        self._load()

    def _load(self):
        if not HALLS_FILE.exists():
            return

        lines = HALLS_FILE.read_text(
            encoding="utf-8"
        ).splitlines()

        for line in lines:
            if not line.strip():
                continue

            fields = line.split(" | ")

            if (
                len(fields) != 5
                or fields[4] not in ("active", "inactive")
            ):
                raise ValueError(
                    "Invalid hall data format."
                )

            hall_id, name, capacity, equipment, status = fields

            equipment_list = (
                equipment.split(",")
                if equipment else []
            )

            self.halls[int(hall_id)] = Hall(
                name,
                int(capacity),
                equipment_list,
                status == "active"
            )

    def _save(self):
        HALLS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        lines = []

        for hall_id, hall in self.halls.items():
            status = (
                "active" if hall.status else "inactive"
            )

            equipment = ",".join(hall.equipment)

            lines.append(
                f"{hall_id} | {hall.name} | "
                f"{hall.capacity} | {equipment} | {status}"
            )

        HALLS_FILE.write_text(
            "\n".join(lines) + ("\n" if lines else ""),
            encoding="utf-8"
        )

    def add_hall(self, hall_id, hall):
        if not isinstance(hall, Hall):
            raise ValueError("Input must be a Hall instance.")

        if type(hall_id) is not int or hall_id <= 0:
            raise ValueError("Hall ID must be a positive integer.")

        if hall_id in self.halls:
            raise ValueError("This ID already exists.")

        self.halls[hall_id] = hall
        self._save()

    def view_halls(self):
        return self.halls

    def activate_hall(self, hall_id):
        if hall_id not in self.halls:
            raise ValueError("Hall not found.")

        self.halls[hall_id].status = True
        self._save()

    def deactivate_hall(self, hall_id):
        if hall_id not in self.halls:
            raise ValueError("Hall not found.")

        self.halls[hall_id].status = False
        self._save()

    def edit_hall(self, hall_id, new_hall):
        if hall_id not in self.halls:
            raise ValueError("Hall not found.")

        if not isinstance(new_hall, Hall):
            raise ValueError("Input must be a Hall instance.")

        self.halls[hall_id] = new_hall
        self._save()

