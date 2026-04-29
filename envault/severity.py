"""Severity levels for vault variables — assign, query, and report."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

VALID_LEVELS = ("low", "medium", "high", "critical")


def _severity_path(vault_path: Path) -> Path:
    return vault_path.parent / ".envault_severity.json"


def _load_severity(vault_path: Path) -> Dict[str, dict]:
    p = _severity_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_severity(vault_path: Path, data: Dict[str, dict]) -> None:
    _severity_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class SeverityEntry:
    key: str
    level: str
    note: Optional[str]
    set_at: str


def set_severity(vault_path: Path, key: str, level: str, note: Optional[str] = None) -> SeverityEntry:
    """Assign a severity level to a variable."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid severity level '{level}'. Choose from: {VALID_LEVELS}")
    data = _load_severity(vault_path)
    entry = {
        "level": level,
        "note": note,
        "set_at": datetime.now(timezone.utc).isoformat(),
    }
    data[key] = entry
    _save_severity(vault_path, data)
    return SeverityEntry(key=key, **entry)


def remove_severity(vault_path: Path, key: str) -> bool:
    """Remove severity assignment for a variable. Returns True if removed."""
    data = _load_severity(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_severity(vault_path, data)
    return True


def get_severity(vault_path: Path, key: str) -> Optional[SeverityEntry]:
    """Return the severity entry for a key, or None."""
    data = _load_severity(vault_path)
    if key not in data:
        return None
    e = data[key]
    return SeverityEntry(key=key, level=e["level"], note=e.get("note"), set_at=e["set_at"])


def list_severity(vault_path: Path) -> List[SeverityEntry]:
    """Return all severity entries sorted by level then key."""
    data = _load_severity(vault_path)
    order = {lvl: i for i, lvl in enumerate(VALID_LEVELS)}
    entries = [
        SeverityEntry(key=k, level=v["level"], note=v.get("note"), set_at=v["set_at"])
        for k, v in data.items()
    ]
    return sorted(entries, key=lambda e: (order.get(e.level, 99), e.key))


def get_keys_by_level(vault_path: Path, level: str) -> List[str]:
    """Return all keys assigned the given severity level."""
    return [e.key for e in list_severity(vault_path) if e.level == level]
