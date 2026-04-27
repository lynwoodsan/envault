"""Tests for CLI retention commands."""
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_retention import retention_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.write_text("placeholder")
    return tmp_path, str(vf)


def invoke(runner, tmp_path, vault_file, *args):
    return runner.invoke(retention_group, [*args, "--vault", vault_file])


def test_ret_set_outputs_confirmation(runner, vault_dir):
    tmp_path, vf = vault_dir
    result = invoke(runner, tmp_path, vf, "set", "API_KEY", "--days", "30")
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "30" in result.output
    assert "warn" in result.output


def test_ret_set_custom_action(runner, vault_dir):
    tmp_path, vf = vault_dir
    result = invoke(runner, tmp_path, vf, "set", "SECRET", "--days", "7", "--action", "delete")
    assert result.exit_code == 0
    assert "delete" in result.output


def test_ret_set_invalid_days_exits_nonzero(runner, vault_dir):
    tmp_path, vf = vault_dir
    result = invoke(runner, tmp_path, vf, "set", "KEY", "--days", "0")
    assert result.exit_code != 0


def test_ret_remove_existing(runner, vault_dir):
    tmp_path, vf = vault_dir
    invoke(runner, tmp_path, vf, "set", "TOKEN", "--days", "14")
    result = invoke(runner, tmp_path, vf, "remove", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_ret_remove_nonexistent_exits_nonzero(runner, vault_dir):
    tmp_path, vf = vault_dir
    result = invoke(runner, tmp_path, vf, "remove", "GHOST")
    assert result.exit_code != 0


def test_ret_show_existing(runner, vault_dir):
    tmp_path, vf = vault_dir
    invoke(runner, tmp_path, vf, "set", "DB_PASS", "--days", "60", "--action", "archive")
    result = invoke(runner, tmp_path, vf, "show", "DB_PASS")
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "60" in result.output
    assert "archive" in result.output


def test_ret_show_missing_exits_nonzero(runner, vault_dir):
    tmp_path, vf = vault_dir
    result = invoke(runner, tmp_path, vf, "show", "MISSING")
    assert result.exit_code != 0


def test_ret_list_empty(runner, vault_dir):
    tmp_path, vf = vault_dir
    result = invoke(runner, tmp_path, vf, "list")
    assert result.exit_code == 0
    assert "No retention" in result.output


def test_ret_list_shows_entries(runner, vault_dir):
    tmp_path, vf = vault_dir
    invoke(runner, tmp_path, vf, "set", "A", "--days", "10")
    invoke(runner, tmp_path, vf, "set", "B", "--days", "20")
    result = invoke(runner, tmp_path, vf, "list")
    assert "A" in result.output
    assert "B" in result.output


def test_ret_due_no_expired(runner, vault_dir):
    tmp_path, vf = vault_dir
    invoke(runner, tmp_path, vf, "set", "FRESH", "--days", "90")
    result = invoke(runner, tmp_path, vf, "due")
    assert result.exit_code == 0
    assert "No keys" in result.output


def test_ret_due_shows_expired(runner, vault_dir):
    tmp_path, vf = vault_dir
    invoke(runner, tmp_path, vf, "set", "OLD", "--days", "1")
    retention_json = tmp_path / ".envault_retention.json"
    data = json.loads(retention_json.read_text())
    data["OLD"]["due_at"] = (datetime.utcnow() - timedelta(days=2)).isoformat()
    retention_json.write_text(json.dumps(data))
    result = invoke(runner, tmp_path, vf, "due")
    assert "OLD" in result.output
