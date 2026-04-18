"""TTL (time-to-live) support for vault variables."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

_TTL_FILENAME = ".envault_ttl.json"


def _ttl_path(vault_path: Path) -> Path:
    return vault_path.parent / _TTL_FILENAME


def _load_ttl(vault_path: Path) -> dict:
    p = _ttl_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(vault_path: Path, data: dict) -> None:
    _ttl_path(vault_path).write_text(json.dumps(data, indent=2))


def set_ttl(vault_path: Path, key: str, seconds: int) -> float:
    """Set expiry for a key. Returns the expiry timestamp."""
    data = _load_ttl(vault_path)
    expires_at = time.time() + seconds
    data[key] = expires_at
    _save_ttl(vault_path, data)
    return expires_at


def remove_ttl(vault_path: Path, key: str) -> None:
    data = _load_ttl(vault_path)
    data.pop(key, None)
    _save_ttl(vault_path, data)


def get_ttl(vault_path: Path, key: str) -> Optional[float]:
    """Return expiry timestamp or None if no TTL set."""
    return _load_ttl(vault_path).get(key)


def is_expired(vault_path: Path, key: str) -> bool:
    """Return True if the key has a TTL and it has passed."""
    expires_at = get_ttl(vault_path, key)
    if expires_at is None:
        return False
    return time.time() > expires_at


def list_ttls(vault_path: Path) -> dict[str, float]:
    """Return all key -> expiry timestamp mappings."""
    return _load_ttl(vault_path)


def purge_expired(vault_path: Path) -> list[str]:
    """Remove TTL records for expired keys and return their names."""
    data = _load_ttl(vault_path)
    now = time.time()
    expired = [k for k, exp in data.items() if now > exp]
    for k in expired:
        del data[k]
    _save_ttl(vault_path, data)
    return expired
