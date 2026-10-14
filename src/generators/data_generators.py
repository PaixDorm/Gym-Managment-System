def active_members(members):
    for member in members:
        if member.is_active:
            yield member
def coach_classes(classes, coach_username):
    for gym_class in classes:
        if gym_class.coach == coach_username:
            yield gym_class
def class_members(enrollments, class_id):
    for enrollment in enrollments:
        if (
            str(enrollment.class_id) == str(class_id)
            and enrollment.enrollment_status == "active"
        ):
            yield enrollment.enrolled_member
















