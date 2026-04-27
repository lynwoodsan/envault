"""Tests for envault.immutable."""

import pytest
from pathlib import Path

from envault.immutable import (
    mark_immutable,
    unmark_immutable,
    is_immutable,
    get_immutable_entry,
    list_immutable,
    check_immutable,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def test_mark_immutable_returns_entry(vault_file):
    entry = mark_immutable(vault_file, "DB_PASSWORD")
    assert entry["key"] == "DB_PASSWORD"
    assert entry["reason"] is None
    assert "marked_at" in entry


def test_mark_immutable_with_reason(vault_file):
    entry = mark_immutable(vault_file, "API_KEY", reason="Production secret")
    assert entry["reason"] == "Production secret"


def test_is_immutable_true_after_mark(vault_file):
    mark_immutable(vault_file, "SECRET")
    assert is_immutable(vault_file, "SECRET") is True


def test_is_immutable_false_before_mark(vault_file):
    assert is_immutable(vault_file, "NOT_MARKED") is False


def test_unmark_immutable_returns_true(vault_file):
    mark_immutable(vault_file, "KEY")
    result = unmark_immutable(vault_file, "KEY")
    assert result is True
    assert is_immutable(vault_file, "KEY") is False


def test_unmark_nonexistent_returns_false(vault_file):
    result = unmark_immutable(vault_file, "GHOST")
    assert result is False


def test_get_immutable_entry_returns_dict(vault_file):
    mark_immutable(vault_file, "TOKEN", reason="Do not touch")
    entry = get_immutable_entry(vault_file, "TOKEN")
    assert entry is not None
    assert entry["key"] == "TOKEN"
    assert entry["reason"] == "Do not touch"


def test_get_immutable_entry_missing_returns_none(vault_file):
    assert get_immutable_entry(vault_file, "MISSING") is None


def test_list_immutable_sorted(vault_file):
    mark_immutable(vault_file, "Z_KEY")
    mark_immutable(vault_file, "A_KEY")
    entries = list_immutable(vault_file)
    assert [e["key"] for e in entries] == ["A_KEY", "Z_KEY"]


def test_list_immutable_empty(vault_file):
    assert list_immutable(vault_file) == []


def test_check_immutable_raises_for_marked(vault_file):
    mark_immutable(vault_file, "LOCKED", reason="Compliance")
    with pytest.raises(ValueError, match="immutable"):
        check_immutable(vault_file, "LOCKED")


def test_check_immutable_reason_in_message(vault_file):
    mark_immutable(vault_file, "LOCKED", reason="Compliance")
    with pytest.raises(ValueError, match="Compliance"):
        check_immutable(vault_file, "LOCKED")


def test_check_immutable_passes_for_unmarked(vault_file):
    check_immutable(vault_file, "FREE")  # should not raise


def test_persists_across_calls(vault_file):
    mark_immutable(vault_file, "PERSIST")
    # Reload from disk implicitly
    assert is_immutable(vault_file, "PERSIST") is True
    unmark_immutable(vault_file, "PERSIST")
    assert is_immutable(vault_file, "PERSIST") is False
