import pytest
from envault.env_check import CheckRule, check_vars, load_rules, format_check_report


VARS = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "supersecret123",
    "PORT": "8080",
}


def test_all_present_ok():
    rules = [CheckRule(key="DATABASE_URL"), CheckRule(key="SECRET_KEY")]
    results = check_vars(VARS, rules)
    assert all(r.status == "ok" for r in results)


def test_missing_required():
    rules = [CheckRule(key="MISSING_VAR", required=True)]
    results = check_vars(VARS, rules)
    assert results[0].status == "missing"


def test_missing_optional_ok():
    rules = [CheckRule(key="OPTIONAL_VAR", required=False)]
    results = check_vars(VARS, rules)
    assert results[0].status == "ok"


def test_pattern_match_ok():
    rules = [CheckRule(key="PORT", pattern=r"\d+")]
    results = check_vars(VARS, rules)
    assert results[0].status == "ok"


def test_pattern_mismatch_invalid():
    rules = [CheckRule(key="PORT", pattern=r"[a-z]+")]
    results = check_vars(VARS, rules)
    assert results[0].status == "invalid"
    assert "pattern" in results[0].message


def test_min_length_fail():
    rules = [CheckRule(key="PORT", min_length=10)]
    results = check_vars(VARS, rules)
    assert results[0].status == "invalid"
    assert "short" in results[0].message


def test_load_rules_from_dicts():
    data = [{"key": "FOO", "required": True, "pattern": ".*", "min_length": 0, "description": ""}]
    rules = load_rules(data)
    assert len(rules) == 1
    assert rules[0].key == "FOO"


def test_format_check_report_contains_summary():
    rules = [CheckRule(key="DATABASE_URL"), CheckRule(key="MISSING", required=True)]
    results = check_vars(VARS, rules)
    report = format_check_report(results)
    assert "1/2" in report
    assert "✗" in report
    assert "✓" in report
