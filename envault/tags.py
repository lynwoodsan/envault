"""Tag support for envault variables."""
from __future__ import annotations
from envault.vault import load_vault, save_vault

META_KEY = "__tags__"


def _load_tags(vault_file: str, password: str) -> dict[str, list[str]]:
    vault = load_vault(vault_file, password)
    raw = vault.get(META_KEY, {})
    return raw if isinstance(raw, dict) else {}


def _save_tags(vault_file: str, password: str, tags: dict[str, list[str]]) -> None:
    vault = load_vault(vault_file, password)
    vault[META_KEY] = tags
    save_vault(vault_file, password, vault)


def add_tag(vault_file: str, password: str, key: str, tag: str) -> None:
    """Add a tag to a variable."""
    tags = _load_tags(vault_file, password)
    entry = tags.setdefault(key, [])
    if tag not in entry:
        entry.append(tag)
    _save_tags(vault_file, password, tags)


def remove_tag(vault_file: str, password: str, key: str, tag: str) -> bool:
    """Remove a tag from a variable. Returns True if removed."""
    tags = _load_tags(vault_file, password)
    entry = tags.get(key, [])
    if tag in entry:
        entry.remove(tag)
        tags[key] = entry
        _save_tags(vault_file, password, tags)
        return True
    return False


def get_tags(vault_file: str, password: str, key: str) -> list[str]:
    """Return tags for a variable."""
    return _load_tags(vault_file, password).get(key, [])


def list_by_tag(vault_file: str, password: str, tag: str) -> list[str]:
    """Return all variable names that have the given tag."""
    tags = _load_tags(vault_file, password)
    return [k for k, v in tags.items() if tag in v]


def all_tags(vault_file: str, password: str) -> dict[str, list[str]]:
    """Return full tag map (key -> [tags])."""
    return _load_tags(vault_file, password)
