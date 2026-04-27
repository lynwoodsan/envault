"""Tests for envault.deprecation."""

import pytest
from pathlib import Path

from envault.deprecation import (
    deprecate_var,
    undeprecate_var,
    get_deprecation,
    list_deprecated,
    is_deprecated,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.touch()
    return vf


def test_deprecate_var_returns_entry(vault_file):
    entry = deprecate_var(vault_file, "OLD_KEY", reason="Use NEW_KEY instead")
    assert entry["key"] == "OLD_KEY"
    assert entry["reason"] == "Use NEW_KEY instead"
    assert "deprecated_at" in entry


def test_deprecate_var_with_replacement(vault_file):
    entry = deprecate_var(vault_file, "OLD_KEY", replacement="NEW_KEY")
    assert entry["replacement"] == "NEW_KEY"


def test_deprecate_var_with_sunset_date(vault_file):
    entry = deprecate_var(vault_file, "OLD_KEY", sunset_date="2025-12-31")
    assert entry["sunset_date"] == "2025-12-31"


def test_get_deprecation_returns_entry(vault_file):
    deprecate_var(vault_file, "OLD_KEY", reason="legacy")
    entry = get_deprecation(vault_file, "OLD_KEY")
    assert entry is not None
    assert entry["reason"] == "legacy"


def test_get_deprecation_missing_returns_none(vault_file):
    assert get_deprecation(vault_file, "MISSING_KEY") is None


def test_is_deprecated_true(vault_file):
    deprecate_var(vault_file, "OLD_KEY")
    assert is_deprecated(vault_file, "OLD_KEY") is True


def test_is_deprecated_false_for_unknown(vault_file):
    assert is_deprecated(vault_file, "NEVER_SET") is False


def test_undeprecate_var_removes_entry(vault_file):
    deprecate_var(vault_file, "OLD_KEY")
    result = undeprecate_var(vault_file, "OLD_KEY")
    assert result is True
    assert get_deprecation(vault_file, "OLD_KEY") is None


def test_undeprecate_nonexistent_returns_false(vault_file):
    assert undeprecate_var(vault_file, "GHOST") is False


def test_list_deprecated_returns_all(vault_file):
    deprecate_var(vault_file, "KEY_A", reason="old")
    deprecate_var(vault_file, "KEY_B", reason="very old")
    items = list_deprecated(vault_file)
    keys = [i["key"] for i in items]
    assert "KEY_A" in keys
    assert "KEY_B" in keys


def test_list_deprecated_empty_vault(vault_file):
    assert list_deprecated(vault_file) == []


def test_deprecate_overwrites_existing(vault_file):
    deprecate_var(vault_file, "OLD_KEY", reason="first")
    deprecate_var(vault_file, "OLD_KEY", reason="second")
    entry = get_deprecation(vault_file, "OLD_KEY")
    assert entry["reason"] == "second"
