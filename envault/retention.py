"""Retention policy management for vault variables."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

VALID_ACTIONS = ("archive", "delete", "warn")


def _retention_path(vault_file: str) -> Path:
    return Path(vault_file).parent / ".envault_retention.json"


def _load_retention(vault_file: str) -> dict:
    p = _retention_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_retention(vault_file: str, data: dict) -> None:
    _retention_path(vault_file).write_text(json.dumps(data, indent=2))


def set_retention(vault_file: str, key: str, days: int, action: str = "warn") -> dict:
    """Set a retention policy for a key."""
    if days <= 0:
        raise ValueError("days must be a positive integer")
    if action not in VALID_ACTIONS:
        raise ValueError(f"action must be one of {VALID_ACTIONS}")
    data = _load_retention(vault_file)
    entry = {
        "key": key,
        "days": days,
        "action": action,
        "set_at": datetime.utcnow().isoformat(),
        "due_at": (datetime.utcnow() + timedelta(days=days)).isoformat(),
    }
    data[key] = entry
    _save_retention(vault_file, data)
    return entry


def remove_retention(vault_file: str, key: str) -> bool:
    data = _load_retention(vault_file)
    if key not in data:
        return False
    del data[key]
    _save_retention(vault_file, data)
    return True


def get_retention(vault_file: str, key: str) -> Optional[dict]:
    return _load_retention(vault_file).get(key)


def list_retention(vault_file: str) -> list[dict]:
    return list(_load_retention(vault_file).values())


def get_due_keys(vault_file: str) -> list[dict]:
    """Return all keys whose retention period has elapsed."""
    now = datetime.utcnow()
    return [
        entry
        for entry in list_retention(vault_file)
        if datetime.fromisoformat(entry["due_at"]) <= now
    ]
