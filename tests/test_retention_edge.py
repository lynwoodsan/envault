"""Edge-case tests for envault.retention module."""
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from envault.retention import (
    set_retention,
    remove_retention,
    get_retention,
    list_retention,
    get_due_keys,
    VALID_ACTIONS,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.write_text("placeholder")
    return str(vf)


def test_valid_actions_tuple_contains_three():
    assert len(VALID_ACTIONS) == 3
    assert "warn" in VALID_ACTIONS
    assert "archive" in VALID_ACTIONS
    assert "delete" in VALID_ACTIONS


def test_set_retention_persists_to_disk(vault_file):
    set_retention(vault_file, "PERSIST", 5)
    p = Path(vault_file).parent / ".envault_retention.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert "PERSIST" in data


def test_set_retention_overwrites_existing(vault_file):
    set_retention(vault_file, "KEY", 10, action="warn")
    set_retention(vault_file, "KEY", 20, action="delete")
    entry = get_retention(vault_file, "KEY")
    assert entry["days"] == 20
    assert entry["action"] == "delete"


def test_due_at_is_approximately_correct(vault_file):
    before = datetime.utcnow()
    entry = set_retention(vault_file, "CALC", 30)
    after = datetime.utcnow()
    due = datetime.fromisoformat(entry["due_at"])
    assert before + timedelta(days=30) <= due <= after + timedelta(days=30)


def test_remove_then_list_is_empty(vault_file):
    set_retention(vault_file, "ONLY", 7)
    remove_retention(vault_file, "ONLY")
    assert list_retention(vault_file) == []


def test_multiple_due_keys_returned(vault_file):
    for key in ("X", "Y", "Z"):
        set_retention(vault_file, key, 1)
    p = Path(vault_file).parent / ".envault_retention.json"
    data = json.loads(p.read_text())
    past = (datetime.utcnow() - timedelta(days=1)).isoformat()
    for key in ("X", "Y"):
        data[key]["due_at"] = past
    p.write_text(json.dumps(data))
    due_keys = {e["key"] for e in get_due_keys(vault_file)}
    assert due_keys == {"X", "Y"}
