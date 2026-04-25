"""Tests for envault.scoring."""
import pytest
from pathlib import Path
from envault.scoring import score_value, score_vault, format_score_report, ScoreResult
from envault.vault import save_vault


# ---------------------------------------------------------------------------
# score_value
# ---------------------------------------------------------------------------

def test_empty_value_scores_zero():
    r = score_value("KEY", "")
    assert r.score == 0
    assert r.grade == "F"
    assert any("Empty" in i for i in r.issues)


def test_common_weak_secret_penalised():
    r = score_value("DB_PASS", "password")
    assert r.score < 50
    assert any("common" in i.lower() for i in r.issues)


def test_short_value_penalised():
    r = score_value("TOKEN", "abc")
    assert r.score < 70
    assert any("short" in i.lower() for i in r.issues)


def test_strong_value_scores_high():
    r = score_value("API_KEY", "X9#mK!qR2@vLpZ7n")
    assert r.score >= 90
    assert r.grade == "A"
    assert r.issues == []


def test_only_digits_penalised():
    r = score_value("PIN", "12345678")
    assert any("digit" in i.lower() for i in r.issues)


def test_only_lowercase_penalised():
    r = score_value("SECRET", "abcdefghij")
    assert any("lowercase" in i.lower() for i in r.issues)


def test_grade_boundaries():
    assert ScoreResult("K", 90, "A").grade == "A"
    assert ScoreResult("K", 75, "B").grade == "B"
    assert ScoreResult("K", 55, "C").grade == "C"


# ---------------------------------------------------------------------------
# score_vault
# ---------------------------------------------------------------------------

@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.env"
    save_vault(p, "pw", {"STRONG": "X9#mK!qR2@vLpZ7n", "WEAK": "password"})
    return p


def test_score_vault_returns_all_keys(vault_file):
    results = score_vault(vault_file, "pw")
    keys = {r.key for r in results}
    assert "STRONG" in keys
    assert "WEAK" in keys


def test_score_vault_strong_beats_weak(vault_file):
    results = score_vault(vault_file, "pw")
    by_key = {r.key: r for r in results}
    assert by_key["STRONG"].score > by_key["WEAK"].score


# ---------------------------------------------------------------------------
# format_score_report
# ---------------------------------------------------------------------------

def test_format_empty_report():
    assert format_score_report([]) == "No variables to score."


def test_format_report_contains_key():
    r = score_value("MY_KEY", "short")
    report = format_score_report([r])
    assert "MY_KEY" in report


def test_format_report_shows_issues():
    r = score_value("X", "password")
    report = format_score_report([r])
    assert "-" in report
