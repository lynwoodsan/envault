"""Tests for envault/trust.py"""

import pytest
from pathlib import Path
from envault.trust import (
    set_trust,
    remove_trust,
    get_trust,
    list_trust,
    get_keys_by_level,
    VALID_LEVELS,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.write_bytes(b"dummy")
    return vf


def test_set_trust_returns_entry(vault_file):
    entry = set_trust(vault_file, "API_KEY", "trusted")
    assert entry.key == "API_KEY"
    assert entry.level == "trusted"
    assert entry.note is None
    assert entry.set_by == "user"


def test_set_trust_with_note(vault_file):
    entry = set_trust(vault_file, "DB_PASS", "verified", note="audited by security team")
    assert entry.note == "audited by security team"


def test_set_trust_invalid_level_raises(vault_file):
    with pytest.raises(ValueError, match="Invalid trust level"):
        set_trust(vault_file, "API_KEY", "unknown")


def test_get_trust_returns_entry(vault_file):
    set_trust(vault_file, "TOKEN", "provisional")
    entry = get_trust(vault_file, "TOKEN")
    assert entry is not None
    assert entry.level == "provisional"
    assert entry.key == "TOKEN"


def test_get_trust_missing_returns_none(vault_file):
    assert get_trust(vault_file, "NONEXISTENT") is None


def test_set_trust_overwrites_existing(vault_file):
    set_trust(vault_file, "API_KEY", "untrusted")
    set_trust(vault_file, "API_KEY", "verified")
    entry = get_trust(vault_file, "API_KEY")
    assert entry.level == "verified"


def test_remove_trust_returns_true(vault_file):
    set_trust(vault_file, "API_KEY", "trusted")
    result = remove_trust(vault_file, "API_KEY")
    assert result is True
    assert get_trust(vault_file, "API_KEY") is None


def test_remove_trust_nonexistent_returns_false(vault_file):
    assert remove_trust(vault_file, "MISSING") is False


def test_list_trust_empty(vault_file):
    assert list_trust(vault_file) == []


def test_list_trust_multiple(vault_file):
    set_trust(vault_file, "KEY_A", "trusted")
    set_trust(vault_file, "KEY_B", "untrusted")
    entries = list_trust(vault_file)
    assert len(entries) == 2
    keys = {e.key for e in entries}
    assert keys == {"KEY_A", "KEY_B"}


def test_get_keys_by_level(vault_file):
    set_trust(vault_file, "A", "trusted")
    set_trust(vault_file, "B", "trusted")
    set_trust(vault_file, "C", "untrusted")
    result = get_keys_by_level(vault_file, "trusted")
    assert set(result) == {"A", "B"}


def test_get_keys_by_level_invalid_raises(vault_file):
    with pytest.raises(ValueError):
        get_keys_by_level(vault_file, "bogus")


def test_valid_levels_tuple_contains_four():
    assert len(VALID_LEVELS) == 4
    assert "untrusted" in VALID_LEVELS
    assert "verified" in VALID_LEVELS


def test_set_trust_custom_actor(vault_file):
    entry = set_trust(vault_file, "SECRET", "trusted", actor="ci-bot")
    assert entry.set_by == "ci-bot"
    stored = get_trust(vault_file, "SECRET")
    assert stored.set_by == "ci-bot"
