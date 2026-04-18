"""Search and filter environment variables in the vault."""

from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional

from envault.vault import list_vars


def search_vars(
    vault_path: str,
    password: str,
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return variables whose keys match *pattern* (glob-style).

    Args:
        vault_path: Path to the vault file.
        password: Master password.
        pattern: Glob pattern, e.g. ``"DB_*"`` or ``"*SECRET*"``.
        case_sensitive: When False (default) matching ignores case.

    Returns:
        Ordered dict of matching key/value pairs.
    """
    all_vars: Dict[str, str] = list_vars(vault_path, password)

    if not case_sensitive:
        pattern = pattern.lower()

    result: Dict[str, str] = {}
    for key, value in all_vars.items():
        candidate = key if case_sensitive else key.lower()
        if fnmatch.fnmatch(candidate, pattern):
            result[key] = value

    return result


def search_by_value(
    vault_path: str,
    password: str,
    substring: str,
    *,
    case_sensitive: bool = False,
) -> List[str]:
    """Return keys whose *decrypted* values contain *substring*.

    Useful for auditing accidental plaintext secrets.

    Args:
        vault_path: Path to the vault file.
        password: Master password.
        substring: String to look for inside values.
        case_sensitive: When False (default) matching ignores case.

    Returns:
        List of matching variable names.
    """
    all_vars: Dict[str, str] = list_vars(vault_path, password)

    needle = substring if case_sensitive else substring.lower()
    matches: List[str] = []
    for key, value in all_vars.items():
        haystack = value if case_sensitive else value.lower()
        if needle in haystack:
            matches.append(key)

    return matches
