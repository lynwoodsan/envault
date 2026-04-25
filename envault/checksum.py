"""Checksum tracking for vault variables.

Records a hash of each variable's value at a point in time, allowing
detection of out-of-band modifications or drift from a known-good state.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _checksum_path(vault_file: Path) -> Path:
    return vault_file.parent / ".envault_checksums.json"


def _load_checksums(vault_file: Path) -> dict:
    path = _checksum_path(vault_file)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_checksums(vault_file: Path, data: dict) -> None:
    path = _checksum_path(vault_file)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def record_checksum(vault_file: Path, key: str, value: str) -> str:
    """Record a checksum for the given key/value pair. Returns the hex digest."""
    data = _load_checksums(vault_file)
    digest = _hash_value(value)
    data[key] = {
        "sha256": digest,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_checksums(vault_file, data)
    return digest


def get_checksum(vault_file: Path, key: str) -> Optional[dict]:
    """Return stored checksum entry for key, or None if not recorded."""
    data = _load_checksums(vault_file)
    return data.get(key)


def verify_checksum(vault_file: Path, key: str, current_value: str) -> bool:
    """Return True if current_value matches the stored checksum for key."""
    entry = get_checksum(vault_file, key)
    if entry is None:
        return False
    return entry["sha256"] == _hash_value(current_value)


def remove_checksum(vault_file: Path, key: str) -> bool:
    """Remove checksum record for key. Returns True if it existed."""
    data = _load_checksums(vault_file)
    if key not in data:
        return False
    del data[key]
    _save_checksums(vault_file, data)
    return True


def list_checksums(vault_file: Path) -> dict:
    """Return all recorded checksum entries keyed by variable name."""
    return _load_checksums(vault_file)


def check_all(vault_file: Path, current_vars: dict) -> dict:
    """Compare all stored checksums against current_vars values.

    Returns a dict mapping key -> 'ok' | 'mismatch' | 'unrecorded'.
    """
    results = {}
    data = _load_checksums(vault_file)
    for key, value in current_vars.items():
        if key not in data:
            results[key] = "unrecorded"
        elif data[key]["sha256"] == _hash_value(value):
            results[key] = "ok"
        else:
            results[key] = "mismatch"
    return results
