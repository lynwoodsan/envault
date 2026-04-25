"""Badge generation for vault health/status summary."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.scoring import score_vault
from envault.expiry import get_expiry, list_expiry
from envault.ttl import list_ttl, is_expired
from envault.vault import list_vars


@dataclass
class BadgeSummary:
    total_vars: int
    avg_score: float
    grade: str
    expired_count: int
    expiring_soon_count: int
    issues: List[str] = field(default_factory=list)


def _grade_from_score(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 55:
        return "C"
    if score >= 35:
        return "D"
    return "F"


def generate_badge(vault_path: Path, password: str, warn_days: int = 7) -> BadgeSummary:
    """Produce a BadgeSummary for the vault at *vault_path*."""
    from datetime import datetime, timezone

    vars_ = list_vars(vault_path, password)
    total = len(vars_)

    if total == 0:
        return BadgeSummary(
            total_vars=0,
            avg_score=0.0,
            grade="F",
            expired_count=0,
            expiring_soon_count=0,
            issues=["Vault is empty"],
        )

    results = score_vault(vault_path, password)
    avg = sum(r.score for r in results) / len(results) if results else 0.0
    grade = _grade_from_score(avg)

    now = datetime.now(tz=timezone.utc)
    expired = 0
    soon = 0
    expiry_entries = list_expiry(vault_path)
    for key, entry in expiry_entries.items():
        from datetime import datetime as dt
        due = entry.get("expires_at")
        if due is None:
            continue
        due_dt = dt.fromisoformat(due)
        if due_dt.tzinfo is None:
            due_dt = due_dt.replace(tzinfo=timezone.utc)
        delta = (due_dt - now).total_seconds()
        if delta <= 0:
            expired += 1
        elif delta <= warn_days * 86400:
            soon += 1

    issues: List[str] = []
    if expired:
        issues.append(f"{expired} variable(s) have expired")
    if soon:
        issues.append(f"{soon} variable(s) expiring within {warn_days} days")
    low = [r.key for r in results if r.score < 40]
    if low:
        issues.append(f"Weak secrets: {', '.join(low[:3])}{'...' if len(low) > 3 else ''}")

    return BadgeSummary(
        total_vars=total,
        avg_score=round(avg, 1),
        grade=grade,
        expired_count=expired,
        expiring_soon_count=soon,
        issues=issues,
    )


def format_badge_report(summary: BadgeSummary) -> str:
    """Return a human-readable badge report string."""
    lines = [
        f"Vault Badge  [{summary.grade}]",
        f"  Variables : {summary.total_vars}",
        f"  Avg Score : {summary.avg_score}/100",
        f"  Expired   : {summary.expired_count}",
        f"  Exp. Soon : {summary.expiring_soon_count}",
    ]
    if summary.issues:
        lines.append("  Issues:")
        for issue in summary.issues:
            lines.append(f"    - {issue}")
    return "\n".join(lines)
