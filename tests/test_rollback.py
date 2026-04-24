"""Tests for envault.rollback."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import save_vault, load_vault
from envault.snapshot import create_snapshot
from envault.rollback import rollback_to_snapshot, list_rollback_points, RollbackResult


PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.json"
    save_vault(path, PASSWORD, {"ALPHA": "1", "BETA": "2"})
    return path


def test_rollback_result_type(vault_file: Path) -> None:
    snap = create_snapshot(vault_file, PASSWORD)
    save_vault(vault_file, PASSWORD, {"ALPHA": "99", "GAMMA": "3"})
    snap_id = Path(snap).stem[:8]
    result = rollback_to_snapshot(vault_file, PASSWORD, snap_id)
    assert isinstance(result, RollbackResult)


def test_rollback_restores_vars(vault_file: Path) -> None:
    snap = create_snapshot(vault_file, PASSWORD)
    save_vault(vault_file, PASSWORD, {"ALPHA": "changed", "NEW_KEY": "x"})
    snap_id = Path(snap).stem
    rollback_to_snapshot(vault_file, PASSWORD, snap_id)
    restored = load_vault(vault_file, PASSWORD)
    assert restored == {"ALPHA": "1", "BETA": "2"}


def test_rollback_counts_keys(vault_file: Path) -> None:
    snap = create_snapshot(vault_file, PASSWORD)
    save_vault(vault_file, PASSWORD, {"ALPHA": "1", "BETA": "2", "EXTRA": "3"})
    snap_id = Path(snap).stem
    result = rollback_to_snapshot(vault_file, PASSWORD, snap_id)
    assert result.keys_restored == 2
    assert result.keys_removed == 1


def test_rollback_with_label(vault_file: Path) -> None:
    snap = create_snapshot(vault_file, PASSWORD, label="before-release")
    snap_id = Path(snap).stem
    result = rollback_to_snapshot(vault_file, PASSWORD, snap_id)
    assert result.label == "before-release"


def test_rollback_no_label(vault_file: Path) -> None:
    snap = create_snapshot(vault_file, PASSWORD)
    snap_id = Path(snap).stem
    result = rollback_to_snapshot(vault_file, PASSWORD, snap_id)
    assert result.label is None


def test_rollback_missing_snapshot_raises(vault_file: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No snapshot found"):
        rollback_to_snapshot(vault_file, PASSWORD, "nonexistent-id")


def test_rollback_partial_id_match(vault_file: Path) -> None:
    snap = create_snapshot(vault_file, PASSWORD)
    save_vault(vault_file, PASSWORD, {})
    # Use only first 6 chars of stem as partial ID
    partial = Path(snap).stem[:6]
    result = rollback_to_snapshot(vault_file, PASSWORD, partial)
    assert result.keys_restored == 2


def test_list_rollback_points_empty(tmp_path: Path) -> None:
    path = tmp_path / "vault.json"
    save_vault(path, PASSWORD, {})
    points = list_rollback_points(path)
    assert points == []


def test_list_rollback_points_returns_entries(vault_file: Path) -> None:
    create_snapshot(vault_file, PASSWORD)
    create_snapshot(vault_file, PASSWORD, label="v2")
    points = list_rollback_points(vault_file)
    assert len(points) == 2
