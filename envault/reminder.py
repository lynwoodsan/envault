"""Reminder module: schedule and retrieve rotation/review reminders for vault keys."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def _reminder_path(vault_path: Path) -> Path:
    return vault_path.parent / ".envault_reminders.json"


def _load_reminders(vault_path: Path) -> dict:
    p = _reminder_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_reminders(vault_path: Path, data: dict) -> None:
    p = _reminder_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_reminder(vault_path: Path, key: str, days: int, note: str = "") -> datetime:
    """Schedule a reminder for *key* in *days* days from now."""
    if days <= 0:
        raise ValueError("days must be a positive integer")
    data = _load_reminders(vault_path)
    due = datetime.utcnow() + timedelta(days=days)
    data[key] = {
        "due": due.isoformat(),
        "note": note,
    }
    _save_reminders(vault_path, data)
    return due


def remove_reminder(vault_path: Path, key: str) -> bool:
    """Remove the reminder for *key*. Returns True if it existed."""
    data = _load_reminders(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_reminders(vault_path, data)
    return True


def get_reminder(vault_path: Path, key: str) -> Optional[dict]:
    """Return reminder dict for *key* or None."""
    return _load_reminders(vault_path).get(key)


def list_reminders(vault_path: Path) -> list[dict]:
    """Return all reminders sorted by due date."""
    data = _load_reminders(vault_path)
    entries = [
        {"key": k, "due": v["due"], "note": v["note"]}
        for k, v in data.items()
    ]
    return sorted(entries, key=lambda e: e["due"])


def due_reminders(vault_path: Path) -> list[dict]:
    """Return reminders whose due date is now or in the past."""
    now = datetime.utcnow().isoformat()
    return [r for r in list_reminders(vault_path) if r["due"] <= now]
