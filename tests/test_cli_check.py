import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from envault.cli_check import check_group
from envault.vault import set_var


PASSWORD = "checkpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def prepared_vault(tmp_path):
    vault_file = tmp_path / ".envault"
    set_var(vault_file, PASSWORD, "DB_URL", "postgres://localhost")
    set_var(vault_file, PASSWORD, "SECRET", "abc123")
    return vault_file


def invoke(runner, vault_file, args):
    with patch("envault.cli_check.get_password", return_value=PASSWORD):
        return runner.invoke(check_group, ["--vault", str(vault_file)] + args)


def test_check_run_all_ok(runner, prepared_vault, tmp_path):
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps([
        {"key": "DB_URL", "required": True, "pattern": None, "min_length": 0, "description": ""},
        {"key": "SECRET", "required": True, "pattern": None, "min_length": 0, "description": ""},
    ]))
    result = invoke(runner, prepared_vault, ["run", str(schema)])
    assert result.exit_code == 0
    assert "2/2" in result.output


def test_check_run_missing_key_exits_1(runner, prepared_vault, tmp_path):
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps([
        {"key": "MISSING_VAR", "required": True, "pattern": None, "min_length": 0, "description": ""},
    ]))
    result = invoke(runner, prepared_vault, ["run", str(schema)])
    assert result.exit_code == 1
    assert "✗" in result.output


def test_check_init_schema_creates_file(runner, prepared_vault, tmp_path):
    out = tmp_path / "out.json"
    result = invoke(runner, prepared_vault, ["init-schema", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    keys = [r["key"] for r in data]
    assert "DB_URL" in keys
    assert "SECRET" in keys


def test_check_run_pattern_failure(runner, prepared_vault, tmp_path):
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps([
        {"key": "SECRET", "required": True, "pattern": "^[0-9]+$", "min_length": 0, "description": ""},
    ]))
    result = invoke(runner, prepared_vault, ["run", str(schema)])
    assert result.exit_code == 1
    assert "!" in result.output
