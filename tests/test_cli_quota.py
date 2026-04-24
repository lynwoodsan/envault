"""Tests for envault.cli_quota"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from envault.cli_quota import quota_group
from envault.vault import set_var, save_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def prepared_vault(tmp_path):
    vault_file = tmp_path / ".envault"
    password = "testpass"
    set_var(vault_file, password, "API_KEY", "abc123")
    set_var(vault_file, password, "DB_URL", "postgres://localhost/db")
    return vault_file, password


def invoke(runner, vault_file, args, password="testpass"):
    with patch("envault.cli_quota.get_password", return_value=password):
        return runner.invoke(quota_group, ["--vault", str(vault_file)] + args)


def test_quota_set_outputs_confirmation(runner, prepared_vault):
    vault_file, _ = prepared_vault
    result = invoke(runner, vault_file, ["set", "20"])
    assert result.exit_code == 0
    assert "20" in result.output


def test_quota_set_invalid_limit_exits_1(runner, prepared_vault):
    vault_file, _ = prepared_vault
    result = invoke(runner, vault_file, ["set", "0"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_quota_remove_when_set(runner, prepared_vault):
    vault_file, _ = prepared_vault
    invoke(runner, vault_file, ["set", "10"])
    result = invoke(runner, vault_file, ["remove"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_quota_remove_when_not_set(runner, prepared_vault):
    vault_file, _ = prepared_vault
    result = invoke(runner, vault_file, ["remove"])
    assert result.exit_code == 0
    assert "No quota" in result.output


def test_quota_show_no_quota(runner, prepared_vault):
    vault_file, _ = prepared_vault
    result = invoke(runner, vault_file, ["show"])
    assert result.exit_code == 0
    assert "No quota" in result.output


def test_quota_show_with_limit(runner, prepared_vault):
    vault_file, _ = prepared_vault
    invoke(runner, vault_file, ["set", "15"])
    result = invoke(runner, vault_file, ["show"])
    assert result.exit_code == 0
    assert "15" in result.output


def test_quota_check_within_limit(runner, prepared_vault):
    vault_file, _ = prepared_vault
    invoke(runner, vault_file, ["set", "10"])
    result = invoke(runner, vault_file, ["check"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_quota_check_exceeded_exits_1(runner, prepared_vault):
    vault_file, _ = prepared_vault
    # vault has 2 vars; set quota to 1
    invoke(runner, vault_file, ["set", "1"])
    result = invoke(runner, vault_file, ["check"])
    assert result.exit_code == 1
    assert "EXCEEDED" in result.output


def test_quota_check_no_limit_always_ok(runner, prepared_vault):
    vault_file, _ = prepared_vault
    result = invoke(runner, vault_file, ["check"])
    assert result.exit_code == 0
    assert "No quota" in result.output
