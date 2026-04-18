"""Diff two vault snapshots or compare vault against a .env file."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from envault.vault import load_vault
from envault.export import import_dotenv


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


def diff_vaults(
    vault_path_a: str,
    password_a: str,
    vault_path_b: str,
    password_b: str,
) -> List[DiffEntry]:
    """Compare two vault files and return a list of DiffEntry."""
    vars_a: Dict[str, str] = load_vault(vault_path_a, password_a)
    vars_b: Dict[str, str] = load_vault(vault_path_b, password_b)
    return _compare_dicts(vars_a, vars_b)


def diff_vault_dotenv(
    vault_path: str,
    password: str,
    dotenv_path: str,
) -> List[DiffEntry]:
    """Compare a vault against a .env file."""
    vault_vars: Dict[str, str] = load_vault(vault_path, password)
    dotenv_vars: Dict[str, str] = import_dotenv(dotenv_path)
    return _compare_dicts(vault_vars, dotenv_vars)


def _compare_dicts(
    old: Dict[str, str], new: Dict[str, str]
) -> List[DiffEntry]:
    entries: List[DiffEntry] = []
    all_keys = sorted(set(old) | set(new))
    for key in all_keys:
        if key in old and key not in new:
            entries.append(DiffEntry(key=key, status="removed", old_value=old[key]))
        elif key not in old and key in new:
            entries.append(DiffEntry(key=key, status="added", new_value=new[key]))
        elif old[key] != new[key]:
            entries.append(
                DiffEntry(key=key, status="changed", old_value=old[key], new_value=new[key])
            )
        else:
            entries.append(
                DiffEntry(key=key, status="unchanged", old_value=old[key], new_value=new[key])
            )
    return entries


def format_diff(entries: List[DiffEntry], show_values: bool = False) -> str:
    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    for e in entries:
        sym = symbols[e.status]
        if show_values and e.status == "changed":
            lines.append(f"{sym} {e.key}  ({e.old_value!r} -> {e.new_value!r})")
        else:
            lines.append(f"{sym} {e.key}")
    return "\n".join(lines)
