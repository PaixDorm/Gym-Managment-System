import importlib
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.models import file_helper
from src.models.enrollment import Enrollment
from src.models.workout import Exercise
from src.member.enrollment_manager import EnrollmentManager
from src.coach.workout_manager import WorkoutManager
from src.coach import coach_panel


@pytest.fixture
def isolated_data(tmp_path, monkeypatch):
    """Keep all reading and writing out of real project data."""
    monkeypatch.setattr(file_helper, "DATA_DIR", str(tmp_path))
    return tmp_path


def new_class(capacity=2, enrolled=None, status="active"):
    return {
        "id": "1", "title": "Yoga", "sport": "yoga",
        "coach": "coach1", "hall": "2", "day": "Saturday", "time": "18:30",
        "capacity": capacity, "status": status,
        "enrolled": [] if enrolled is None else enrolled,
    }


def member_module(monkeypatch):
    """Import member panel even when other teammates' modules are still empty."""
    from src.admin import user_manager
    from src.member import subscription_manager, wallet_manager

    required = [
        (user_manager, "find_username"),
        (subscription_manager, "has_active_subscription"),
        (subscription_manager, "get_subscription_state"),
        (subscription_manager, "get_current_subscription"),
        (subscription_manager, "get_days_left"),
        (subscription_manager, "get_plans"),
        (subscription_manager, "buy_subscription"),
        (wallet_manager, "get_wallet"),
        (wallet_manager, "get_transactions"),
        (wallet_manager, "charge_wallet"),
    ]
    for module, name in required:
        if not hasattr(module, name):
            monkeypatch.setattr(module, name, Mock(name=name), raising=False)
    return importlib.import_module("src.member.member_panel")


def test_enroll_success_is_saved_and_reloaded(isolated_data):
    manager = EnrollmentManager()
    enrollment = manager.enroll("sara", "1", new_class(), True)
    assert enrollment.enrolled_member == "sara"
    assert enrollment.enrollment_status == "active"
    assert len(EnrollmentManager().get_member_enrollments("sara")) == 1


@pytest.mark.parametrize(
    "cls, active_subscription",
    [
        (new_class(status="inactive"), True),
        (new_class(), False),
    ],
)
def test_enroll_rejects_invalid_conditions(isolated_data, cls, active_subscription):
    with pytest.raises(PermissionError):
        EnrollmentManager().enroll("sara", "1", cls, active_subscription)
    assert EnrollmentManager().all_enrollments() == []


def test_duplicate_active_enrollment_is_rejected(isolated_data):
    manager = EnrollmentManager()
    manager.enroll("sara", "1", new_class(), True)
    with pytest.raises(PermissionError):
        manager.enroll("sara", "1", new_class(), True)
    assert len(manager.get_member_enrollments("sara")) == 1


def test_cancel_only_own_active_enrollment(isolated_data):
    manager = EnrollmentManager()
    manager.enroll("sara", "1", new_class(), True)
    assert manager.cancel("ali", "1") is False
    assert len(manager.get_member_enrollments("sara")) == 1
    assert manager.cancel("sara", "1") is True
    assert manager.cancel("sara", "1") is False
    assert manager.get_member_enrollments("sara") == []


def test_can_reenroll_after_cancel(isolated_data):
    manager = EnrollmentManager()
    manager.enroll("sara", "1", new_class(), True)
    assert manager.cancel("sara", "1") is True
    manager.enroll("sara", "1", new_class(), True)
    assert len(manager.get_member_enrollments("sara")) == 1


def test_capacity_uses_active_enrollments_not_stale_class_list(isolated_data):
    """Regression: a class with one seat must reject a second person."""
    manager = EnrollmentManager()
    manager.enroll("ali", "1", new_class(capacity=1), True)
    with pytest.raises(PermissionError):
        manager.enroll("sara", "1", new_class(capacity=1, enrolled=[]), True)


def test_member_class_listing_uses_active_enrollments(isolated_data, monkeypatch):
    """Regression: classes.txt has 9 columns, enrollments.txt is the source of members."""
    file_helper.write_lines("classes.txt", [
        "1 | Yoga | yoga | coach1 | 2 | Saturday | 18:30 | 2 | active"
    ])
    manager = EnrollmentManager()
    manager.enroll("sara", "1", new_class(), True)
    manager.enroll("ali", "1", new_class(), True)
    mod = member_module(monkeypatch)
    classes = mod.get_all_classes()
    assert len(classes) == 1
    assert sorted(classes[0]["enrolled"]) == ["ali", "sara"]


