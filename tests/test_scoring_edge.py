"""Edge-case and integration tests for scoring."""
import pytest
from envault.scoring import score_value, score_vault, format_score_report, ScoreResult
from envault.vault import save_vault


def test_score_returns_score_result_type():
    r = score_value("K", "someValue1!")
    assert isinstance(r, ScoreResult)


def test_score_key_preserved():
    r = score_value("MY_SECRET", "hello")
    assert r.key == "MY_SECRET"


def test_score_100_cap():
    # Even an extremely strong value should not exceed 100
    r = score_value("K", "aB3!dE6@gH9#jK2$mN5%")
    assert r.score <= 100


def test_score_zero_floor():
    r = score_value("K", "")
    assert r.score >= 0


def test_format_report_ok_label_when_no_issues():
    r = ScoreResult(key="K", score=95, grade="A", issues=[])
    report = format_score_report([r])
    assert "OK" in report


def test_format_report_multiple_keys():
    results = [
        score_value("A", "X9#mK!qR2@vLpZ7n"),
        score_value("B", "password"),
    ]
    report = format_score_report(results)
    assert "A" in report
    assert "B" in report


def test_score_vault_empty(tmp_path):
    p = tmp_path / "vault.env"
    save_vault(p, "pw", {})
    results = score_vault(p, "pw")
    assert results == []


def test_score_vault_wrong_password_raises(tmp_path):
    p = tmp_path / "vault.env"
    save_vault(p, "correct", {"K": "v"})
    with pytest.raises(Exception):
        score_vault(p, "wrong")


def test_score_value_with_special_chars_only():
    # A value that is long but only special chars — should still score reasonably
    r = score_value("K", "!@#$%^&*()_+-=")
    assert r.score > 0


def test_score_16_char_value_no_short_penalty():
    r = score_value("K", "abcdefghijklmnop")
    short_issues = [i for i in r.issues if "short" in i.lower()]
    assert short_issues == []
