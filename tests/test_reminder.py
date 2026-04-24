"""Tests for envault.reminder."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from envault.reminder import (
    set_reminder,
    remove_reminder,
    get_reminder,
    list_reminders,
    due_reminders,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.env"
    vf.touch()
    return vf


def test_set_reminder_returns_due_date(vault_file):
    due = set_reminder(vault_file, "API_KEY", 7)
    assert isinstance(due, datetime)
    assert due > datetime.utcnow()


def test_get_reminder_returns_entry(vault_file):
    set_reminder(vault_file, "API_KEY", 30, note="rotate quarterly")
    entry = get_reminder(vault_file, "API_KEY")
    assert entry is not None
    assert "due" in entry
    assert entry["note"] == "rotate quarterly"


def test_get_reminder_missing_returns_none(vault_file):
    assert get_reminder(vault_file, "NONEXISTENT") is None


def test_set_reminder_invalid_days_raises(vault_file):
    with pytest.raises(ValueError):
        set_reminder(vault_file, "API_KEY", 0)
    with pytest.raises(ValueError):
        set_reminder(vault_file, "API_KEY", -5)


def test_remove_reminder_returns_true(vault_file):
    set_reminder(vault_file, "DB_PASS", 10)
    assert remove_reminder(vault_file, "DB_PASS") is True
    assert get_reminder(vault_file, "DB_PASS") is None


def test_remove_nonexistent_returns_false(vault_file):
    assert remove_reminder(vault_file, "GHOST") is False


def test_list_reminders_sorted(vault_file):
    set_reminder(vault_file, "Z_KEY", 20)
    set_reminder(vault_file, "A_KEY", 5)
    set_reminder(vault_file, "M_KEY", 10)
    reminders = list_reminders(vault_file)
    dues = [r["due"] for r in reminders]
    assert dues == sorted(dues)


def test_list_reminders_empty(vault_file):
    assert list_reminders(vault_file) == []


def test_due_reminders_past_only(vault_file):
    set_reminder(vault_file, "FUTURE_KEY", 30)
    # Manually inject a past reminder
    import json
    rpath = vault_file.parent / ".envault_reminders.json"
    data = json.loads(rpath.read_text())
    past = (datetime.utcnow() - timedelta(days=1)).isoformat()
    data["OLD_KEY"] = {"due": past, "note": "overdue"}
    rpath.write_text(json.dumps(data))

    due = due_reminders(vault_file)
    keys = [r["key"] for r in due]
    assert "OLD_KEY" in keys
    assert "FUTURE_KEY" not in keys
