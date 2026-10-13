from src.admin import admin_reports as rep


def test_most_popular_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(rep, "read_lines", lambda f: [])
    assert rep.most_popular_classes() is None


def test_most_popular(monkeypatch):
    fake = [
        "sara|A|2025-01-01|1|active",
        "reza|A|2025-01-02|2|active",
        "ali|B|2025-01-03|3|active",
    ]
    monkeypatch.setattr(rep, "read_lines", lambda f: fake if f == "enrollments.txt" else [])
    assert rep.most_popular_classes() == "A"
    assert rep.enrollments_per_class() == {"A": 2, "B": 1}