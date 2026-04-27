"""Ownership tracking for vault variables."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _ownership_path(vault_file: str) -> Path:
    return Path(vault_file).parent / ".envault_ownership.json"


def _load_ownership(vault_file: str) -> dict:
    p = _ownership_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ownership(vault_file: str, data: dict) -> None:
    _ownership_path(vault_file).write_text(json.dumps(data, indent=2))


def set_owner(vault_file: str, key: str, owner: str, note: str = "") -> dict:
    """Assign an owner to a variable."""
    data = _load_ownership(vault_file)
    entry = {
        "owner": owner,
        "note": note,
        "assigned_at": datetime.now(timezone.utc).isoformat(),
    }
    data[key] = entry
    _save_ownership(vault_file, data)
    return entry


def remove_owner(vault_file: str, key: str) -> bool:
    """Remove ownership record for a variable. Returns True if removed."""
    data = _load_ownership(vault_file)
    if key not in data:
        return False
    del data[key]
    _save_ownership(vault_file, data)
    return True


def get_owner(vault_file: str, key: str) -> Optional[dict]:
    """Return ownership entry for a key, or None."""
    return _load_ownership(vault_file).get(key)


def list_owned(vault_file: str) -> dict[str, dict]:
    """Return all ownership entries keyed by variable name."""
    return _load_ownership(vault_file)


def get_keys_by_owner(vault_file: str, owner: str) -> list[str]:
    """Return all keys assigned to a given owner."""
    data = _load_ownership(vault_file)
    return [k for k, v in data.items() if v.get("owner") == owner]
