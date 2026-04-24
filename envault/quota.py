"""Quota management for envault vaults.

Allows setting a maximum number of variables allowed in a vault,
and checking whether the current vault is within its quota.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _quota_path(vault_file: Path) -> Path:
    return vault_file.parent / ".envault_quota.json"


def _load_quota(vault_file: Path) -> dict:
    p = _quota_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quota(vault_file: Path, data: dict) -> None:
    _quota_path(vault_file).write_text(json.dumps(data, indent=2))


@dataclass
class QuotaStatus:
    limit: Optional[int]
    current: int
    exceeded: bool
    remaining: Optional[int]


def set_quota(vault_file: Path, limit: int) -> None:
    """Set the maximum number of variables allowed in the vault."""
    if limit < 1:
        raise ValueError("Quota limit must be at least 1")
    data = _load_quota(vault_file)
    data["limit"] = limit
    _save_quota(vault_file, data)


def remove_quota(vault_file: Path) -> bool:
    """Remove the quota limit. Returns True if a quota existed."""
    data = _load_quota(vault_file)
    if "limit" not in data:
        return False
    del data["limit"]
    _save_quota(vault_file, data)
    return True


def get_quota(vault_file: Path) -> Optional[int]:
    """Return the configured quota limit, or None if unset."""
    return _load_quota(vault_file).get("limit")


def check_quota(vault_file: Path, current_count: int) -> QuotaStatus:
    """Return a QuotaStatus for the given vault and current variable count."""
    limit = get_quota(vault_file)
    if limit is None:
        return QuotaStatus(limit=None, current=current_count, exceeded=False, remaining=None)
    exceeded = current_count > limit
    remaining = max(0, limit - current_count)
    return QuotaStatus(limit=limit, current=current_count, exceeded=exceeded, remaining=remaining)


def format_quota_status(status: QuotaStatus) -> str:
    """Return a human-readable quota status string."""
    if status.limit is None:
        return f"No quota set. Current variables: {status.current}"
    bar = f"{status.current}/{status.limit}"
    if status.exceeded:
        return f"Quota EXCEEDED: {bar} (over by {status.current - status.limit})"
    return f"Quota OK: {bar} (remaining: {status.remaining})"
