"""Tests for envault/cli_policy.py"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_policy import policy_group
from envault.vault import save_vault

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def prepared_vault(tmp_path):
    vault_path = tmp_path / ".envault"
    save_vault(vault_path, PASSWORD, {"APP_HOST": "localhost", "APP_PORT": "5432"})
    return vault_path


def invoke(runner, vault_path, *args):
    return runner.invoke(policy_group, ["--vault", str(vault_path)] + list(args),
                         catch_exceptions=False)


def test_pol_add_and_list(runner, prepared_vault):
    result = invoke(runner, prepared_vault, "add", "prefix_rule", "--required-prefix", "APP_")
    assert result.exit_code == 0
    assert "saved" in result.output

    result = invoke(runner, prepared_vault, "list")
    assert result.exit_code == 0
    assert "prefix_rule" in result.output
    assert "APP_" in result.output


def test_pol_add_multiple_options(runner, prepared_vault):
    result = invoke(runner, prepared_vault, "add", "strict",
                    "--required-prefix", "APP_",
                    "--max-length", "128")
    assert result.exit_code == 0
    result = invoke(runner, prepared_vault, "list")
    assert "max_len=128" in result.output


def test_pol_remove_existing(runner, prepared_vault):
    invoke(runner, prepared_vault, "add", "r1", "--required-prefix", "X_")
    result = invoke(runner, prepared_vault, "remove", "r1")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_pol_remove_nonexistent_exits_1(runner, prepared_vault):
    result = runner.invoke(policy_group,
                           ["--vault", str(prepared_vault), "remove", "ghost"],
                           catch_exceptions=False)
    assert result.exit_code == 1


def test_pol_list_empty(runner, prepared_vault):
    result = invoke(runner, prepared_vault, "list")
    assert result.exit_code == 0
    assert "No policy rules" in result.output


def test_pol_check_passes(runner, prepared_vault):
    invoke(runner, prepared_vault, "add", "prefix", "--required-prefix", "APP_")
    result = runner.invoke(policy_group,
                           ["--vault", str(prepared_vault), "check",
                            "--password", PASSWORD],
                           catch_exceptions=False)
    assert result.exit_code == 0
    assert "passed" in result.output


def test_pol_check_fails_on_violation(runner, tmp_path):
    vault_path = tmp_path / ".envault"
    save_vault(vault_path, PASSWORD, {"DB_HOST": "localhost"})
    invoke(runner, vault_path, "add", "prefix", "--required-prefix", "APP_")
    result = runner.invoke(policy_group,
                           ["--vault", str(vault_path), "check",
                            "--password", PASSWORD],
                           catch_exceptions=False)
    assert result.exit_code == 1
    assert "DB_HOST" in result.output
