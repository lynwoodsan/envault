"""Group management for vault variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _grouping_path(vault_file: str) -> Path:
    return Path(vault_file).parent / ".envault_groups.json"


def _load_groups(vault_file: str) -> Dict[str, List[str]]:
    path = _grouping_path(vault_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_groups(vault_file: str, data: Dict[str, List[str]]) -> None:
    _grouping_path(vault_file).write_text(json.dumps(data, indent=2))


def add_to_group(vault_file: str, group: str, key: str) -> List[str]:
    """Add a key to a named group. Returns the updated key list."""
    data = _load_groups(vault_file)
    members = data.get(group, [])
    if key not in members:
        members.append(key)
    data[group] = members
    _save_groups(vault_file, data)
    return members


def remove_from_group(vault_file: str, group: str, key: str) -> bool:
    """Remove a key from a group. Returns True if removed."""
    data = _load_groups(vault_file)
    members = data.get(group, [])
    if key not in members:
        return False
    members.remove(key)
    if members:
        data[group] = members
    else:
        data.pop(group, None)
    _save_groups(vault_file, data)
    return True


def get_group(vault_file: str, group: str) -> List[str]:
    """Return all keys in a group."""
    return _load_groups(vault_file).get(group, [])


def list_groups(vault_file: str) -> Dict[str, List[str]]:
    """Return all groups and their members."""
    return _load_groups(vault_file)


def get_groups_for_key(vault_file: str, key: str) -> List[str]:
    """Return all groups that contain the given key."""
    return [
        group
        for group, members in _load_groups(vault_file).items()
        if key in members
    ]


def delete_group(vault_file: str, group: str) -> bool:
    """Delete an entire group. Returns True if it existed."""
    data = _load_groups(vault_file)
    if group not in data:
        return False
    del data[group]
    _save_groups(vault_file, data)
    return True
