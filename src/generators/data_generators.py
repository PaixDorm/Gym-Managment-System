def active_members(members):
    for member in members:
        if member.status:
            yield member

def coach_classes(classes, coach_id):
    for gym_class in classes:
        if gym_class.coach == coach_id:
            yield gym_class 

def class_members(enrollments, class_id):
    for enrollment in enrollments:
        if enrollment.class_id == class_id:
            yield enrollment.member_id






















