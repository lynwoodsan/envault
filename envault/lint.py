"""Lint/validation checks for vault variable names and values."""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LintIssue:
    key: str
    level: str  # 'error' | 'warning'
    message: str


_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_SECRETS_PATTERN = re.compile(r'(password|secret|token|key|api)', re.IGNORECASE)
_PLACEHOLDER_RE = re.compile(r'^(todo|fixme|changeme|placeholder|example|test)$', re.IGNORECASE)


def lint_key(key: str) -> List[LintIssue]:
    issues = []
    if not _VALID_KEY_RE.match(key):
        issues.append(LintIssue(key=key, level='error',
            message=f"Key '{key}' must be uppercase with underscores (A-Z, 0-9, _)"))
    if key.startswith('_'):
        issues.append(LintIssue(key=key, level='warning',
            message=f"Key '{key}' starts with underscore, which is unconventional"))
    return issues


def lint_value(key: str, value: str) -> List[LintIssue]:
    issues = []
    if not value.strip():
        issues.append(LintIssue(key=key, level='warning',
            message=f"Key '{key}' has an empty or whitespace-only value"))
    if _PLACEHOLDER_RE.match(value.strip()):
        issues.append(LintIssue(key=key, level='warning',
            message=f"Key '{key}' appears to have a placeholder value: '{value}'"))
    if len(value) > 4096:
        issues.append(LintIssue(key=key, level='warning',
            message=f"Key '{key}' value is unusually long ({len(value)} chars)"))
    return issues


def lint_vars(variables: dict) -> List[LintIssue]:
    """Run all lint checks on a dict of key->value pairs."""
    issues = []
    seen_values: dict = {}
    for key, value in variables.items():
        issues.extend(lint_key(key))
        issues.extend(lint_value(key, value))
        if _SECRETS_PATTERN.search(key) and value in seen_values:
            issues.append(LintIssue(key=key, level='warning',
                message=f"Key '{key}' shares its value with '{seen_values[value]}' — possible copy-paste error"))
        seen_values[value] = key
    return issues


def format_lint_report(issues: List[LintIssue]) -> str:
    if not issues:
        return "No issues found."
    lines = []
    for issue in issues:
        prefix = "[ERROR]" if issue.level == 'error' else "[WARN] "
        lines.append(f"{prefix} {issue.message}")
    return "\n".join(lines)
