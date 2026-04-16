"""Tests for CLI share-export and share-import commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli import cli
import envault.cli_sharing  # noqa: F401 — registers commands
from envault.vault import set_var, load_vault


PASSWORD = "cliSharePass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def prepared_vault(tmp_path):
    vpath = tmp_path / ".envault"
    set_var(vpath, PASSWORD, "TOKEN", "abc123")
    return tmp_path


def invoke(runner, args, input_text, **kwargs):
    return runner.invoke(cli, args, input=input_text, catch_exceptions=False, **kwargs)


def test_share_export_creates_bundle(runner, prepared_vault):
    bundle = prepared_vault / "bundle.json"
    result = invoke(
        runner,
        ["share-export", str(bundle), "--vault", str(prepared_vault / ".envault")],
        input_text=f"{PASSWORD}\n",
    )
    assert result.exit_code == 0
    assert bundle.exists()
    assert "exported" in result.output


def test_share_export_with_note(runner, prepared_vault):
    bundle = prepared_vault / "bundle.json"
    result = invoke(
        runner,
        ["share-export", str(bundle), "--note", "staging", "--vault", str(prepared_vault / ".envault")],
        input_text=f"{PASSWORD}\n",
    )
    assert result.exit_code == 0
    assert "staging" in result.output


def test_share_import_roundtrip(runner, prepared_vault, tmp_path):
    bundle = prepared_vault / "bundle.json"
    invoke(
        runner,
        ["share-export", str(bundle), "--vault", str(prepared_vault / ".envault")],
        input_text=f"{PASSWORD}\n",
    )
    new_vault = tmp_path / ".envault"
    result = invoke(
        runner,
        ["share-import", str(bundle), "--vault", str(new_vault)],
        input_text=f"{PASSWORD}\n",
    )
    assert result.exit_code == 0
    assert "imported" in result.output
    vars_ = load_vault(new_vault, PASSWORD)
    assert vars_["TOKEN"] == "abc123"


def test_share_export_missing_vault(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["share-export", str(tmp_path / "out.json"), "--vault", str(tmp_path / ".envault")],
        input=f"{PASSWORD}\n",
    )
    assert result.exit_code != 0
