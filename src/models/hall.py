class Hall:
    def __init__(self, name, capacity, equipment, status):
        
        if not isinstance(name, str) or not name.strip():
                raise ValueError("Hall name cannot be empty.")
        if any(ch in name for ch in ("|", "\n", "\r")):
            raise ValueError(
                "Hall name contains forbidden characters."
            )
        self.name = name

        if type(capacity) is not int:
            raise ValueError("Please enter a valid integer.")
        if capacity <= 0:
            raise ValueError("Value must be greater than zero.")
        self.capacity = capacity

        if not type(equipment) is list:
            raise ValueError("Equipment must be provided as a list.")
        for item in equipment:
            if (
                not isinstance(item, str)
                or not item.strip()
                or any(ch in item for ch in (",", "|", "\n", "\r"))
            ):
                raise ValueError(
                    "Equipment contains an invalid name."
                )
        self.equipment = equipment
        
        if not type(status) is bool:
            raise ValueError("Status must be a boolean.")
        self.status = status

        