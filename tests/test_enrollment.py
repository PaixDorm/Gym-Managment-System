import pytest
from src.member.enrollment_manager import EnrollmentManager


def fake_class(status="active", cap=2, enrolled=None):
    return {
        "id": "C1", "status": status, "capacity": cap,
        "enrolled": enrolled or [],
    }


def test_enroll_inactive_class():
    em = EnrollmentManager()
    with pytest.raises(PermissionError):
        em.enroll("sara", "C1", fake_class(status="inactive"), True)


def test_enroll_full():
    em = EnrollmentManager()
    with pytest.raises(PermissionError):
        em.enroll("sara", "C1", fake_class(cap=1, enrolled=["x"]), True)


def test_enroll_no_subscription():
    em = EnrollmentManager()
    with pytest.raises(PermissionError):
        em.enroll("sara", "C1", fake_class(), False)


def test_enrollment_model():
    from src.models.enrollment import Enrollment
    e = Enrollment.new_enrollment("sara", "C1")
    assert e.enrollment_status == "active"
    assert e.tracking_number.isdigit()
    e.enrollment_cancelling()
    assert e.enrollment_status == "cancelled"