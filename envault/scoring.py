"""Variable strength scoring — rates how 'secure' an env var's value is."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envault.vault import load_vault


@dataclass
class ScoreResult:
    key: str
    score: int          # 0-100
    grade: str          # A/B/C/D/F
    issues: List[str] = field(default_factory=list)


_GRADE_THRESHOLDS = [(90, "A"), (75, "B"), (55, "C"), (35, "D"), (0, "F")]


def _grade(score: int) -> str:
    for threshold, letter in _GRADE_THRESHOLDS:
        if score >= threshold:
            return letter
    return "F"


def score_value(key: str, value: str) -> ScoreResult:
    """Score a single key/value pair and return a ScoreResult."""
    issues: List[str] = []
    score = 100

    if len(value) == 0:
        return ScoreResult(key=key, score=0, grade="F", issues=["Empty value"])

    if len(value) < 8:
        score -= 30
        issues.append("Value is very short (< 8 chars)")
    elif len(value) < 16:
        score -= 15
        issues.append("Value is short (< 16 chars)")

    if value.lower() in {"password", "secret", "changeme", "admin", "1234", "test"}:
        score -= 40
        issues.append("Value matches a common weak secret")

    if re.fullmatch(r"[a-z]+", value):
        score -= 20
        issues.append("Value contains only lowercase letters")
    elif re.fullmatch(r"[0-9]+", value):
        score -= 20
        issues.append("Value contains only digits")

    has_upper = bool(re.search(r"[A-Z]", value))
    has_digit = bool(re.search(r"[0-9]", value))
    has_special = bool(re.search(r"[^A-Za-z0-9]", value))
    complexity = sum([has_upper, has_digit, has_special])
    if complexity == 0:
        score -= 15
        issues.append("No uppercase, digits, or special characters")
    elif complexity == 1:
        score -= 5

    score = max(0, min(100, score))
    return ScoreResult(key=key, score=score, grade=_grade(score), issues=issues)


def score_vault(vault_path: Path, password: str) -> List[ScoreResult]:
    """Score all variables in a vault."""
    data = load_vault(vault_path, password)
    return [score_value(k, v) for k, v in sorted(data.items())]


def format_score_report(results: List[ScoreResult]) -> str:
    if not results:
        return "No variables to score."
    lines = []
    for r in results:
        prefix = f"[{r.grade}] {r.key} ({r.score}/100)"
        if r.issues:
            lines.append(prefix)
            for issue in r.issues:
                lines.append(f"    - {issue}")
        else:
            lines.append(f"{prefix} — OK")
    return "\n".join(lines)
