from src.models.file_helper import read_lines, write_lines
from src.models.enrollment import Enrollment

ENROLLMENTS_FILE = "enrollments.txt"

class EnrollmentManager:
    def all_enrollments(self):
        result = []

        for information in read_lines(ENROLLMENTS_FILE):
            result.append(Enrollment.enrollment_information(information))

        return result

    def save_all_enrollments(self, all_enrollments):
        lines = []

        for enrollment in all_enrollments:
            lines.append(enrollment.to_text())

        write_lines(ENROLLMENTS_FILE, lines)

    def get_member_enrollments(self, username):
        result = []

        for enrollment in self.all_enrollments():
            if enrollment.enrolled_member == username and enrollment.being_active_checking():
                result.append(enrollment)

        return result

    def is_member_enrolled_in_this_class(self, username, class_id):
        for enrollment in self.get_member_enrollments(username):
            if enrollment.class_id == class_id:
                return True
        return False

    def enroll(self, username, class_id, cls, is_subscription_active):
        if cls["status"] != "active":
            raise PermissionError("این کلاس فعال نیست")
        if not cls["capacity"] > len(cls["enrolled"]):
            raise PermissionError("ظرفیت این کلاس پر است")
        if not is_subscription_active:
            raise PermissionError("اشتراک شما فعال نیست")
        if self.is_member_enrolled_in_this_class(username, class_id):
            raise PermissionError("شما قبلاً در این کلاس ثبت نام کرده اید")

        new_enroll = Enrollment.new_enrollment(username, class_id)
        all_enrolls = self.all_enrollments()
        all_enrolls.append(new_enroll)
        self.save_all_enrollments(all_enrolls)

        return new_enroll

    def cancel(self, username, class_id):
        all_enrolls = self.all_enrollments()
        found = False

        for enrollment in all_enrolls:
            if enrollment.enrolled_member == username and enrollment.class_id == class_id and enrollment.being_active_checking():
                enrollment.enrollment_cancelling()
                found = True

        if found:
            self.save_all_enrollments(all_enrolls)

        return found