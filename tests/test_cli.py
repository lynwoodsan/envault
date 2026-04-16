import os
import pytest
from click.testing import CliRunner
from envault.cli import cli


PASSWORD = "testpassword"


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return CliRunner()


def invoke(runner, args):
    return runner.invoke(cli, ["--password", PASSWORD] + args)


def test_set_and_list(runner):
    result = invoke(runner, ["set", "FOO", "bar"])
    assert result.exit_code == 0
    assert "Set FOO" in result.output

    result = invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "FOO" in result.output


def test_delete(runner):
    invoke(runner, ["set", "FOO", "bar"])
    result = invoke(runner, ["delete", "FOO"])
    assert result.exit_code == 0
    assert "Deleted FOO" in result.output

    result = invoke(runner, ["list"])
    assert "FOO" not in result.output


def test_export(runner, tmp_path):
    invoke(runner, ["set", "KEY", "value123"])
    out_file = str(tmp_path / "out.env")
    result = invoke(runner, ["export", out_file])
    assert result.exit_code == 0
    content = open(out_file).read()
    assert "KEY" in content
    assert "value123" in content


def test_import(runner, tmp_path):
    env_file = tmp_path / "import.env"
    env_file.write_text('IMPORTED_KEY="hello world"\n')
    result = invoke(runner, ["import", str(env_file)])
    assert result.exit_code == 0
    assert "Imported 1" in result.output

    result = invoke(runner, ["list"])
    assert "IMPORTED_KEY" in result.output


def test_list_empty(runner):
    result = invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "No variables stored" in result.output
