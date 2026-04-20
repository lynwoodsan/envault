"""Namespace support for grouping environment variables under logical prefixes."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def _ns_path(vault_file: Path) -> Path:
    return vault_file.parent / ".envault_namespaces.json"


def _load_namespaces(vault_file: Path) -> Dict[str, List[str]]:
    """Load namespace -> [keys] mapping from disk."""
    path = _ns_path(vault_file)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_namespaces(vault_file: Path, data: Dict[str, List[str]]) -> None:
    path = _ns_path(vault_file)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def assign_namespace(vault_file: Path, key: str, namespace: str) -> None:
    """Assign a key to a namespace. A key can belong to multiple namespaces."""
    data = _load_namespaces(vault_file)
    members = data.setdefault(namespace, [])
    if key not in members:
        members.append(key)
    _save_namespaces(vault_file, data)


def unassign_namespace(vault_file: Path, key: str, namespace: str) -> bool:
    """Remove a key from a namespace. Returns True if removed, False if not found."""
    data = _load_namespaces(vault_file)
    members = data.get(namespace, [])
    if key not in members:
        return False
    members.remove(key)
    if not members:
        del data[namespace]
    _save_namespaces(vault_file, data)
    return True


def get_namespace_keys(vault_file: Path, namespace: str) -> List[str]:
    """Return all keys assigned to a namespace."""
    data = _load_namespaces(vault_file)
    return list(data.get(namespace, []))


def get_key_namespaces(vault_file: Path, key: str) -> List[str]:
    """Return all namespaces a key belongs to."""
    data = _load_namespaces(vault_file)
    return [ns for ns, members in data.items() if key in members]


def list_namespaces(vault_file: Path) -> List[str]:
    """Return all defined namespace names."""
    data = _load_namespaces(vault_file)
    return sorted(data.keys())


def delete_namespace(vault_file: Path, namespace: str) -> bool:
    """Delete an entire namespace. Returns True if it existed."""
    data = _load_namespaces(vault_file)
    if namespace not in data:
        return False
    del data[namespace]
    _save_namespaces(vault_file, data)
    return True
