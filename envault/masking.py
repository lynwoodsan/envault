"""Masking support for sensitive vault variables.

Allows marking keys as masked so their values are redacted
when displayed in CLI output or exported to logs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_MASK_FILENAME = ".envault_masks"
MASK_PLACEHOLDER = "********"


def _mask_path(vault_file: Path) -> Path:
    return vault_file.parent / _MASK_FILENAME


def _load_masks(vault_file: Path) -> Dict[str, dict]:
    path = _mask_path(vault_file)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_masks(vault_file: Path, data: Dict[str, dict]) -> None:
    path = _mask_path(vault_file)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def mask_var(vault_file: Path, key: str, reason: Optional[str] = None) -> None:
    """Mark a variable as masked."""
    masks = _load_masks(vault_file)
    masks[key] = {"reason": reason or ""}
    _save_masks(vault_file, masks)


def unmask_var(vault_file: Path, key: str) -> bool:
    """Remove mask from a variable. Returns True if it was masked."""
    masks = _load_masks(vault_file)
    if key not in masks:
        return False
    del masks[key]
    _save_masks(vault_file, masks)
    return True


def is_masked(vault_file: Path, key: str) -> bool:
    """Return True if the key is currently masked."""
    return key in _load_masks(vault_file)


def get_masked_keys(vault_file: Path) -> List[str]:
    """Return a list of all masked keys."""
    return list(_load_masks(vault_file).keys())


def apply_masks(vault_file: Path, variables: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of variables with masked values replaced by placeholder."""
    masks = _load_masks(vault_file)
    return {
        k: (MASK_PLACEHOLDER if k in masks else v)
        for k, v in variables.items()
    }


def get_mask_reason(vault_file: Path, key: str) -> Optional[str]:
    """Return the reason a key was masked, or None if not masked."""
    masks = _load_masks(vault_file)
    entry = masks.get(key)
    if entry is None:
        return None
    return entry.get("reason") or None
