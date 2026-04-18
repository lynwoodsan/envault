"""Tests for CLI TTL commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_ttl import ttl_group
from envault.ttl import set_ttl


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def invoke(runner, vault_dir, *args):
    vault = str(vault_dir / ".envault")
    return runner.invoke(ttl_group, [*args, "--vault", vault])


def test_ttl_set_outputs_expiry(runner, vault_dir):
    result = invoke(runner, vault_dir, "set", "API_KEY", "3600")
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "expires at" in result.output


def test_ttl_list_empty(runner, vault_dir):
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No TTLs" in result.output


def test_ttl_list_shows_keys(runner, vault_dir):
    vault_path = vault_dir / ".envault"
    set_ttl(vault_path, "DB_PASS", 500)
    result = invoke(runner, vault_dir, "list")
    assert "DB_PASS" in result.output


def test_ttl_list_marks_expired(runner, vault_dir):
    vault_path = vault_dir / ".envault"
    set_ttl(vault_path, "OLD", -10)
    result = invoke(runner, vault_dir, "list")
    assert "EXPIRED" in result.output


def test_ttl_remove(runner, vault_dir):
    vault_path = vault_dir / ".envault"
    set_ttl(vault_path, "TOKEN", 60)
    result = invoke(runner, vault_dir, "remove", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_ttl_purge_nothing(runner, vault_dir):
    result = invoke(runner, vault_dir, "purge")
    assert result.exit_code == 0
    assert "Nothing to purge" in result.output


def test_ttl_purge_expired(runner, vault_dir):
    vault_path = vault_dir / ".envault"
    set_ttl(vault_path, "STALE", -5)
    set_ttl(vault_path, "FRESH", 100)
    result = invoke(runner, vault_dir, "purge")
    assert "STALE" in result.output
    assert "FRESH" not in result.output
