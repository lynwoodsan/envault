"""Tests for envault.retention module."""
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from envault.retention import (
    set_retention,
    remove_retention,
    get_retention,
    list_retention,
    get_due_keys,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.write_text("placeholder")
    return str(vf)


def test_set_retention_returns_entry(vault_file):
    entry = set_retention(vault_file, "API_KEY", 30)
    assert entry["key"] == "API_KEY"
    assert entry["days"] == 30
    assert entry["action"] == "warn"
    assert "due_at" in entry
    assert "set_at" in entry


def test_set_retention_custom_action(vault_file):
    entry = set_retention(vault_file, "SECRET", 7, action="delete")
    assert entry["action"] == "delete"


def test_set_retention_invalid_days_raises(vault_file):
    with pytest.raises(ValueError, match="positive"):
        set_retention(vault_file, "KEY", 0)


def test_set_retention_invalid_action_raises(vault_file):
    with pytest.raises(ValueError, match="action"):
        set_retention(vault_file, "KEY", 10, action="explode")


def test_get_retention_returns_entry(vault_file):
    set_retention(vault_file, "DB_PASS", 60)
    entry = get_retention(vault_file, "DB_PASS")
    assert entry is not None
    assert entry["key"] == "DB_PASS"


def test_get_retention_missing_returns_none(vault_file):
    assert get_retention(vault_file, "MISSING") is None


def test_remove_retention_returns_true(vault_file):
    set_retention(vault_file, "TOKEN", 14)
    assert remove_retention(vault_file, "TOKEN") is True
    assert get_retention(vault_file, "TOKEN") is None


def test_remove_retention_nonexistent_returns_false(vault_file):
    assert remove_retention(vault_file, "GHOST") is False


def test_list_retention_empty(vault_file):
    assert list_retention(vault_file) == []


def test_list_retention_multiple(vault_file):
    set_retention(vault_file, "A", 10)
    set_retention(vault_file, "B", 20)
    entries = list_retention(vault_file)
    assert len(entries) == 2
    keys = {e["key"] for e in entries}
    assert keys == {"A", "B"}


def test_get_due_keys_past_due(vault_file):
    entry = set_retention(vault_file, "OLD_KEY", 1)
    import json
    from pathlib import Path
    p = Path(vault_file).parent / ".envault_retention.json"
    data = json.loads(p.read_text())
    data["OLD_KEY"]["due_at"] = (datetime.utcnow() - timedelta(days=1)).isoformat()
    p.write_text(json.dumps(data))
    due = get_due_keys(vault_file)
    assert any(e["key"] == "OLD_KEY" for e in due)


def test_get_due_keys_not_yet_due(vault_file):
    set_retention(vault_file, "FRESH", 90)
    due = get_due_keys(vault_file)
    assert not any(e["key"] == "FRESH" for e in due)
