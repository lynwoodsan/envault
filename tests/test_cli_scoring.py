"""Tests for envault.cli_scoring."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_scoring import score_group
from envault.vault import save_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def prepared_vault(tmp_path):
    p = tmp_path / "vault.env"
    save_vault(p, "secret", {
        "STRONG_KEY": "X9#mK!qR2@vLpZ7n",
        "WEAK_KEY": "password",
    })
    return p


def invoke(runner, args, vault, extra_env=None):
    env = {"ENVAULT_PASSWORD": "secret"}
    if extra_env:
        env.update(extra_env)
    return runner.invoke(score_group, ["--vault", str(vault)] + args, env=env)


def test_score_run_shows_keys(runner, prepared_vault):
    result = invoke(runner, ["run"], prepared_vault)
    assert result.exit_code == 0
    assert "STRONG_KEY" in result.output
    assert "WEAK_KEY" in result.output


def test_score_run_shows_grades(runner, prepared_vault):
    result = invoke(runner, ["run"], prepared_vault)
    assert "[A]" in result.output or "[B]" in result.output
    assert "[F]" in result.output or "[D]" in result.output


def test_score_run_min_grade_exits_1_on_weak(runner, prepared_vault):
    result = invoke(runner, ["run", "--min-grade", "B"], prepared_vault)
    assert result.exit_code == 1


def test_score_run_min_grade_passes_when_all_strong(runner, tmp_path):
    p = tmp_path / "vault.env"
    save_vault(p, "secret", {"KEY": "X9#mK!qR2@vLpZ7n"})
    result = invoke(runner, ["run", "--min-grade", "A"], p)
    assert result.exit_code == 0


def test_score_run_missing_vault(runner, tmp_path):
    result = invoke(runner, ["run"], tmp_path / "missing.env")
    assert result.exit_code == 1
    assert "not found" in result.output.lower() or "not found" in (result.output + "").lower()


def test_score_check_strong_value(runner):
    result = runner.invoke(score_group, ["check", "API_KEY", "X9#mK!qR2@vLpZ7n"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_score_check_weak_value_exits_1(runner):
    result = runner.invoke(score_group, ["check", "DB_PASS", "password"])
    assert result.exit_code == 1
    assert "DB_PASS" in result.output


def test_score_check_shows_issues(runner):
    result = runner.invoke(score_group, ["check", "X", "abc"])
    assert "-" in result.output
