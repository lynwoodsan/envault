"""Alias support: map short names to vault keys."""
import json
from pathlib import Path


def _alias_path(vault_file: Path) -> Path:
    return vault_file.parent / ".envault_aliases.json"


def _load_aliases(vault_file: Path) -> dict:
    p = _alias_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(vault_file: Path, data: dict) -> None:
    _alias_path(vault_file).write_text(json.dumps(data, indent=2))


def add_alias(vault_file: Path, alias: str, key: str) -> None:
    """Map alias -> key."""
    data = _load_aliases(vault_file)
    data[alias] = key
    _save_aliases(vault_file, data)


def remove_alias(vault_file: Path, alias: str) -> bool:
    data = _load_aliases(vault_file)
    if alias not in data:
        return False
    del data[alias]
    _save_aliases(vault_file, data)
    return True


def resolve_alias(vault_file: Path, alias: str) -> str | None:
    """Return the key for alias, or None if not found."""
    return _load_aliases(vault_file).get(alias)


def list_aliases(vault_file: Path) -> dict:
    return _load_aliases(vault_file)


def reverse_lookup(vault_file: Path, key: str) -> list[str]:
    """Return all aliases pointing to key."""
    data = _load_aliases(vault_file)
    return [a for a, k in data.items() if k == key]
