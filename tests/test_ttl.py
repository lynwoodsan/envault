"""Tests for envault.ttl module."""

import time
import pytest
from pathlib import Path
from envault.ttl import (
    set_ttl, remove_ttl, get_ttl, is_expired, list_ttls, purge_expired
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / ".envault"


def test_set_and_get_ttl(vault_file):
    expires_at = set_ttl(vault_file, "API_KEY", 60)
    assert get_ttl(vault_file, "API_KEY") == pytest.approx(expires_at, abs=1)


def test_get_ttl_missing_key(vault_file):
    assert get_ttl(vault_file, "MISSING") is None


def test_is_expired_not_yet(vault_file):
    set_ttl(vault_file, "TOKEN", 100)
    assert not is_expired(vault_file, "TOKEN")


def test_is_expired_past(vault_file):
    set_ttl(vault_file, "OLD_KEY", -1)
    assert is_expired(vault_file, "OLD_KEY")


def test_is_expired_no_ttl(vault_file):
    assert not is_expired(vault_file, "NO_TTL_KEY")


def test_remove_ttl(vault_file):
    set_ttl(vault_file, "API_KEY", 60)
    remove_ttl(vault_file, "API_KEY")
    assert get_ttl(vault_file, "API_KEY") is None


def test_remove_ttl_nonexistent(vault_file):
    remove_ttl(vault_file, "GHOST")  # should not raise


def test_list_ttls(vault_file):
    set_ttl(vault_file, "A", 10)
    set_ttl(vault_file, "B", 20)
    ttls = list_ttls(vault_file)
    assert "A" in ttls
    assert "B" in ttls


def test_purge_expired_removes_only_expired(vault_file):
    set_ttl(vault_file, "ALIVE", 100)
    set_ttl(vault_file, "DEAD", -1)
    purged = purge_expired(vault_file)
    assert "DEAD" in purged
    assert "ALIVE" not in purged
    assert get_ttl(vault_file, "ALIVE") is not None
    assert get_ttl(vault_file, "DEAD") is None


def test_purge_expired_empty(vault_file):
    result = purge_expired(vault_file)
    assert result == []
