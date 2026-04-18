"""Pin/lock specific variables to prevent accidental overwrites."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List


def _pin_path(vault_file: Path) -> Path:
    return vault_file.parent / ".envault_pins.json"


def _load_pins(vault_file: Path) -> dict:
    p = _pin_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(vault_file: Path, pins: dict) -> None:
    _pin_path(vault_file).write_text(json.dumps(pins, indent=2))


def pin_var(vault_file: Path, key: str, reason: str = "") -> None:
    """Pin a variable key so it cannot be overwritten."""
    pins = _load_pins(vault_file)
    pins[key] = {"reason": reason}
    _save_pins(vault_file, pins)


def unpin_var(vault_file: Path, key: str) -> bool:
    """Unpin a variable. Returns True if it was pinned."""
    pins = _load_pins(vault_file)
    if key not in pins:
        return False
    del pins[key]
    _save_pins(vault_file, pins)
    return True


def is_pinned(vault_file: Path, key: str) -> bool:
    return key in _load_pins(vault_file)


def list_pins(vault_file: Path) -> List[dict]:
    pins = _load_pins(vault_file)
    return [{"key": k, "reason": v.get("reason", "")} for k, v in pins.items()]


def get_pin_reason(vault_file: Path, key: str) -> str:
    pins = _load_pins(vault_file)
    return pins.get(key, {}).get("reason", "")
