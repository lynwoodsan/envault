"""Annotation support for vault variables — attach free-form notes/comments."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


def _annotation_path(vault_file: str) -> Path:
    return Path(vault_file).parent / ".envault_annotations.json"


def _load_annotations(vault_file: str) -> dict:
    path = _annotation_path(vault_file)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_annotations(vault_file: str, data: dict) -> None:
    path = _annotation_path(vault_file)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_annotation(vault_file: str, key: str, note: str, author: str = "envault") -> dict:
    """Set or overwrite an annotation for a variable key."""
    data = _load_annotations(vault_file)
    entry = {
        "note": note,
        "author": author,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    data[key] = entry
    _save_annotations(vault_file, data)
    return entry


def get_annotation(vault_file: str, key: str) -> Optional[dict]:
    """Return the annotation for a key, or None if not set."""
    return _load_annotations(vault_file).get(key)


def remove_annotation(vault_file: str, key: str) -> bool:
    """Remove annotation for a key. Returns True if it existed."""
    data = _load_annotations(vault_file)
    if key not in data:
        return False
    del data[key]
    _save_annotations(vault_file, data)
    return True


def list_annotations(vault_file: str) -> dict:
    """Return all annotations keyed by variable name."""
    return _load_annotations(vault_file)


def clear_annotations(vault_file: str) -> int:
    """Remove all annotations. Returns count of removed entries."""
    data = _load_annotations(vault_file)
    count = len(data)
    _save_annotations(vault_file, {})
    return count
