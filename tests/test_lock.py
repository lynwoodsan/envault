"""Tests for envault.lock module."""

import pytest
from pathlib import Path
from envault.lock import (
    lock_vault,
    unlock_vault,
    lock_key,
    unlock_key,
    is_vault_locked,
    is_key_locked,
    list_locked_keys,
    get_vault_lock_reason,
)


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / ".envault"
    p.touch()
    return p


def test_vault_not_locked_by_default(vault_file):
    assert is_vault_locked(vault_file) is False


def test_lock_vault(vault_file):
    lock_vault(vault_file)
    assert is_vault_locked(vault_file) is True


def test_lock_vault_with_reason(vault_file):
    lock_vault(vault_file, reason="freeze for release")
    assert get_vault_lock_reason(vault_file) == "freeze for release"


def test_unlock_vault(vault_file):
    lock_vault(vault_file)
    unlock_vault(vault_file)
    assert is_vault_locked(vault_file) is False


def test_unlock_vault_clears_reason(vault_file):
    lock_vault(vault_file, reason="temp")
    unlock_vault(vault_file)
    assert get_vault_lock_reason(vault_file) == ""


def test_key_not_locked_by_default(vault_file):
    assert is_key_locked(vault_file, "MY_KEY") is False


def test_lock_key(vault_file):
    lock_key(vault_file, "DB_PASSWORD")
    assert is_key_locked(vault_file, "DB_PASSWORD") is True


def test_lock_key_with_reason(vault_file):
    lock_key(vault_file, "API_TOKEN", reason="do not change")
    locked = list_locked_keys(vault_file)
    assert locked["API_TOKEN"] == "do not change"


def test_unlock_key_returns_true(vault_file):
    lock_key(vault_file, "MY_KEY")
    result = unlock_key(vault_file, "MY_KEY")
    assert result is True
    assert is_key_locked(vault_file, "MY_KEY") is False


def test_unlock_nonexistent_key_returns_false(vault_file):
    result = unlock_key(vault_file, "GHOST_KEY")
    assert result is False


def test_list_locked_keys_empty(vault_file):
    assert list_locked_keys(vault_file) == {}


def test_list_locked_keys_multiple(vault_file):
    lock_key(vault_file, "KEY_A", reason="r1")
    lock_key(vault_file, "KEY_B", reason="r2")
    locked = list_locked_keys(vault_file)
    assert set(locked.keys()) == {"KEY_A", "KEY_B"}
    assert locked["KEY_A"] == "r1"


def test_lock_and_unlock_does_not_affect_other_keys(vault_file):
    lock_key(vault_file, "KEY_A")
    lock_key(vault_file, "KEY_B")
    unlock_key(vault_file, "KEY_A")
    assert is_key_locked(vault_file, "KEY_A") is False
    assert is_key_locked(vault_file, "KEY_B") is True
