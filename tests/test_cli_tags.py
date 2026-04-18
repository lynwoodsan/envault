"""Tests for CLI tag commands."""
import pytest
from click.testing import CliRunner
from envault.cli import cli
from envault.vault import set_var

PASSWORD = "cli-test-pass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def prepared_vault(tmp_path):
    vf = str(tmp_path / "vault.json")
    set_var(vf, PASSWORD, "DB_HOST", "localhost")
    set_var(vf, PASSWORD, "API_KEY", "abc123")
    return vf


def invoke(runner, vault_file, *args):
    return runner.invoke(cli, list(args) + ["--vault", vault_file],
                         input=PASSWORD + "\n", catch_exceptions=False)


def test_tag_add(runner, prepared_vault):
    result = invoke(runner, prepared_vault, "tag", "add", "DB_HOST", "infra")
    assert result.exit_code == 0
    assert "Tagged DB_HOST" in result.output


def test_tag_list(runner, prepared_vault):
    invoke(runner, prepared_vault, "tag", "add", "DB_HOST", "infra")
    result = invoke(runner, prepared_vault, "tag", "list", "DB_HOST")
    assert "infra" in result.output


def test_tag_list_empty(runner, prepared_vault):
    result = invoke(runner, prepared_vault, "tag", "list", "API_KEY")
    assert "No tags" in result.output


def test_tag_remove(runner, prepared_vault):
    invoke(runner, prepared_vault, "tag", "add", "API_KEY", "external")
    result = invoke(runner, prepared_vault, "tag", "remove", "API_KEY", "external")
    assert "Removed" in result.output


def test_tag_remove_nonexistent(runner, prepared_vault):
    result = runner.invoke(cli, ["tag", "remove", "API_KEY", "ghost",
                                  "--vault", prepared_vault],
                           input=PASSWORD + "\n", catch_exceptions=False)
    assert "not found" in result.output


def test_tag_find(runner, prepared_vault):
    invoke(runner, prepared_vault, "tag", "add", "DB_HOST", "database")
    invoke(runner, prepared_vault, "tag", "add", "API_KEY", "database")
    result = invoke(runner, prepared_vault, "tag", "find", "database")
    assert "DB_HOST" in result.output
    assert "API_KEY" in result.output


def test_tag_find_none(runner, prepared_vault):
    result = invoke(runner, prepared_vault, "tag", "find", "missing")
    assert "No variables" in result.output
