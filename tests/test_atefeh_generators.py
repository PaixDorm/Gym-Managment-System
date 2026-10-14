from types import SimpleNamespace

from src.generators.data_generators import (
    active_members,
    coach_classes,
    class_members,
)


def test_active_members_uses_user_is_active():
    users = [
        SimpleNamespace(username="ali", is_active=True),
        SimpleNamespace(username="sara", is_active=False),
    ]
    result = list(active_members(users))
    assert [user.username for user in result] == ["ali"]


def test_coach_classes_matches_username():
    classes = [
        SimpleNamespace(coach="coach1", title="Yoga"),
        SimpleNamespace(coach="coach2", title="Pilates"),
    ]
    result = list(coach_classes(classes, "coach1"))
    assert [gym_class.title for gym_class in result] == ["Yoga"]


def test_class_members_uses_real_enrollments():
    enrollments = [
        SimpleNamespace(class_id="1", enrolled_member="ali", enrollment_status="active"),
        SimpleNamespace(class_id="1", enrolled_member="sara", enrollment_status="cancelled"),
        SimpleNamespace(class_id="2", enrolled_member="reza", enrollment_status="active"),
    ]
    assert list(class_members(enrollments, "1")) == ["ali"]
