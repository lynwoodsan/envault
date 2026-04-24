"""Tests for envault/policy.py"""

import pytest
from pathlib import Path
from envault.policy import (
    PolicyRule, PolicyViolation,
    load_policy, save_policy, add_rule, remove_rule,
    check_policy, format_policy_report,
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "test.vault"


def test_load_policy_missing_returns_empty(vault_file):
    rules = load_policy(vault_file)
    assert rules == []


def test_save_and_load_roundtrip(vault_file):
    rule = PolicyRule(name="prefix_rule", required_prefix="APP_")
    save_policy(vault_file, [rule])
    loaded = load_policy(vault_file)
    assert len(loaded) == 1
    assert loaded[0].name == "prefix_rule"
    assert loaded[0].required_prefix == "APP_"


def test_add_rule_appends(vault_file):
    add_rule(vault_file, PolicyRule(name="r1", required_prefix="X_"))
    add_rule(vault_file, PolicyRule(name="r2", max_length=64))
    rules = load_policy(vault_file)
    assert len(rules) == 2


def test_add_rule_overwrites_same_name(vault_file):
    add_rule(vault_file, PolicyRule(name="r1", required_prefix="OLD_"))
    add_rule(vault_file, PolicyRule(name="r1", required_prefix="NEW_"))
    rules = load_policy(vault_file)
    assert len(rules) == 1
    assert rules[0].required_prefix == "NEW_"


def test_remove_rule_returns_true(vault_file):
    add_rule(vault_file, PolicyRule(name="r1", required_prefix="A_"))
    result = remove_rule(vault_file, "r1")
    assert result is True
    assert load_policy(vault_file) == []


def test_remove_nonexistent_rule_returns_false(vault_file):
    result = remove_rule(vault_file, "ghost")
    assert result is False


def test_check_required_prefix_violation(vault_file):
    add_rule(vault_file, PolicyRule(name="prefix", required_prefix="APP_"))
    violations = check_policy(vault_file, {"DB_HOST": "localhost"})
    assert len(violations) == 1
    assert violations[0].key == "DB_HOST"


def test_check_required_prefix_pass(vault_file):
    add_rule(vault_file, PolicyRule(name="prefix", required_prefix="APP_"))
    violations = check_policy(vault_file, {"APP_HOST": "localhost"})
    assert violations == []


def test_check_forbidden_pattern(vault_file):
    add_rule(vault_file, PolicyRule(name="no_secrets", forbidden_pattern=r"password"))
    violations = check_policy(vault_file, {"KEY": "my_password_123"})
    assert len(violations) == 1


def test_check_max_length(vault_file):
    add_rule(vault_file, PolicyRule(name="short", max_length=5))
    violations = check_policy(vault_file, {"KEY": "toolongvalue"})
    assert len(violations) == 1


def test_check_no_violations_returns_empty(vault_file):
    add_rule(vault_file, PolicyRule(name="short", max_length=50))
    violations = check_policy(vault_file, {"KEY": "ok"})
    assert violations == []


def test_format_report_no_violations():
    report = format_policy_report([])
    assert "passed" in report


def test_format_report_with_violations():
    v = PolicyViolation(key="DB_HOST", rule="prefix", message="Missing prefix")
    report = format_policy_report([v])
    assert "DB_HOST" in report
    assert "prefix" in report
