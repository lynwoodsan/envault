"""CLI tests for envault.cli_classification."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_classification import classification_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "test.vault")


def invoke(runner, vault_file, *args):
    return runner.invoke(classification_group, [*args, "--vault", vault_file])


def test_cls_set_outputs_confirmation(runner, vault_file):
    result = invoke(runner, vault_file, "set", "DB_PASSWORD", "secret")
    assert result.exit_code == 0
    assert "secret" in result.output
    assert "DB_PASSWORD" in result.output


def test_cls_set_with_note(runner, vault_file):
    result = invoke(runner, vault_file, "set", "API_KEY", "confidential", "--note", "vendor key")
    assert result.exit_code == 0


def test_cls_show_after_set(runner, vault_file):
    invoke(runner, vault_file, "set", "TOKEN", "internal")
    result = invoke(runner, vault_file, "show", "TOKEN")
    assert result.exit_code == 0
    assert "internal" in result.output


def test_cls_show_missing_key(runner, vault_file):
    result = invoke(runner, vault_file, "show", "GHOST")
    assert result.exit_code == 0
    assert "No classification" in result.output


def test_cls_remove_existing(runner, vault_file):
    invoke(runner, vault_file, "set", "MY_VAR", "public")
    result = invoke(runner, vault_file, "remove", "MY_VAR")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_cls_remove_nonexistent(runner, vault_file):
    result = invoke(runner, vault_file, "remove", "NOTHING")
    assert result.exit_code == 0
    assert "No classification" in result.output


def test_cls_list_empty(runner, vault_file):
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No classifications" in result.output


def test_cls_list_shows_entries(runner, vault_file):
    invoke(runner, vault_file, "set", "A", "public")
    invoke(runner, vault_file, "set", "B", "secret")
    result = invoke(runner, vault_file, "list")
    assert "A" in result.output
    assert "B" in result.output


def test_cls_list_filtered_by_level(runner, vault_file):
    invoke(runner, vault_file, "set", "X", "secret")
    invoke(runner, vault_file, "set", "Y", "public")
    result = invoke(runner, vault_file, "list", "--level", "secret")
    assert "X" in result.output
    assert "Y" not in result.output
