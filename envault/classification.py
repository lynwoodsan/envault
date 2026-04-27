"""Variable classification: assign sensitivity levels to vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_LEVELS = ("public", "internal", "confidential", "secret")


def _classification_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".classifications.json")


def _load_classifications(vault_path: str) -> Dict[str, dict]:
    path = _classification_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_classifications(vault_path: str, data: Dict[str, dict]) -> None:
    _classification_path(vault_path).write_text(json.dumps(data, indent=2))


def classify_var(
    vault_path: str,
    key: str,
    level: str,
    note: Optional[str] = None,
) -> dict:
    """Assign a classification level to a key."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid level '{level}'. Choose from: {VALID_LEVELS}")
    data = _load_classifications(vault_path)
    entry = {"level": level, "note": note}
    data[key] = entry
    _save_classifications(vault_path, data)
    return entry


def unclassify_var(vault_path: str, key: str) -> bool:
    """Remove classification from a key. Returns True if it existed."""
    data = _load_classifications(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_classifications(vault_path, data)
    return True


def get_classification(vault_path: str, key: str) -> Optional[dict]:
    """Return the classification entry for a key, or None."""
    return _load_classifications(vault_path).get(key)


def list_classifications(vault_path: str) -> Dict[str, dict]:
    """Return all classifications."""
    return _load_classifications(vault_path)


def get_keys_by_level(vault_path: str, level: str) -> List[str]:
    """Return all keys classified at the given level."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid level '{level}'. Choose from: {VALID_LEVELS}")
    data = _load_classifications(vault_path)
    return [k for k, v in data.items() if v.get("level") == level]
