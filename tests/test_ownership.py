"""Tests for envault/ownership.py"""

import pytest
from pathlib import Path
from envault.ownership import (
    set_owner,
    remove_owner,
    get_owner,
    list_owned,
    get_keys_by_owner,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def test_set_owner_returns_entry(vault_file):
    entry = set_owner(vault_file, "DB_PASSWORD", "alice")
    assert entry["owner"] == "alice"
    assert "assigned_at" in entry
    assert entry["note"] == ""


def test_set_owner_with_note(vault_file):
    entry = set_owner(vault_file, "API_KEY", "bob", note="Primary API contact")
    assert entry["note"] == "Primary API contact"


def test_get_owner_returns_entry(vault_file):
    set_owner(vault_file, "SECRET", "carol")
    result = get_owner(vault_file, "SECRET")
    assert result is not None
    assert result["owner"] == "carol"


def test_get_owner_missing_returns_none(vault_file):
    assert get_owner(vault_file, "NONEXISTENT") is None


def test_remove_owner_returns_true(vault_file):
    set_owner(vault_file, "TOKEN", "dave")
    assert remove_owner(vault_file, "TOKEN") is True
    assert get_owner(vault_file, "TOKEN") is None


def test_remove_owner_nonexistent_returns_false(vault_file):
    assert remove_owner(vault_file, "GHOST_KEY") is False


def test_list_owned_returns_all(vault_file):
    set_owner(vault_file, "KEY_A", "alice")
    set_owner(vault_file, "KEY_B", "bob")
    owned = list_owned(vault_file)
    assert "KEY_A" in owned
    assert "KEY_B" in owned
    assert len(owned) == 2


def test_list_owned_empty_vault(vault_file):
    assert list_owned(vault_file) == {}


def test_get_keys_by_owner(vault_file):
    set_owner(vault_file, "DB_HOST", "alice")
    set_owner(vault_file, "DB_PASS", "alice")
    set_owner(vault_file, "API_KEY", "bob")
    keys = get_keys_by_owner(vault_file, "alice")
    assert set(keys) == {"DB_HOST", "DB_PASS"}


def test_get_keys_by_owner_no_match(vault_file):
    set_owner(vault_file, "SOME_KEY", "alice")
    assert get_keys_by_owner(vault_file, "nobody") == []


def test_set_owner_overwrites_existing(vault_file):
    set_owner(vault_file, "KEY", "alice")
    set_owner(vault_file, "KEY", "bob", note="Transferred")
    entry = get_owner(vault_file, "KEY")
    assert entry["owner"] == "bob"
    assert entry["note"] == "Transferred"
