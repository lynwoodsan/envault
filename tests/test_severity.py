"""Tests for envault.severity."""

import pytest
from pathlib import Path
from envault.severity import (
    set_severity,
    remove_severity,
    get_severity,
    list_severity,
    get_keys_by_level,
    VALID_LEVELS,
    SeverityEntry,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    vf.write_text("{}")
    return vf


def test_set_severity_returns_entry(vault_file):
    entry = set_severity(vault_file, "DB_PASSWORD", "critical")
    assert isinstance(entry, SeverityEntry)
    assert entry.key == "DB_PASSWORD"
    assert entry.level == "critical"


def test_set_severity_with_note(vault_file):
    entry = set_severity(vault_file, "API_KEY", "high", note="Rotated quarterly")
    assert entry.note == "Rotated quarterly"


def test_set_severity_invalid_level_raises(vault_file):
    with pytest.raises(ValueError, match="Invalid severity level"):
        set_severity(vault_file, "FOO", "extreme")


def test_get_severity_returns_entry(vault_file):
    set_severity(vault_file, "SECRET", "medium")
    entry = get_severity(vault_file, "SECRET")
    assert entry is not None
    assert entry.level == "medium"


def test_get_severity_missing_returns_none(vault_file):
    assert get_severity(vault_file, "NONEXISTENT") is None


def test_remove_severity_returns_true(vault_file):
    set_severity(vault_file, "TOKEN", "low")
    assert remove_severity(vault_file, "TOKEN") is True
    assert get_severity(vault_file, "TOKEN") is None


def test_remove_severity_nonexistent_returns_false(vault_file):
    assert remove_severity(vault_file, "GHOST") is False


def test_list_severity_sorted_by_level_then_key(vault_file):
    set_severity(vault_file, "Z_KEY", "low")
    set_severity(vault_file, "A_KEY", "critical")
    set_severity(vault_file, "M_KEY", "medium")
    entries = list_severity(vault_file)
    levels = [e.level for e in entries]
    assert levels == sorted(levels, key=lambda l: VALID_LEVELS.index(l))


def test_get_keys_by_level(vault_file):
    set_severity(vault_file, "DB_PASS", "critical")
    set_severity(vault_file, "LOG_LEVEL", "low")
    set_severity(vault_file, "API_SECRET", "critical")
    critical_keys = get_keys_by_level(vault_file, "critical")
    assert "DB_PASS" in critical_keys
    assert "API_SECRET" in critical_keys
    assert "LOG_LEVEL" not in critical_keys


def test_valid_levels_tuple_contains_four():
    assert len(VALID_LEVELS) == 4
    assert "critical" in VALID_LEVELS


def test_set_severity_persists(vault_file):
    set_severity(vault_file, "PERSIST_KEY", "high")
    entry = get_severity(vault_file, "PERSIST_KEY")
    assert entry is not None
    assert entry.level == "high"


def test_overwrite_severity(vault_file):
    set_severity(vault_file, "MYVAR", "low")
    set_severity(vault_file, "MYVAR", "critical", note="Upgraded")
    entry = get_severity(vault_file, "MYVAR")
    assert entry.level == "critical"
    assert entry.note == "Upgraded"
