from datetime import time as Time

class GymClass:
    def __init__(self, title, sport, coach, time, day, hall, capacity, status):

        if not isinstance(title, str) or not title.strip():
            raise ValueError("نام کلاس نباید خالی باشد")
        self.title = title
        
        if not isinstance(sport, str) or not sport.strip():
            raise ValueError("رشته ورزشی نباید خالی باشد ")
        self.sport = sport

        if not isinstance(coach, str) or not coach.strip():
           raise ValueError("نام کاربری مربی معتبر نیست")
        self.coach = coach

        if not isinstance(time, Time):
            raise ValueError("زمان کلاس باید از نوع time باشد")
        self.time = time

        if not isinstance(day, str) or not day.strip():
            raise ValueError("روز ورزش نباید خالی باشد")
        self.day = day

        if type(hall) is not int:
            raise ValueError("لطفا مقدار معتبر وارد کنید")
        if hall <= 0:
            raise ValueError("لطفا مقدار صحیح را وارد کنید")
        self.hall = hall

        if type(capacity) is not int:
            raise ValueError("لطفا مقدار معتبر وارد کنید")
        if capacity <= 0:
            raise ValueError("لطفا مقدار صحیح را وارد کنید")
        self.capacity = capacity

        if not type(status) is bool:
            raise ValueError("وضعیت باید فعال یا غیرفعال باشد")
        self.status = status