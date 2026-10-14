from datetime import date
import random

class Enrollment:
    def __init__(self, enrolled_member, class_id, enrollment_date, tracking_number, enrollment_status):
        self.enrolled_member = enrolled_member
        self.class_id = class_id
        self.enrollment_date = enrollment_date
        self.tracking_number = tracking_number
        self.enrollment_status = enrollment_status

    @staticmethod
    def enrollment_information(information: str):
        information = information.split(" | ")

        return Enrollment(
            enrolled_member = information[0],
            class_id = information[1],
            enrollment_date = information[2],
            tracking_number = information[3],
            enrollment_status = information[4]
        )

    @staticmethod
    def new_enrollment(enrolled_member, class_id):
        return Enrollment(
            enrolled_member = enrolled_member,
            class_id = class_id,
            enrollment_date = date.today().isoformat(),
            tracking_number = random.randint(100000, 999999),
            enrollment_status = "active"
        )
    def being_active_checking(self):
        if self.enrollment_status == "active":
            return True
        else:
            return False
    def enrollment_cancelling(self):
        self.enrollment_status = "cancelled"

    def to_text(self):
        return f"{self.enrolled_member} | {self.class_id} | {self.enrollment_date} | {self.tracking_number} | {self.enrollment_status}"

    def __str__(self):
        return f"enrolled member: {self.enrolled_member} , class id: {self.class_id} , enrollment date (YYYY-MM-DD): {self.enrollment_date} , tracking number: {self.tracking_number} , enrollment status (active/cancelled): {self.enrollment_status}"