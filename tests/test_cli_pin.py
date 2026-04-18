import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_pin import pin_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.write_text("dummy")
    return vf


def invoke(runner, vault_file, *args):
    return runner.invoke(pin_group, [*args, "--vault", str(vault_file)])


def test_pin_add(runner, vault_file):
    result = invoke(runner, vault_file, "add", "MY_KEY")
    assert result.exit_code == 0
    assert "Pinned 'MY_KEY'" in result.output


def test_pin_add_with_reason(runner, vault_file):
    result = invoke(runner, vault_file, "add", "MY_KEY", "--reason", "critical")
    assert result.exit_code == 0
    assert "critical" in result.output


def test_pin_list_empty(runner, vault_file):
    result = invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No pinned" in result.output


def test_pin_list_shows_keys(runner, vault_file):
    invoke(runner, vault_file, "add", "KEY_A", "--reason", "important")
    invoke(runner, vault_file, "add", "KEY_B")
    result = invoke(runner, vault_file, "list")
    assert "KEY_A" in result.output
    assert "important" in result.output
    assert "KEY_B" in result.output


def test_pin_remove(runner, vault_file):
    invoke(runner, vault_file, "add", "KEY_X")
    result = invoke(runner, vault_file, "remove", "KEY_X")
    assert result.exit_code == 0
    assert "Unpinned" in result.output


def test_pin_remove_nonexistent(runner, vault_file):
    result = invoke(runner, vault_file, "remove", "GHOST")
    assert result.exit_code == 1


def test_pin_check_pinned(runner, vault_file):
    invoke(runner, vault_file, "add", "Z")
    result = invoke(runner, vault_file, "check", "Z")
    assert "is pinned" in result.output


def test_pin_check_not_pinned(runner, vault_file):
    result = invoke(runner, vault_file, "check", "NOPE")
    assert "is not pinned" in result.output
