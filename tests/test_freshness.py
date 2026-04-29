"""Tests for envault.freshness."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.freshness import (
    get_freshness,
    is_stale,
    list_stale,
    remove_freshness,
    touch_var,
)


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    vf = tmp_path / ".envault"
    vf.write_text("{}")
    return str(vf)


def test_touch_var_returns_datetime(vault_file):
    result = touch_var(vault_file, "API_KEY")
    assert isinstance(result, datetime)


def test_get_freshness_returns_entry(vault_file):
    touch_var(vault_file, "DB_PASS", actor="alice")
    entry = get_freshness(vault_file, "DB_PASS")
    assert entry is not None
    assert entry["actor"] == "alice"
    assert "updated_at" in entry


def test_get_freshness_missing_returns_none(vault_file):
    assert get_freshness(vault_file, "NONEXISTENT") is None


def test_touch_var_persists(vault_file):
    touch_var(vault_file, "SECRET")
    freshness_file = Path(vault_file).parent / ".envault_freshness.json"
    data = json.loads(freshness_file.read_text())
    assert "SECRET" in data


def test_is_stale_false_when_just_touched(vault_file):
    touch_var(vault_file, "TOKEN")
    assert is_stale(vault_file, "TOKEN", max_days=30) is False


def test_is_stale_true_when_never_recorded(vault_file):
    assert is_stale(vault_file, "MISSING_KEY", max_days=1) is True


def test_is_stale_true_when_old(vault_file):
    # Manually write an old timestamp
    freshness_file = Path(vault_file).parent / ".envault_freshness.json"
    old_date = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
    freshness_file.write_text(json.dumps({"OLD_KEY": {"updated_at": old_date, "actor": "bot"}}))
    assert is_stale(vault_file, "OLD_KEY", max_days=30) is True


def test_list_stale_returns_old_keys(vault_file):
    freshness_file = Path(vault_file).parent / ".envault_freshness.json"
    old_date = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    fresh_date = datetime.now(timezone.utc).isoformat()
    freshness_file.write_text(json.dumps({
        "STALE_KEY": {"updated_at": old_date, "actor": "x"},
        "FRESH_KEY": {"updated_at": fresh_date, "actor": "x"},
    }))
    stale = list_stale(vault_file, max_days=30)
    assert "STALE_KEY" in stale
    assert "FRESH_KEY" not in stale


def test_remove_freshness_returns_true(vault_file):
    touch_var(vault_file, "REMOVABLE")
    assert remove_freshness(vault_file, "REMOVABLE") is True
    assert get_freshness(vault_file, "REMOVABLE") is None


def test_remove_freshness_nonexistent_returns_false(vault_file):
    assert remove_freshness(vault_file, "GHOST") is False


def test_touch_var_overwrites_existing(vault_file):
    t1 = touch_var(vault_file, "KEY")
    t2 = touch_var(vault_file, "KEY")
    entry = get_freshness(vault_file, "KEY")
    stored = datetime.fromisoformat(entry["updated_at"])
    assert stored >= t1