def test_coach_class_listing_uses_active_enrollments(isolated_data):
    file_helper.write_lines("classes.txt", [
        "1 | Yoga | yoga | coach1 | 2 | Saturday | 18:30 | 2 | active",
        "2 | Pilates | pilates | coach2 | 2 | Monday | 19:00 | 5 | active",
    ])
    EnrollmentManager().enroll("sara", "1", new_class(), True)
    classes = coach_panel.get_all_classes_by_coach("coach1")
    assert len(classes) == 1
    assert classes[0]["id"] == "1"
    assert classes[0]["enrolled"] == ["sara"]


@pytest.mark.parametrize(
    "fields",
    [
        ("", 3, 10, 30),
        ("Squat", 0, 10, 30),
        ("Squat", 3, 0, 30),
        ("Squat", 3, 10, 0),
    ],
)
def test_exercise_rejects_invalid_values(fields):
    with pytest.raises(ValueError):
        Exercise(*fields)


def test_exercise_round_trip():
    original = Exercise("Squat", 3, 12, 60, "slow")
    copied = Exercise.exercise_information(original.to_text().split(" | "))
    assert (copied.exercise_name, copied.number_of_sets,
            copied.number_of_repeats, copied.rest_time,
            copied.exercise_description) == ("Squat", 3, 12, 60, "slow")


def test_workouts_persist_and_keep_members_separate(isolated_data):
    manager = WorkoutManager()
    manager.add_exercise("1", "sara", "coach1", Exercise("Squat", 3, 10, 30))
    manager.add_exercise("1", "ali", "coach1", Exercise("Run", 2, 5, 20))
    assert [e.exercise_name for e in WorkoutManager().get_exercises("1", "sara", "coach1")] == ["Squat"]
    assert [e.exercise_name for e in WorkoutManager().get_exercises("1", "ali", "coach1")] == ["Run"]


def test_replacing_workout_keeps_other_members_untouched(isolated_data):
    manager = WorkoutManager()
    manager.add_exercise("1", "ali", "coach1", Exercise("Run", 2, 5, 20))
    manager.add_exercise("1", "sara", "coach1", Exercise("Squat", 3, 10, 30))
    manager.save_exercises("1", "sara", "coach1", [Exercise("Plank", 2, 8, 20)])
    assert [e.exercise_name for e in manager.get_exercises("1", "sara", "coach1")] == ["Plank"]
    assert [e.exercise_name for e in manager.get_exercises("1", "ali", "coach1")] == ["Run"]


def test_workouts_of_coaches_do_not_overwrite_each_other(isolated_data):
    manager = WorkoutManager()
    manager.add_exercise("1", "sara", "coach1", Exercise("Squat", 3, 10, 30))
    manager.add_exercise("1", "sara", "coach2", Exercise("Run", 2, 5, 20))
    assert [e.exercise_name for e in manager.get_exercises("1", "sara", "coach1")] == ["Squat"]
    assert [e.exercise_name for e in manager.get_exercises("1", "sara", "coach2")] == ["Run"]


@pytest.mark.parametrize("bad_index", ["0", "-1", "99", "abc"])
def test_coach_cannot_pick_invalid_member_index(monkeypatch, bad_index):
    monkeypatch.setattr(coach_panel, "get_all_classes_by_coach", lambda _: [
        {**new_class(enrolled=["sara"])}
    ])
    panel = coach_panel.CoachPanel("coach1")
    editor = Mock()
    monkeypatch.setattr(panel, "edit_workout", editor)
    answers = iter(["1", bad_index])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    panel.manage_workouts()
    editor.assert_not_called()


@pytest.mark.parametrize("bad_index", ["0", "-1", "99", "abc"])
def test_member_cannot_cancel_wrong_item(monkeypatch, bad_index):
    mod = member_module(monkeypatch)
    panel = mod.MemberPanel("sara")
    panel.enrollments.get_member_enrollments = Mock(return_value=[
        SimpleNamespace(class_id="1", tracking_number="123")
    ])
    panel.enrollments.cancel = Mock()
    monkeypatch.setattr(mod, "get_class_by_id", lambda _: new_class())
    monkeypatch.setattr("builtins.input", lambda _: bad_index)
    panel.my_classes()
    panel.enrollments.cancel.assert_not_called()


def test_profile_without_subscription(monkeypatch, capsys):
    mod = member_module(monkeypatch)
    monkeypatch.setattr(mod, "find_username", lambda _: SimpleNamespace(
        name="Sara", username="sara", email="s@test.com", is_active=True
    ))
    monkeypatch.setattr(mod, "get_subscription_state", lambda _: "none")
    monkeypatch.setattr(mod, "get_current_subscription", lambda _: None)
    mod.MemberPanel("sara").my_profile_and_subscription_status()
    assert "No subscription" in capsys.readouterr().out


