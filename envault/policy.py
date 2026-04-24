"""Policy enforcement for vault variables — define and check rules like required prefix, forbidden patterns, max length, etc."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class PolicyRule:
    name: str
    required_prefix: Optional[str] = None
    forbidden_pattern: Optional[str] = None
    max_length: Optional[int] = None
    allowed_keys: Optional[List[str]] = None


@dataclass
class PolicyViolation:
    key: str
    rule: str
    message: str


def _policy_path(vault_path: Path) -> Path:
    return vault_path.parent / ".envault_policy.json"


def load_policy(vault_path: Path) -> List[PolicyRule]:
    path = _policy_path(vault_path)
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return [PolicyRule(**r) for r in data.get("rules", [])]


def save_policy(vault_path: Path, rules: List[PolicyRule]) -> None:
    path = _policy_path(vault_path)
    data = {"rules": [r.__dict__ for r in rules]}
    path.write_text(json.dumps(data, indent=2))


def add_rule(vault_path: Path, rule: PolicyRule) -> None:
    rules = load_policy(vault_path)
    rules = [r for r in rules if r.name != rule.name]
    rules.append(rule)
    save_policy(vault_path, rules)


def remove_rule(vault_path: Path, name: str) -> bool:
    rules = load_policy(vault_path)
    new_rules = [r for r in rules if r.name != name]
    if len(new_rules) == len(rules):
        return False
    save_policy(vault_path, new_rules)
    return True


def check_policy(vault_path: Path, variables: dict) -> List[PolicyViolation]:
    rules = load_policy(vault_path)
    violations: List[PolicyViolation] = []
    for rule in rules:
        for key, value in variables.items():
            if rule.required_prefix and not key.startswith(rule.required_prefix):
                violations.append(PolicyViolation(key, rule.name,
                    f"Key '{key}' does not start with required prefix '{rule.required_prefix}'"))
            if rule.forbidden_pattern and re.search(rule.forbidden_pattern, value):
                violations.append(PolicyViolation(key, rule.name,
                    f"Value for '{key}' matches forbidden pattern '{rule.forbidden_pattern}'"))
            if rule.max_length and len(value) > rule.max_length:
                violations.append(PolicyViolation(key, rule.name,
                    f"Value for '{key}' exceeds max length {rule.max_length}"))
            if rule.allowed_keys and key not in rule.allowed_keys:
                violations.append(PolicyViolation(key, rule.name,
                    f"Key '{key}' is not in the allowed keys list for rule '{rule.name}'"))
    return violations


def format_policy_report(violations: List[PolicyViolation]) -> str:
    if not violations:
        return "Policy check passed. No violations found."
    lines = [f"Policy violations ({len(violations)}):", ""]
    for v in violations:
        lines.append(f"  [{v.rule}] {v.key}: {v.message}")
    return "\n".join(lines)
