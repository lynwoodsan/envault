"""Tests for envault/cli_expiry.py"""

import json
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from click.testing import CliRunner

from envault.cli_expiry import expiry_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    vf = tmp_path / "test.vault"
    vf.write_text("{}")
    return tmp_path, str(vf)


def invoke(runner, args, vault):
    return runner.invoke(expiry_group, args + ["--vault", vault])


def test_exp_set_outputs_expiry(runner, vault_dir):
    _, vf = vault_dir
    result = invoke(runner, ["set", "API_KEY", "30"], vf)
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "UTC" in result.output


def test_exp_set_invalid_days_exits_nonzero(runner, vault_dir):
    _, vf = vault_dir
    result = invoke(runner, ["set", "API_KEY", "0"], vf)
    assert result.exit_code != 0


def test_exp_get_shows_expiry(runner, vault_dir):
    _, vf = vault_dir
    invoke(runner, ["set", "DB_PASS", "7"], vf)
    result = invoke(runner, ["get", "DB_PASS"], vf)
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "UTC" in result.output


def test_exp_get_no_expiry(runner, vault_dir):
    _, vf = vault_dir
    result = invoke(runner, ["get", "MISSING"], vf)
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_exp_get_shows_expired_label(runner, vault_dir):
    tmp, vf = vault_dir
    p = tmp / ".envault_expiry.json"
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    p.write_text(json.dumps({"OLD": past}))
    result = invoke(runner, ["get", "OLD"], vf)
    assert "EXPIRED" in result.output


def test_exp_list_empty(runner, vault_dir):
    _, vf = vault_dir
    result = invoke(runner, ["list"], vf)
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_exp_list_shows_keys(runner, vault_dir):
    _, vf = vault_dir
    invoke(runner, ["set", "KEY_A", "5"], vf)
    invoke(runner, ["set", "KEY_B", "10"], vf)
    result = invoke(runner, ["list"], vf)
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_exp_list_expired_only(runner, vault_dir):
    tmp, vf = vault_dir
    p = tmp / ".envault_expiry.json"
    now = datetime.now(timezone.utc)
    data = {
        "OLD": (now - timedelta(days=1)).isoformat(),
        "NEW": (now + timedelta(days=5)).isoformat(),
    }
    p.write_text(json.dumps(data))
    result = invoke(runner, ["list", "--expired-only"], vf)
    assert "OLD" in result.output
    assert "NEW" not in result.output


def test_exp_remove_existing(runner, vault_dir):
    _, vf = vault_dir
    invoke(runner, ["set", "TOKEN", "3"], vf)
    result = invoke(runner, ["remove", "TOKEN"], vf)
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_exp_remove_nonexistent(runner, vault_dir):
    _, vf = vault_dir
    result = invoke(runner, ["remove", "GHOST"], vf)
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_exp_purge_dry_run(runner, vault_dir):
    tmp, vf = vault_dir
    p = tmp / ".envault_expiry.json"
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    p.write_text(json.dumps({"STALE": past}))
    result = invoke(runner, ["purge", "--dry-run"], vf)
    assert "dry-run" in result.output
    assert p.exists()  # file untouched


def test_exp_purge_removes_expired(runner, vault_dir):
    tmp, vf = vault_dir
    p = tmp / ".envault_expiry.json"
    past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    p.write_text(json.dumps({"STALE": past}))
    result = invoke(runner, ["purge"], vf)
    assert result.exit_code == 0
    remaining = json.loads(p.read_text())
    assert "STALE" not in remaining
