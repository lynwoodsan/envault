"""Rollback support: restore vault state from a snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envault.snapshot import list_snapshots, load_snapshot, _snapshot_dir
from envault.vault import save_vault, load_vault
from envault.audit import log_event


@dataclass
class RollbackResult:
    snapshot_id: str
    keys_restored: int
    keys_removed: int
    label: Optional[str]


def rollback_to_snapshot(
    vault_path: Path,
    password: str,
    snapshot_id: str,
    actor: str = "envault",
) -> RollbackResult:
    """Restore the vault to the state captured in the given snapshot.

    Args:
        vault_path: Path to the vault file.
        password: Master password for the vault.
        snapshot_id: Snapshot identifier (timestamp prefix or full name).
        actor: Identity to record in the audit log.

    Returns:
        A RollbackResult describing what changed.

    Raises:
        FileNotFoundError: If the snapshot cannot be located.
        ValueError: If the password is wrong for the current vault.
    """
    snap_dir = _snapshot_dir(vault_path)
    matches = [p for p in snap_dir.glob("*.json") if p.stem.startswith(snapshot_id)]
    if not matches:
        raise FileNotFoundError(f"No snapshot found matching '{snapshot_id}'")
    snap_path = sorted(matches)[0]

    snap_data = load_snapshot(snap_path)
    snap_vars: dict[str, str] = snap_data.get("vars", {})
    label: Optional[str] = snap_data.get("label")

    current_vars = load_vault(vault_path, password)
    keys_before = set(current_vars.keys())
    keys_after = set(snap_vars.keys())

    keys_removed = len(keys_before - keys_after)
    keys_restored = len(keys_after)

    save_vault(vault_path, password, snap_vars)

    log_event(
        vault_path,
        action="rollback",
        key="*",
        actor=actor,
        meta={"snapshot_id": snap_path.stem, "label": label},
    )

    return RollbackResult(
        snapshot_id=snap_path.stem,
        keys_restored=keys_restored,
        keys_removed=keys_removed,
        label=label,
    )


def list_rollback_points(vault_path: Path) -> list[dict]:
    """Return available snapshots that can be rolled back to."""
    return list_snapshots(vault_path)
