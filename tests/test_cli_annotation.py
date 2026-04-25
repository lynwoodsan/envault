"""Tests for CLI annotation commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_annotation import annotation_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    vf.write_text("{}")
    return str(vf)


def invoke(runner, vault_file, *args):
    return runner.invoke(annotation_group, [*args, "--vault", vault_file])


def test_ann_set_outputs_confirmation(runner, vault_file):
    result = invoke(runner, vault_file, "set", "DB_HOST", "Primary DB")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "Annotation set" in result.output


def test_ann_get_shows_note(runner, vault_file):
    invoke(runner, vault_file, "set", "API_KEY", "A secret key")
    result = invoke(runner, vault_file, "get", "API_KEY")
    assert result.exit_code == 0
    assert "A secret key" in result.output
    assert "API_KEY" in result.output


def test_ann_get_missing_exits_1(runner, vault_file):
    result = invoke(runner, vault_file, "get", "MISSING_KEY")
    assert result.exit_code == 1
    assert "No annotation" in result.output


def test_ann_remove_existing(runner, vault_file):
    invoke(runner, vault_file, "set", "TO_REMOVE", "will be gone")
    result = invoke(runner, vault_file, "remove", "TO_REMOVE")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_ann_remove_nonexistent_exits_1(runner, vault_file):
    result = invoke(runner, vault_file, "remove", "GHOST")
    assert result.exit_code == 1


def test_ann_list_shows_all(runner, vault_file):
    invoke(runner, vault_file, "set", "KEY_A", "note A")
    invoke(runner, vault_file, "set", "KEY_B", "note B")
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_ann_list_empty(runner, vault_file):
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No annotations" in result.output


def test_ann_set_custom_author(runner, vault_file):
    result = runner.invoke(
        annotation_group,
        ["set", "KEY", "note", "--vault", vault_file, "--author", "bob"]
    )
    assert result.exit_code == 0
    assert "bob" in result.output
