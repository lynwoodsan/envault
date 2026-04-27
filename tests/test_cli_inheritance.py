"""Tests for CLI inheritance commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_inheritance import inheritance_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        inheritance_group,
        [*args, "--vault-dir", str(vault_dir)],
        catch_exceptions=False,
    )


def test_add_parent_outputs_confirmation(runner, vault_dir):
    result = invoke(runner, vault_dir, "add-parent", "/shared/base")
    assert result.exit_code == 0
    assert "Parent added" in result.output
    assert "/shared/base" in result.output


def test_list_parents_empty(runner, vault_dir):
    result = invoke(runner, vault_dir, "list-parents")
    assert result.exit_code == 0
    assert "No parent vaults" in result.output


def test_list_parents_shows_added(runner, vault_dir):
    invoke(runner, vault_dir, "add-parent", "/shared/base")
    result = invoke(runner, vault_dir, "list-parents")
    assert "/shared/base" in result.output


def test_remove_parent_success(runner, vault_dir):
    invoke(runner, vault_dir, "add-parent", "/shared/base")
    result = invoke(runner, vault_dir, "remove-parent", "/shared/base")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_parent_missing_exits_1(runner, vault_dir):
    result = runner.invoke(
        inheritance_group,
        ["remove-parent", "/nonexistent", "--vault-dir", str(vault_dir)],
    )
    assert result.exit_code == 1


def test_override_outputs_confirmation(runner, vault_dir):
    result = invoke(runner, vault_dir, "override", "DB_URL")
    assert result.exit_code == 0
    assert "DB_URL" in result.output


def test_list_overrides_empty(runner, vault_dir):
    result = invoke(runner, vault_dir, "list-overrides")
    assert result.exit_code == 0
    assert "No overrides" in result.output


def test_list_overrides_shows_key(runner, vault_dir):
    invoke(runner, vault_dir, "override", "API_SECRET")
    result = invoke(runner, vault_dir, "list-overrides")
    assert "API_SECRET" in result.output


def test_unoverride_success(runner, vault_dir):
    invoke(runner, vault_dir, "override", "API_SECRET")
    result = invoke(runner, vault_dir, "unoverride", "API_SECRET")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_unoverride_missing_exits_1(runner, vault_dir):
    result = runner.invoke(
        inheritance_group,
        ["unoverride", "MISSING_KEY", "--vault-dir", str(vault_dir)],
    )
    assert result.exit_code == 1
