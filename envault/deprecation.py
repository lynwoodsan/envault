"""Deprecation tracking for vault variables."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _deprecation_path(vault_file: Path) -> Path:
    return vault_file.parent / ".envault_deprecations.json"


def _load_deprecations(vault_file: Path) -> dict:
    path = _deprecation_path(vault_file)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_deprecations(vault_file: Path, data: dict) -> None:
    path = _deprecation_path(vault_file)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def deprecate_var(
    vault_file: Path,
    key: str,
    reason: str = "",
    replacement: Optional[str] = None,
    sunset_date: Optional[str] = None,
) -> dict:
    """Mark a variable as deprecated."""
    data = _load_deprecations(vault_file)
    entry = {
        "key": key,
        "reason": reason,
        "replacement": replacement,
        "sunset_date": sunset_date,
        "deprecated_at": datetime.now(timezone.utc).isoformat(),
    }
    data[key] = entry
    _save_deprecations(vault_file, data)
    return entry


def undeprecate_var(vault_file: Path, key: str) -> bool:
    """Remove deprecation from a variable."""
    data = _load_deprecations(vault_file)
    if key not in data:
        return False
    del data[key]
    _save_deprecations(vault_file, data)
    return True


def get_deprecation(vault_file: Path, key: str) -> Optional[dict]:
    """Return the deprecation entry for a key, or None."""
    return _load_deprecations(vault_file).get(key)


def list_deprecated(vault_file: Path) -> list[dict]:
    """Return all deprecated variable entries."""
    return list(_load_deprecations(vault_file).values())


def is_deprecated(vault_file: Path, key: str) -> bool:
    """Return True if the key is marked as deprecated."""
    return key in _load_deprecations(vault_file)
