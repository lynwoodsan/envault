"""Vault inheritance: allow a vault to extend another vault's variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_INHERIT_FILE = ".envault-inherit.json"


def _inherit_path(vault_dir: Path) -> Path:
    return vault_dir / _INHERIT_FILE


def _load_inheritance(vault_dir: Path) -> Dict:
    p = _inherit_path(vault_dir)
    if not p.exists():
        return {"parents": [], "overrides": []}
    return json.loads(p.read_text())


def _save_inheritance(vault_dir: Path, data: Dict) -> None:
    _inherit_path(vault_dir).write_text(json.dumps(data, indent=2))


def add_parent(vault_dir: Path, parent_path: str) -> None:
    """Register a parent vault path for inheritance."""
    data = _load_inheritance(vault_dir)
    if parent_path not in data["parents"]:
        data["parents"].append(parent_path)
    _save_inheritance(vault_dir, data)


def remove_parent(vault_dir: Path, parent_path: str) -> bool:
    """Remove a parent vault from the inheritance chain. Returns True if removed."""
    data = _load_inheritance(vault_dir)
    if parent_path in data["parents"]:
        data["parents"].remove(parent_path)
        _save_inheritance(vault_dir, data)
        return True
    return False


def list_parents(vault_dir: Path) -> List[str]:
    """Return ordered list of parent vault paths."""
    return _load_inheritance(vault_dir)["parents"]


def add_override(vault_dir: Path, key: str) -> None:
    """Mark a key as locally overridden (not inherited even if parent defines it)."""
    data = _load_inheritance(vault_dir)
    if key not in data["overrides"]:
        data["overrides"].append(key)
    _save_inheritance(vault_dir, data)


def remove_override(vault_dir: Path, key: str) -> bool:
    data = _load_inheritance(vault_dir)
    if key in data["overrides"]:
        data["overrides"].remove(key)
        _save_inheritance(vault_dir, data)
        return True
    return False


def get_overrides(vault_dir: Path) -> List[str]:
    return _load_inheritance(vault_dir)["overrides"]


def resolve_vars(
    local_vars: Dict[str, str],
    parent_vars: Dict[str, str],
    overrides: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Merge parent vars into local vars, respecting override list.

    Local keys always win. Keys in *overrides* are never pulled from parent.
    """
    overrides = overrides or []
    merged = {k: v for k, v in parent_vars.items() if k not in overrides}
    merged.update(local_vars)
    return merged
