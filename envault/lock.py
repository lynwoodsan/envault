"""Vault locking: prevent writes to a vault or specific keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_LOCK_FILE = ".envault-locks.json"


def _lock_path(vault_path: Path) -> Path:
    return vault_path.parent / _LOCK_FILE


def _load_locks(vault_path: Path) -> dict:
    p = _lock_path(vault_path)
    if not p.exists():
        return {"vault": False, "keys": {}}
    with p.open() as f:
        return json.load(f)


def _save_locks(vault_path: Path, data: dict) -> None:
    p = _lock_path(vault_path)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def lock_vault(vault_path: Path, reason: Optional[str] = None) -> None:
    """Lock the entire vault (no writes allowed)."""
    data = _load_locks(vault_path)
    data["vault"] = True
    data["vault_reason"] = reason or ""
    _save_locks(vault_path, data)


def unlock_vault(vault_path: Path) -> None:
    """Unlock the entire vault."""
    data = _load_locks(vault_path)
    data["vault"] = False
    data["vault_reason"] = ""
    _save_locks(vault_path, data)


def lock_key(vault_path: Path, key: str, reason: Optional[str] = None) -> None:
    """Lock a specific key so it cannot be modified or deleted."""
    data = _load_locks(vault_path)
    data["keys"][key] = {"locked": True, "reason": reason or ""}
    _save_locks(vault_path, data)


def unlock_key(vault_path: Path, key: str) -> bool:
    """Unlock a specific key. Returns False if key was not locked."""
    data = _load_locks(vault_path)
    if key not in data["keys"]:
        return False
    del data["keys"][key]
    _save_locks(vault_path, data)
    return True


def is_vault_locked(vault_path: Path) -> bool:
    return _load_locks(vault_path).get("vault", False)


def is_key_locked(vault_path: Path, key: str) -> bool:
    data = _load_locks(vault_path)
    return data["keys"].get(key, {}).get("locked", False)


def list_locked_keys(vault_path: Path) -> dict[str, str]:
    """Return {key: reason} for all locked keys."""
    data = _load_locks(vault_path)
    return {k: v.get("reason", "") for k, v in data["keys"].items() if v.get("locked")}


def get_vault_lock_reason(vault_path: Path) -> str:
    return _load_locks(vault_path).get("vault_reason", "")
