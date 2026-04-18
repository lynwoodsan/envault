import pytest
from click.testing import CliRunner
from envault.cli_compare import compare_group
from envault.vault import save_vault
import os


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args, **kwargs):
    return runner.invoke(compare_group, *args, catch_exceptions=False, **kwargs)


@pytest.fixture
def two_vaults(tmp_path):
    a = str(tmp_path / "a.vault")
    b = str(tmp_path / "b.vault")
    save_vault(a, {"FOO": "same", "BAR": "left_only"}, "passA")
    save_vault(b, {"FOO": "same", "BAZ": "right_only"}, "passB")
    return a, b


def test_cmp_vaults_output(runner, two_vaults):
    a, b = two_vaults
    result = invoke(runner, ["vaults", a, b, "--password-a", "passA", "--password-b", "passB"])
    assert "FOO" in result.output
    assert "Summary" in result.output


def test_cmp_vaults_exits_1_on_diff(runner, two_vaults):
    a, b = two_vaults
    result = runner.invoke(compare_group, ["vaults", a, b, "--password-a", "passA", "--password-b", "passB"])
    assert result.exit_code == 1


def test_cmp_vaults_exits_0_on_match(runner, tmp_path):
    a = str(tmp_path / "a.vault")
    b = str(tmp_path / "b.vault")
    save_vault(a, {"X": "1"}, "pw")
    save_vault(b, {"X": "1"}, "pw")
    result = runner.invoke(compare_group, ["vaults", a, b, "--password-a", "pw", "--password-b", "pw"])
    assert result.exit_code == 0


def test_cmp_dotenv(runner, tmp_path):
    vault = str(tmp_path / "v.vault")
    dotenv = str(tmp_path / ".env")
    save_vault(vault, {"FOO": "bar"}, "pw")
    with open(dotenv, "w") as f:
        f.write("FOO=bar\n")
    result = runner.invoke(compare_group, ["dotenv", vault, dotenv, "--password", "pw"])
    assert "match" in result.output
    assert result.exit_code == 0


def test_cmp_dotenv_mismatch(runner, tmp_path):
    vault = str(tmp_path / "v.vault")
    dotenv = str(tmp_path / ".env")
    save_vault(vault, {"FOO": "bar"}, "pw")
    with open(dotenv, "w") as f:
        f.write("FOO=different\n")
    result = runner.invoke(compare_group, ["dotenv", vault, dotenv, "--password", "pw"])
    assert result.exit_code == 1
