import pytest
from envault.lint import lint_key, lint_value, lint_vars, format_lint_report, LintIssue


def test_valid_key_no_issues():
    issues = lint_key("DATABASE_URL")
    assert issues == []


def test_lowercase_key_is_error():
    issues = lint_key("database_url")
    assert any(i.level == 'error' for i in issues)


def test_key_with_leading_underscore_warning():
    issues = lint_key("_PRIVATE")
    # leading underscore is also invalid per regex, but check warning exists
    assert any('underscore' in i.message for i in issues)


def test_key_with_numbers_valid():
    issues = lint_key("API_KEY_2")
    assert issues == []


def test_empty_value_warning():
    issues = lint_value("MY_VAR", "")
    assert any(i.level == 'warning' for i in issues)


def test_placeholder_value_warning():
    for placeholder in ["changeme", "TODO", "example"]:
        issues = lint_value("MY_VAR", placeholder)
        assert any('placeholder' in i.message.lower() for i in issues)


def test_normal_value_no_issues():
    issues = lint_value("MY_VAR", "some-real-value-123")
    assert issues == []


def test_long_value_warning():
    issues = lint_value("BIG", "x" * 5000)
    assert any('long' in i.message for i in issues)


def test_lint_vars_combined():
    variables = {
        "GOOD_KEY": "real_value",
        "bad_key": "also_fine",
        "EMPTY_VAR": "",
    }
    issues = lint_vars(variables)
    keys_with_issues = {i.key for i in issues}
    assert "bad_key" in keys_with_issues
    assert "EMPTY_VAR" in keys_with_issues


def test_lint_vars_duplicate_secret_values():
    variables = {
        "API_KEY": "shared_secret",
        "API_TOKEN": "shared_secret",
    }
    issues = lint_vars(variables)
    assert any('copy-paste' in i.message for i in issues)


def test_format_lint_report_no_issues():
    assert format_lint_report([]) == "No issues found."


def test_format_lint_report_with_issues():
    issues = [
        LintIssue(key="X", level='error', message="Bad key"),
        LintIssue(key="Y", level='warning', message="Suspicious value"),
    ]
    report = format_lint_report(issues)
    assert "[ERROR]" in report
    assert "[WARN]" in report
    assert "Bad key" in report
