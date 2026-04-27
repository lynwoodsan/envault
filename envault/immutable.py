"""Immutable variable protection — prevent accidental overwrites or deletes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _immutable_path(vault_file: str) -> Path:
    return Path(vault_file).parent / ".envault_immutable.json"


def _load_immutable(vault_file: str) -> dict:
    path = _immutable_path(vault_file)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_immutable(vault_file: str, data: dict) -> None:
    path = _immutable_path(vault_file)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def mark_immutable(vault_file: str, key: str, reason: Optional[str] = None) -> dict:
    """Mark a key as immutable."""
    data = _load_immutable(vault_file)
    entry = {
        "key": key,
        "reason": reason,
        "marked_at": datetime.now(timezone.utc).isoformat(),
    }
    data[key] = entry
    _save_immutable(vault_file, data)
    return entry


def unmark_immutable(vault_file: str, key: str) -> bool:
    """Remove immutability from a key. Returns True if it was present."""
    data = _load_immutable(vault_file)
    if key not in data:
        return False
    del data[key]
    _save_immutable(vault_file, data)
    return True


def is_immutable(vault_file: str, key: str) -> bool:
    """Return True if the key is currently marked immutable."""
    return key in _load_immutable(vault_file)


def get_immutable_entry(vault_file: str, key: str) -> Optional[dict]:
    """Return the immutable entry for a key, or None."""
    return _load_immutable(vault_file).get(key)


def list_immutable(vault_file: str) -> list[dict]:
    """Return all immutable entries sorted by key."""
    data = _load_immutable(vault_file)
    return [data[k] for k in sorted(data)]


def check_immutable(vault_file: str, key: str) -> None:
    """Raise ValueError if the key is immutable."""
    entry = get_immutable_entry(vault_file, key)
    if entry:
        reason = entry.get("reason")
        msg = f"Key '{key}' is immutable and cannot be modified or deleted."
        if reason:
            msg += f" Reason: {reason}"
        raise ValueError(msg)
