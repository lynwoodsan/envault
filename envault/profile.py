"""Profile support: named sets of variables (e.g. dev, staging, prod)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional

PROFILE_FILE = ".envault-profiles.json"


def _profile_path(vault_path: str) -> Path:
    return Path(vault_path).parent / PROFILE_FILE


def _load_profiles(vault_path: str) -> Dict[str, List[str]]:
    p = _profile_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_profiles(vault_path: str, profiles: Dict[str, List[str]]) -> None:
    _profile_path(vault_path).write_text(json.dumps(profiles, indent=2))


def create_profile(vault_path: str, name: str) -> None:
    profiles = _load_profiles(vault_path)
    if name not in profiles:
        profiles[name] = []
    _save_profiles(vault_path, profiles)


def delete_profile(vault_path: str, name: str) -> bool:
    profiles = _load_profiles(vault_path)
    if name not in profiles:
        return False
    del profiles[name]
    _save_profiles(vault_path, profiles)
    return True


def assign_key(vault_path: str, name: str, key: str) -> None:
    profiles = _load_profiles(vault_path)
    profiles.setdefault(name, [])
    if key not in profiles[name]:
        profiles[name].append(key)
    _save_profiles(vault_path, profiles)


def unassign_key(vault_path: str, name: str, key: str) -> bool:
    profiles = _load_profiles(vault_path)
    if name not in profiles or key not in profiles[name]:
        return False
    profiles[name].remove(key)
    _save_profiles(vault_path, profiles)
    return True


def get_profile_keys(vault_path: str, name: str) -> Optional[List[str]]:
    profiles = _load_profiles(vault_path)
    return profiles.get(name)


def list_profiles(vault_path: str) -> Dict[str, List[str]]:
    return _load_profiles(vault_path)
