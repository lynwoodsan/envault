"""Tests for the deprecation CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_deprecation import deprecation_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.touch()
    return vf


def invoke(runner, vault_file, *args):
    return runner.invoke(
        deprecation_group, [*args, "--vault", str(vault_file)]
    )


def test_dep_mark_outputs_confirmation(runner, vault_file):
    result = invoke(runner, vault_file, "mark", "OLD_KEY", "--reason", "use NEW instead")
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output
    assert "deprecated" in result.output


def test_dep_mark_with_replacement(runner, vault_file):
    result = invoke(runner, vault_file, "mark", "OLD_KEY", "--replacement", "NEW_KEY")
    assert result.exit_code == 0
    assert "NEW_KEY" in result.output


def test_dep_mark_with_sunset(runner, vault_file):
    result = invoke(runner, vault_file, "mark", "OLD_KEY", "--sunset", "2025-12-31")
    assert result.exit_code == 0
    assert "2025-12-31" in result.output


def test_dep_show_after_mark(runner, vault_file):
    invoke(runner, vault_file, "mark", "OLD_KEY", "--reason", "legacy", "--replacement", "NEW_KEY")
    result = invoke(runner, vault_file, "show", "OLD_KEY")
    assert result.exit_code == 0
    assert "legacy" in result.output
    assert "NEW_KEY" in result.output


def test_dep_show_not_deprecated(runner, vault_file):
    result = invoke(runner, vault_file, "show", "UNKNOWN")
    assert result.exit_code == 0
    assert "not deprecated" in result.output


def test_dep_list_empty(runner, vault_file):
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No deprecated" in result.output


def test_dep_list_shows_entries(runner, vault_file):
    invoke(runner, vault_file, "mark", "KEY_A")
    invoke(runner, vault_file, "mark", "KEY_B", "--replacement", "KEY_C")
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output
    assert "KEY_C" in result.output


def test_dep_unmark_removes_entry(runner, vault_file):
    invoke(runner, vault_file, "mark", "OLD_KEY")
    result = invoke(runner, vault_file, "unmark", "OLD_KEY")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_dep_unmark_nonexistent_exits_1(runner, vault_file):
    result = invoke(runner, vault_file, "unmark", "GHOST")
    assert result.exit_code == 1