def test_profile_handles_inactive_state_without_subscription(monkeypatch, capsys):
    """Regression: financial module may report inactive rather than none."""
    mod = member_module(monkeypatch)
    monkeypatch.setattr(mod, "find_username", lambda _: SimpleNamespace(
        name="Sara", username="sara", email="s@test.com", is_active=True
    ))
    monkeypatch.setattr(mod, "get_subscription_state", lambda _: "inactive")
    monkeypatch.setattr(mod, "get_current_subscription", lambda _: None)
    mod.MemberPanel("sara").my_profile_and_subscription_status()
    assert "No subscription" in capsys.readouterr().out

def test_profile_with_active_subscription(monkeypatch, capsys):
    mod = member_module(monkeypatch)
    monkeypatch.setattr(mod, "find_username", lambda _: SimpleNamespace(
        name="Sara", username="sara", email="s@test.com", is_active=True
    ))
    monkeypatch.setattr(mod, "get_subscription_state", lambda _: "active")
    monkeypatch.setattr(mod, "get_current_subscription", lambda _: SimpleNamespace(
        months=3, start_date="2026-01-01", end_date="2026-04-01"
    ))
    monkeypatch.setattr(mod, "get_days_left", lambda _: 14)
    mod.MemberPanel("sara").my_profile_and_subscription_status()
    assert "14" in capsys.readouterr().out
def test_wallet_shows_balance_and_transactions(monkeypatch, capsys):
    mod = member_module(monkeypatch)
    monkeypatch.setattr(mod, "get_wallet", lambda _: SimpleNamespace(balance=150000))
    monkeypatch.setattr(mod, "get_transactions", lambda _: [SimpleNamespace(
        transaction_type="charge", amount=150000, date="2026-01-01", tracking_code="TX1"
    )])
    panel = mod.MemberPanel("sara")
    panel.see_my_wallet()
    panel.see_my_transactions()
    text = capsys.readouterr().out
    assert "150000" in text and "TX1" in text
def test_wallet_charge_forwards_user_inputs(monkeypatch):
    mod = member_module(monkeypatch)
    charge = Mock()
    monkeypatch.setattr(mod, "charge_wallet", charge)
    inputs = iter(["1234567890123456", "12", "2027", "123456", "123", "50000"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    mod.MemberPanel("sara").charge_my_wallet()
    charge.assert_called_once_with(
        "sara", "1234567890123456", "12", "2027", "123456", "123", "50000"
    )
def test_subscription_purchase_calls_financial_module(monkeypatch):
    mod = member_module(monkeypatch)
    buy = Mock()
    monkeypatch.setattr(
        mod,
        "get_plans",
        lambda: {
            1: SimpleNamespace(price=100000),
            3: SimpleNamespace(price=250000),
            6: SimpleNamespace(price=400000)
        }
    )
    monkeypatch.setattr(mod, "buy_subscription", buy)
    monkeypatch.setattr("builtins.input", lambda _: "3")
    mod.MemberPanel("sara").buy_or_renewal_my_subscription()
    buy.assert_called_once_with("sara", 3)
def test_reports_count_only_active_enrollments(isolated_data, monkeypatch):
    from src.member import subscription_manager
    if not hasattr(subscription_manager, "get_revenue_by_type"):
        monkeypatch.setattr(subscription_manager, "get_revenue_by_type", Mock(return_value={}), raising=False)
    reports = importlib.import_module("src.admin.admin_reports")
    file_helper.write_lines("enrollments.txt", [
        "sara | 1 | 2026-01-01 | 100 | active",
        "ali | 1 | 2026-01-01 | 101 | cancelled",
        "reza | 2 | 2026-01-01 | 102 | active",
    ])
    assert reports.enrollments_per_class() == {"1": 1, "2": 1}
    assert reports.most_popular_classes() == ["1", "2"]


def test_reports_income_uses_financial_source(monkeypatch):
    from src.member import subscription_manager
    if not hasattr(subscription_manager, "get_revenue_by_type"):
        monkeypatch.setattr(subscription_manager, "get_revenue_by_type", Mock(return_value={}), raising=False)
    reports = importlib.import_module("src.admin.admin_reports")
    monkeypatch.setattr(reports, "get_revenue_by_type", lambda: {1: 50000, 3: 100000})
    assert reports.income_by_subscription_type() == {1: 50000, 3: 100000}