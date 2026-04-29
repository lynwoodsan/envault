"""Freshness tracking: record when a variable was last rotated/updated and warn if stale."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

FRESHNESS_FILE = ".envault_freshness.json"


def _freshness_path(vault_path: str) -> Path:
    return Path(vault_path).parent / FRESHNESS_FILE


def _load_freshness(vault_path: str) -> dict:
    p = _freshness_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_freshness(vault_path: str, data: dict) -> None:
    _freshness_path(vault_path).write_text(json.dumps(data, indent=2))


def touch_var(vault_path: str, key: str, actor: str = "envault") -> datetime:
    """Record the current time as the last-updated timestamp for *key*."""
    data = _load_freshness(vault_path)
    now = datetime.now(timezone.utc)
    data[key] = {"updated_at": now.isoformat(), "actor": actor}
    _save_freshness(vault_path, data)
    return now


def get_freshness(vault_path: str, key: str) -> Optional[dict]:
    """Return the freshness entry for *key*, or None if never recorded."""
    return _load_freshness(vault_path).get(key)


def is_stale(vault_path: str, key: str, max_days: int) -> bool:
    """Return True if *key* has not been updated within *max_days* days."""
    entry = get_freshness(vault_path, key)
    if entry is None:
        return True
    updated = datetime.fromisoformat(entry["updated_at"])
    delta = datetime.now(timezone.utc) - updated
    return delta.days >= max_days


def list_stale(vault_path: str, max_days: int) -> list[str]:
    """Return a list of keys that are stale according to *max_days*."""
    data = _load_freshness(vault_path)
    return [k for k in data if is_stale(vault_path, k, max_days)]


def remove_freshness(vault_path: str, key: str) -> bool:
    """Remove freshness tracking for *key*. Returns True if it existed."""
    data = _load_freshness(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_freshness(vault_path, data)
    return True
