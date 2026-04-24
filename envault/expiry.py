"""expiry.py — Track and enforce expiry dates on individual vault variables."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_EXPIRY_FILE = ".envault_expiry.json"


def _expiry_path(vault_path: str) -> Path:
    return Path(vault_path).parent / _EXPIRY_FILE


def _load_expiry(vault_path: str) -> dict:
    p = _expiry_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_expiry(vault_path: str, data: dict) -> None:
    _expiry_path(vault_path).write_text(json.dumps(data, indent=2))


def set_expiry(vault_path: str, key: str, days: int) -> datetime:
    """Set an expiry date *days* from now for *key*. Returns the expiry datetime."""
    if days <= 0:
        raise ValueError("days must be a positive integer")
    data = _load_expiry(vault_path)
    expires_at = datetime.now(timezone.utc).replace(microsecond=0)
    from datetime import timedelta
    expires_at = expires_at + timedelta(days=days)
    data[key] = expires_at.isoformat()
    _save_expiry(vault_path, data)
    return expires_at


def remove_expiry(vault_path: str, key: str) -> bool:
    """Remove expiry for *key*. Returns True if it existed."""
    data = _load_expiry(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_expiry(vault_path, data)
    return True


def get_expiry(vault_path: str, key: str) -> Optional[datetime]:
    """Return the expiry datetime for *key*, or None if not set."""
    data = _load_expiry(vault_path)
    if key not in data:
        return None
    return datetime.fromisoformat(data[key])


def is_expired(vault_path: str, key: str) -> bool:
    """Return True if *key* has passed its expiry date."""
    expiry = get_expiry(vault_path, key)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expiry(vault_path: str) -> dict[str, datetime]:
    """Return a mapping of key -> expiry datetime for all keys with expiry set."""
    data = _load_expiry(vault_path)
    return {k: datetime.fromisoformat(v) for k, v in data.items()}


def get_expired_keys(vault_path: str) -> list[str]:
    """Return a list of keys whose expiry date has passed."""
    now = datetime.now(timezone.utc)
    return [
        key
        for key, expiry in list_expiry(vault_path).items()
        if now >= expiry
    ]
