"""Access control: define per-key read/write permissions for team members."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_ACCESS_FILENAME = ".envault-access.json"

ACCESS_READ = "read"
ACCESS_WRITE = "write"
ACCESS_NONE = "none"

VALID_LEVELS = {ACCESS_READ, ACCESS_WRITE, ACCESS_NONE}


def _access_path(vault_path: Path) -> Path:
    return vault_path.parent / _ACCESS_FILENAME


def _load_access(vault_path: Path) -> Dict:
    path = _access_path(vault_path)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_access(vault_path: Path, data: Dict) -> None:
    path = _access_path(vault_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_access(vault_path: Path, key: str, actor: str, level: str) -> None:
    """Set the access level for an actor on a specific key."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid access level '{level}'. Must be one of {VALID_LEVELS}.")
    data = _load_access(vault_path)
    data.setdefault(key, {})[actor] = level
    _save_access(vault_path, data)


def remove_access(vault_path: Path, key: str, actor: str) -> bool:
    """Remove access entry for an actor on a key. Returns True if removed."""
    data = _load_access(vault_path)
    if key in data and actor in data[key]:
        del data[key][actor]
        if not data[key]:
            del data[key]
        _save_access(vault_path, data)
        return True
    return False


def get_access(vault_path: Path, key: str, actor: str) -> Optional[str]:
    """Get the access level for an actor on a key. Returns None if not set."""
    data = _load_access(vault_path)
    return data.get(key, {}).get(actor)


def list_access(vault_path: Path, key: Optional[str] = None) -> Dict:
    """List all access rules, optionally filtered by key."""
    data = _load_access(vault_path)
    if key is not None:
        return {key: data.get(key, {})}
    return data


def actors_with_access(vault_path: Path, key: str, level: str) -> List[str]:
    """Return all actors that have at least the given level for a key."""
    data = _load_access(vault_path)
    levels_order = [ACCESS_NONE, ACCESS_READ, ACCESS_WRITE]
    min_idx = levels_order.index(level)
    return [
        actor
        for actor, lvl in data.get(key, {}).items()
        if levels_order.index(lvl) >= min_idx
    ]
