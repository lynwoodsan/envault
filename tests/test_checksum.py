"""Tests for envault.checksum module."""

import pytest
from pathlib import Path

from envault.checksum import (
    record_checksum,
    get_checksum,
    verify_checksum,
    remove_checksum,
    list_checksums,
    check_all,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.touch()
    return vf


def test_record_checksum_returns_hex(vault_file):
    digest = record_checksum(vault_file, "API_KEY", "secret123")
    assert isinstance(digest, str)
    assert len(digest) == 64  # sha256 hex


def test_get_checksum_returns_entry(vault_file):
    record_checksum(vault_file, "DB_URL", "postgres://localhost/db")
    entry = get_checksum(vault_file, "DB_URL")
    assert entry is not None
    assert "sha256" in entry
    assert "recorded_at" in entry


def test_get_checksum_missing_returns_none(vault_file):
    result = get_checksum(vault_file, "NONEXISTENT")
    assert result is None


def test_verify_checksum_correct_value(vault_file):
    record_checksum(vault_file, "TOKEN", "abc")
    assert verify_checksum(vault_file, "TOKEN", "abc") is True


def test_verify_checksum_wrong_value(vault_file):
    record_checksum(vault_file, "TOKEN", "abc")
    assert verify_checksum(vault_file, "TOKEN", "xyz") is False


def test_verify_checksum_unrecorded_key(vault_file):
    assert verify_checksum(vault_file, "GHOST", "value") is False


def test_remove_checksum_returns_true(vault_file):
    record_checksum(vault_file, "KEY", "val")
    assert remove_checksum(vault_file, "KEY") is True
    assert get_checksum(vault_file, "KEY") is None


def test_remove_checksum_nonexistent_returns_false(vault_file):
    assert remove_checksum(vault_file, "MISSING") is False


def test_list_checksums_empty(vault_file):
    assert list_checksums(vault_file) == {}


def test_list_checksums_multiple(vault_file):
    record_checksum(vault_file, "A", "1")
    record_checksum(vault_file, "B", "2")
    result = list_checksums(vault_file)
    assert set(result.keys()) == {"A", "B"}


def test_check_all_ok(vault_file):
    record_checksum(vault_file, "X", "hello")
    results = check_all(vault_file, {"X": "hello"})
    assert results["X"] == "ok"


def test_check_all_mismatch(vault_file):
    record_checksum(vault_file, "X", "hello")
    results = check_all(vault_file, {"X": "world"})
    assert results["X"] == "mismatch"


def test_check_all_unrecorded(vault_file):
    results = check_all(vault_file, {"NEW_KEY": "value"})
    assert results["NEW_KEY"] == "unrecorded"


def test_check_all_mixed(vault_file):
    record_checksum(vault_file, "GOOD", "correct")
    record_checksum(vault_file, "BAD", "old")
    results = check_all(vault_file, {"GOOD": "correct", "BAD": "new", "FRESH": "v"})
    assert results["GOOD"] == "ok"
    assert results["BAD"] == "mismatch"
    assert results["FRESH"] == "unrecorded"
