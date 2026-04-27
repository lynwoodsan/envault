"""Visibility control for vault variables (public / private / secret)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VISIBILITY_LEVELS = ("public", "private", "secret")


def _visibility_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".visibility.json")


def _load_visibility(vault_path: str) -> Dict[str, str]:
    path = _visibility_path(vault_path)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_visibility(vault_path: str, data: Dict[str, str]) -> None:
    path = _visibility_path(vault_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_visibility(vault_path: str, key: str, level: str) -> str:
    """Set visibility level for a key. Returns the level."""
    if level not in VISIBILITY_LEVELS:
        raise ValueError(
            f"Invalid visibility level '{level}'. Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    data = _load_visibility(vault_path)
    data[key] = level
    _save_visibility(vault_path, data)
    return level


def get_visibility(vault_path: str, key: str) -> Optional[str]:
    """Return the visibility level for a key, or None if not set."""
    data = _load_visibility(vault_path)
    return data.get(key)


def remove_visibility(vault_path: str, key: str) -> bool:
    """Remove visibility setting for a key. Returns True if it existed."""
    data = _load_visibility(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_visibility(vault_path, data)
    return True


def list_visibility(vault_path: str) -> Dict[str, str]:
    """Return all key -> visibility mappings."""
    return _load_visibility(vault_path)


def filter_by_visibility(vault_path: str, level: str) -> List[str]:
    """Return all keys with the given visibility level."""
    if level not in VISIBILITY_LEVELS:
        raise ValueError(
            f"Invalid visibility level '{level}'. Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    data = _load_visibility(vault_path)
    return [k for k, v in data.items() if v == level]
