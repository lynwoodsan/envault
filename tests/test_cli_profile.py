import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_profile import profile_group
from envault.vault import set_var


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def prepared_vault(tmp_path):
    vault = str(tmp_path / ".envault")
    pw = "testpass"
    set_var(vault, pw, "API_KEY", "abc123")
    set_var(vault, pw, "DB_URL", "postgres://localhost/db")
    return vault, pw


def invoke(runner, args, vault, password=None):
    full = ["--vault", vault] + args
    env = {"ENVAULT_PASSWORD": password} if password else {}
    return runner.invoke(profile_group, full, env=env)


def test_create_profile(runner, prepared_vault):
    vault, pw = prepared_vault
    result = invoke(runner, ["create", "dev"], vault)
    assert result.exit_code == 0
    assert "created" in result.output


def test_delete_profile(runner, prepared_vault):
    vault, pw = prepared_vault
    invoke(runner, ["create", "dev"], vault)
    result = invoke(runner, ["delete", "dev"], vault)
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_nonexistent_profile(runner, prepared_vault):
    vault, pw = prepared_vault
    result = invoke(runner, ["delete", "ghost"], vault)
    assert result.exit_code == 1


def test_assign_and_list(runner, prepared_vault):
    vault, pw = prepared_vault
    invoke(runner, ["create", "dev"], vault)
    invoke(runner, ["assign", "dev", "API_KEY"], vault)
    result = invoke(runner, ["list"], vault)
    assert "API_KEY" in result.output


def test_unassign_key(runner, prepared_vault):
    vault, pw = prepared_vault
    invoke(runner, ["assign", "dev", "API_KEY"], vault)
    result = invoke(runner, ["unassign", "dev", "API_KEY"], vault)
    assert result.exit_code == 0


def test_unassign_missing_key(runner, prepared_vault):
    vault, pw = prepared_vault
    invoke(runner, ["create", "dev"], vault)
    result = invoke(runner, ["unassign", "dev", "NOPE"], vault)
    assert result.exit_code == 1


def test_list_empty(runner, prepared_vault):
    vault, pw = prepared_vault
    result = invoke(runner, ["list"], vault)
    assert "No profiles" in result.output


def test_show_profile(runner, prepared_vault):
    vault, pw = prepared_vault
    invoke(runner, ["assign", "dev", "API_KEY"], vault)
    result = runner.invoke(
        profile_group,
        ["--vault", vault, "show", "dev", "--password", pw]
    )
    assert result.exit_code == 0
    assert "API_KEY=abc123" in result.output
