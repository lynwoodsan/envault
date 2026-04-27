"""Tests for envault.cli_immutable."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_immutable import immutable_group
from envault.immutable import mark_immutable


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def invoke(runner, vault_file, *args):
    return runner.invoke(immutable_group, [*args, "--vault", vault_file])


def test_lock_outputs_confirmation(runner, vault_file):
    result = invoke(runner, vault_file, "lock", "DB_PASS")
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "immutable" in result.output


def test_lock_with_reason(runner, vault_file):
    result = invoke(runner, vault_file, "lock", "API_KEY", "--reason", "Compliance")
    assert result.exit_code == 0
    assert "Compliance" in result.output


def test_unlock_existing(runner, vault_file):
    mark_immutable(vault_file, "TOKEN")
    result = invoke(runner, vault_file, "unlock", "TOKEN")
    assert result.exit_code == 0
    assert "no longer immutable" in result.output


def test_unlock_nonexistent_exits_1(runner, vault_file):
    result = invoke(runner, vault_file, "unlock", "GHOST")
    assert result.exit_code == 1


def test_check_locked_key(runner, vault_file):
    mark_immutable(vault_file, "SECRET")
    result = invoke(runner, vault_file, "check", "SECRET")
    assert result.exit_code == 0
    assert "immutable" in result.output


def test_check_unlocked_key(runner, vault_file):
    result = invoke(runner, vault_file, "check", "FREE_KEY")
    assert result.exit_code == 0
    assert "not immutable" in result.output


def test_list_empty(runner, vault_file):
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No immutable" in result.output


def test_list_shows_keys(runner, vault_file):
    mark_immutable(vault_file, "ALPHA")
    mark_immutable(vault_file, "BETA", reason="important")
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output
    assert "important" in result.output
