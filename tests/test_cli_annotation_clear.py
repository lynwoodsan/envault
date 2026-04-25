"""Tests for the 'annotate clear' CLI command (requires confirmation bypass)."""

import pytest
from click.testing import CliRunner
from envault.cli_annotation import annotation_group
from envault.annotation import set_annotation, list_annotations


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    vf.write_text("{}")
    return str(vf)


def test_ann_clear_removes_all(runner, vault_file):
    set_annotation(vault_file, "A", "note A")
    set_annotation(vault_file, "B", "note B")
    set_annotation(vault_file, "C", "note C")

    result = runner.invoke(
        annotation_group,
        ["clear", "--vault", vault_file, "--yes"]
    )
    assert result.exit_code == 0
    assert "3" in result.output
    assert list_annotations(vault_file) == {}


def test_ann_clear_empty_vault(runner, vault_file):
    result = runner.invoke(
        annotation_group,
        ["clear", "--vault", vault_file, "--yes"]
    )
    assert result.exit_code == 0
    assert "0" in result.output


def test_ann_clear_then_set_works(runner, vault_file):
    set_annotation(vault_file, "OLD", "old note")
    runner.invoke(annotation_group, ["clear", "--vault", vault_file, "--yes"])
    set_annotation(vault_file, "NEW", "new note")
    data = list_annotations(vault_file)
    assert "NEW" in data
    assert "OLD" not in data
