"""CLI tests for envault severity commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_severity import severity_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    vf.write_text("{}")
    return vf


def invoke(runner, vault_file, *args):
    return runner.invoke(severity_group, [*args, "--vault", str(vault_file)])


def test_sev_set_outputs_confirmation(runner, vault_file):
    result = invoke(runner, vault_file, "set", "DB_PASSWORD", "critical")
    assert result.exit_code == 0
    assert "DB_PASSWORD" in result.output
    assert "CRITICAL" in result.output


def test_sev_set_with_note(runner, vault_file):
    result = invoke(runner, vault_file, "set", "API_KEY", "high", "--note", "Rotated quarterly")
    assert result.exit_code == 0
    assert "Rotated quarterly" in result.output


def test_sev_show_after_set(runner, vault_file):
    invoke(runner, vault_file, "set", "MY_VAR", "medium")
    result = invoke(runner, vault_file, "show", "MY_VAR")
    assert result.exit_code == 0
    assert "MEDIUM" in result.output


def test_sev_show_missing_key(runner, vault_file):
    result = invoke(runner, vault_file, "show", "GHOST")
    assert result.exit_code == 0
    assert "No severity" in result.output


def test_sev_remove_existing(runner, vault_file):
    invoke(runner, vault_file, "set", "TOKEN", "low")
    result = invoke(runner, vault_file, "remove", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_sev_remove_nonexistent(runner, vault_file):
    result = invoke(runner, vault_file, "remove", "NONEXISTENT")
    assert result.exit_code == 0
    assert "No severity" in result.output


def test_sev_list_empty(runner, vault_file):
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No severity" in result.output


def test_sev_list_shows_entries(runner, vault_file):
    invoke(runner, vault_file, "set", "KEY_A", "critical")
    invoke(runner, vault_file, "set", "KEY_B", "low")
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_sev_list_filter_by_level(runner, vault_file):
    invoke(runner, vault_file, "set", "CRIT_KEY", "critical")
    invoke(runner, vault_file, "set", "LOW_KEY", "low")
    result = invoke(runner, vault_file, "list", "--level", "critical")
    assert result.exit_code == 0
    assert "CRIT_KEY" in result.output
    assert "LOW_KEY" not in result.output
