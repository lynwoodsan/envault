"""Tests for envault.vault module."""

import pytest

from envault.vault import delete_var, list_vars, load_vault, save_vault, set_var

PASSWORD = "test-password-123"


def test_save_and_load_roundtrip(tmp_path):
    vault_file = str(tmp_path / ".envault")
    data = {"API_KEY": "abc123", "DEBUG": "true"}
    save_vault(data, PASSWORD, vault_file)
    loaded = load_vault(PASSWORD, vault_file)
    assert loaded == data


def test_load_missing_vault_returns_empty(tmp_path):
    vault_file = str(tmp_path / ".envault")
    result = load_vault(PASSWORD, vault_file)
    assert result == {}


def test_load_wrong_password_raises(tmp_path):
    vault_file = str(tmp_path / ".envault")
    save_vault({"KEY": "value"}, PASSWORD, vault_file)
    with pytest.raises(Exception):
        load_vault("wrong-password", vault_file)


def test_set_var_creates_entry(tmp_path):
    vault_file = str(tmp_path / ".envault")
    set_var("MY_VAR", "hello", PASSWORD, vault_file)
    data = load_vault(PASSWORD, vault_file)
    assert data["MY_VAR"] == "hello"


def test_set_var_overwrites_existing(tmp_path):
    vault_file = str(tmp_path / ".envault")
    set_var("MY_VAR", "first", PASSWORD, vault_file)
    set_var("MY_VAR", "second", PASSWORD, vault_file)
    data = load_vault(PASSWORD, vault_file)
    assert data["MY_VAR"] == "second"
    assert len(data) == 1


def test_delete_var_removes_entry(tmp_path):
    vault_file = str(tmp_path / ".envault")
    set_var("TO_DELETE", "val", PASSWORD, vault_file)
    removed = delete_var("TO_DELETE", PASSWORD, vault_file)
    assert removed is True
    data = load_vault(PASSWORD, vault_file)
    assert "TO_DELETE" not in data


def test_delete_var_missing_key_returns_false(tmp_path):
    vault_file = str(tmp_path / ".envault")
    removed = delete_var("NONEXISTENT", PASSWORD, vault_file)
    assert removed is False


def test_list_vars_returns_all(tmp_path):
    vault_file = str(tmp_path / ".envault")
    save_vault({"A": "1", "B": "2", "C": "3"}, PASSWORD, vault_file)
    result = list_vars(PASSWORD, vault_file)
    assert result == {"A": "1", "B": "2", "C": "3"}


def test_list_vars_empty_vault_returns_empty(tmp_path):
    """list_vars on a non-existent vault should return an empty dict."""
    vault_file = str(tmp_path / ".envault")
    result = list_vars(PASSWORD, vault_file)
    assert result == {}


def test_save_vault_persists_to_disk(tmp_path):
    """Saving a vault should create a file on disk."""
    vault_file = str(tmp_path / ".envault")
    save_vault({"KEY": "value"}, PASSWORD, vault_file)
    import os
    assert os.path.exists(vault_file)
