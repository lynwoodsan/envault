"""Trust level management for vault variables."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("untrusted", "provisional", "trusted", "verified")


def _trust_path(vault_file: Path) -> Path:
    return vault_file.parent / ".envault_trust.json"


def _load_trust(vault_file: Path) -> dict:
    path = _trust_path(vault_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_trust(vault_file: Path, data: dict) -> None:
    _trust_path(vault_file).write_text(json.dumps(data, indent=2))


@dataclass
class TrustEntry:
    key: str
    level: str
    note: Optional[str]
    set_at: str
    set_by: str


def set_trust(vault_file: Path, key: str, level: str, note: str = "", actor: str = "user") -> TrustEntry:
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid trust level '{level}'. Must be one of: {VALID_LEVELS}")
    data = _load_trust(vault_file)
    entry = {
        "level": level,
        "note": note or None,
        "set_at": datetime.now(timezone.utc).isoformat(),
        "set_by": actor,
    }
    data[key] = entry
    _save_trust(vault_file, data)
    return TrustEntry(key=key, **entry)


def remove_trust(vault_file: Path, key: str) -> bool:
    data = _load_trust(vault_file)
    if key not in data:
        return False
    del data[key]
    _save_trust(vault_file, data)
    return True


def get_trust(vault_file: Path, key: str) -> Optional[TrustEntry]:
    data = _load_trust(vault_file)
    if key not in data:
        return None
    e = data[key]
    return TrustEntry(key=key, level=e["level"], note=e.get("note"), set_at=e["set_at"], set_by=e["set_by"])


def list_trust(vault_file: Path) -> list[TrustEntry]:
    data = _load_trust(vault_file)
    return [
        TrustEntry(key=k, level=v["level"], note=v.get("note"), set_at=v["set_at"], set_by=v["set_by"])
        for k, v in data.items()
    ]


def get_keys_by_level(vault_file: Path, level: str) -> list[str]:
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid trust level '{level}'.")
    data = _load_trust(vault_file)
    return [k for k, v in data.items() if v["level"] == level]
