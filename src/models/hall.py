class Hall:
    def __init__(self, name, capacity, equipment, status):
        
        if not isinstance(name, str) or not name.strip():
                raise ValueError("نام سالن نباید خالی باشد")
        self.name = name

        if type(capacity) is not int:
            raise ValueError("لطفا مقدار معتبر وارد کنید")
        if capacity <= 0:
            raise ValueError("لطفا مقدار صحیح را وارد کنید")
        self.capacity = capacity

        if not type(equipment) is list:
            raise ValueError("لطفا یک لیست از تجهیزات وارد کنید")
        self.equipment = equipment
        
        if not type(status) is bool:
            raise ValueError("وضعیت باید فعال یا غیرفعال باشد")
        self.status = status

        