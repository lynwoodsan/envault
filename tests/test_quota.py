"""Tests for envault.quota"""

import pytest
from pathlib import Path

from envault.quota import (
    set_quota,
    remove_quota,
    get_quota,
    check_quota,
    format_quota_status,
    QuotaStatus,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    vf.write_bytes(b"")
    return vf


def test_get_quota_missing_returns_none(vault_file):
    assert get_quota(vault_file) is None


def test_set_and_get_quota(vault_file):
    set_quota(vault_file, 10)
    assert get_quota(vault_file) == 10


def test_set_quota_invalid_raises(vault_file):
    with pytest.raises(ValueError, match="at least 1"):
        set_quota(vault_file, 0)


def test_set_quota_negative_raises(vault_file):
    with pytest.raises(ValueError):
        set_quota(vault_file, -5)


def test_remove_quota_returns_true_when_exists(vault_file):
    set_quota(vault_file, 5)
    assert remove_quota(vault_file) is True
    assert get_quota(vault_file) is None


def test_remove_quota_returns_false_when_missing(vault_file):
    assert remove_quota(vault_file) is False


def test_check_quota_no_limit(vault_file):
    status = check_quota(vault_file, 42)
    assert status.limit is None
    assert status.current == 42
    assert status.exceeded is False
    assert status.remaining is None


def test_check_quota_within_limit(vault_file):
    set_quota(vault_file, 10)
    status = check_quota(vault_file, 7)
    assert status.exceeded is False
    assert status.remaining == 3


def test_check_quota_at_limit(vault_file):
    set_quota(vault_file, 5)
    status = check_quota(vault_file, 5)
    assert status.exceeded is False
    assert status.remaining == 0


def test_check_quota_exceeded(vault_file):
    set_quota(vault_file, 3)
    status = check_quota(vault_file, 5)
    assert status.exceeded is True
    assert status.remaining == 0


def test_format_quota_no_limit(vault_file):
    status = check_quota(vault_file, 4)
    out = format_quota_status(status)
    assert "No quota" in out
    assert "4" in out


def test_format_quota_ok(vault_file):
    set_quota(vault_file, 10)
    status = check_quota(vault_file, 6)
    out = format_quota_status(status)
    assert "OK" in out
    assert "6/10" in out


def test_format_quota_exceeded(vault_file):
    set_quota(vault_file, 3)
    status = check_quota(vault_file, 5)
    out = format_quota_status(status)
    assert "EXCEEDED" in out
    assert "5/3" in out
