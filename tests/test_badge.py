"""Tests for envault.badge."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.vault import set_var
from envault.expiry import set_expiry
from envault.badge import (
    BadgeSummary,
    generate_badge,
    format_badge_report,
    _grade_from_score,
)

PASSWORD = "badge-test-pw"


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    set_var(vf, PASSWORD, "API_KEY", "s3cr3t-V@lue-X9!zQ")
    set_var(vf, PASSWORD, "DB_PASS", "Str0ng#Pass!99")
    return vf


def test_generate_badge_returns_summary(vault_file):
    summary = generate_badge(vault_file, PASSWORD)
    assert isinstance(summary, BadgeSummary)


def test_total_vars_correct(vault_file):
    summary = generate_badge(vault_file, PASSWORD)
    assert summary.total_vars == 2


def test_avg_score_in_range(vault_file):
    summary = generate_badge(vault_file, PASSWORD)
    assert 0.0 <= summary.avg_score <= 100.0


def test_grade_assigned(vault_file):
    summary = generate_badge(vault_file, PASSWORD)
    assert summary.grade in ("A", "B", "C", "D", "F")


def test_empty_vault_returns_f_grade(tmp_path):
    from envault.vault import save_vault
    vf = tmp_path / ".envault"
    save_vault(vf, PASSWORD, {})
    summary = generate_badge(vf, PASSWORD)
    assert summary.grade == "F"
    assert summary.total_vars == 0
    assert any("empty" in i.lower() for i in summary.issues)


def test_expired_var_counted(vault_file):
    set_expiry(vault_file, "API_KEY", days=-1)  # already expired
    summary = generate_badge(vault_file, PASSWORD)
    assert summary.expired_count >= 1
    assert any("expired" in i.lower() for i in summary.issues)


def test_expiring_soon_counted(vault_file):
    set_expiry(vault_file, "DB_PASS", days=3)
    summary = generate_badge(vault_file, PASSWORD, warn_days=7)
    assert summary.expiring_soon_count >= 1


def test_grade_from_score_boundaries():
    assert _grade_from_score(100) == "A"
    assert _grade_from_score(90) == "A"
    assert _grade_from_score(89) == "B"
    assert _grade_from_score(75) == "B"
    assert _grade_from_score(74) == "C"
    assert _grade_from_score(55) == "C"
    assert _grade_from_score(54) == "D"
    assert _grade_from_score(35) == "D"
    assert _grade_from_score(34) == "F"
    assert _grade_from_score(0) == "F"


def test_format_badge_report_contains_grade(vault_file):
    summary = generate_badge(vault_file, PASSWORD)
    report = format_badge_report(summary)
    assert summary.grade in report
    assert "Variables" in report
    assert "Avg Score" in report


def test_format_badge_report_lists_issues(vault_file):
    set_expiry(vault_file, "API_KEY", days=-1)
    summary = generate_badge(vault_file, PASSWORD)
    report = format_badge_report(summary)
    assert "Issues" in report
