"""Check environment variables against expected schema/requirements."""
from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class CheckRule:
    key: str
    required: bool = True
    pattern: Optional[str] = None
    min_length: int = 0
    description: str = ""


@dataclass
class CheckResult:
    key: str
    status: str  # 'ok', 'missing', 'invalid'
    message: str = ""


def load_rules(rules_data: list[dict]) -> list[CheckRule]:
    return [CheckRule(**r) for r in rules_data]


def check_vars(vault_vars: dict[str, str], rules: list[CheckRule]) -> list[CheckResult]:
    results = []
    for rule in rules:
        value = vault_vars.get(rule.key)
        if value is None:
            if rule.required:
                results.append(CheckResult(rule.key, "missing", "Required variable not set"))
            else:
                results.append(CheckResult(rule.key, "ok", "Optional, not set"))
            continue
        if len(value) < rule.min_length:
            results.append(CheckResult(rule.key, "invalid",
                f"Value too short (min {rule.min_length})"))
            continue
        if rule.pattern and not re.fullmatch(rule.pattern, value):
            results.append(CheckResult(rule.key, "invalid",
                f"Value does not match pattern '{rule.pattern}'"))
            continue
        results.append(CheckResult(rule.key, "ok"))
    return results


def format_check_report(results: list[CheckResult]) -> str:
    lines = []
    for r in results:
        icon = {"ok": "✓", "missing": "✗", "invalid": "!"}.get(r.status, "?")
        msg = f"  {r.message}" if r.message else ""
        lines.append(f"[{icon}] {r.key}{msg}")
    total = len(results)
    issues = sum(1 for r in results if r.status != "ok")
    lines.append(f"\n{total - issues}/{total} checks passed.")
    return "\n".join(lines)
