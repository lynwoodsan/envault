import pytest
from envault.compare import compare_dicts, compare_vaults, compare_vault_dotenv, format_compare_report, CompareResult
from envault.vault import save_vault
import tempfile, os


def make_vault(tmp_path, name, data, password="pass"):
    p = str(tmp_path / name)
    save_vault(p, data, password)
    return p


def test_compare_dicts_match():
    results = compare_dicts({"A": "1"}, {"A": "1"})
    assert results[0].status == "match"


def test_compare_dicts_mismatch():
    results = compare_dicts({"A": "1"}, {"A": "2"})
    assert results[0].status == "mismatch"
    assert results[0].left == "1"
    assert results[0].right == "2"


def test_compare_dicts_only_left():
    results = compare_dicts({"A": "1"}, {})
    assert results[0].status == "only_left"


def test_compare_dicts_only_right():
    results = compare_dicts({}, {"B": "2"})
    assert results[0].status == "only_right"


def test_compare_dicts_sorted_keys():
    results = compare_dicts({"Z": "1", "A": "2"}, {"Z": "1", "A": "2"})
    assert results[0].key == "A"
    assert results[1].key == "Z"


def test_compare_dicts_empty():
    """Comparing two empty dicts should return an empty result list."""
    results = compare_dicts({}, {})
    assert results == []


def test_compare_vaults(tmp_path):
    a = make_vault(tmp_path, "a.vault", {"X": "hello", "Y": "world"})
    b = make_vault(tmp_path, "b.vault", {"X": "hello", "Y": "changed"})
    results = compare_vaults(a, "pass", b, "pass")
    statuses = {r.key: r.status for r in results}
    assert statuses["X"] == "match"
    assert statuses["Y"] == "mismatch"


def test_compare_vault_dotenv(tmp_path):
    vault = make_vault(tmp_path, "v.vault", {"FOO": "bar"})
    dotenv = str(tmp_path / ".env")
    with open(dotenv, "w") as f:
        f.write("FOO=bar\nBAZ=extra\n")
    results = compare_vault_dotenv(vault, "pass", dotenv)
    statuses = {r.key: r.status for r in results}
    assert statuses["FOO"] == "match"
    assert statuses["BAZ"] == "only_right"


def test_compare_vault_dotenv_only_left(tmp_path):
    """Keys present in vault but missing from dotenv should appear as only_left."""
    vault = make_vault(tmp_path, "v.vault", {"SECRET": "value"})
    dotenv = str(tmp_path / ".env")
    with open(dotenv, "w") as f:
        f.write("OTHER=something\n")
    results = compare_vault_dotenv(vault, "pass", dotenv)
    statuses = {r.key: r.status for r in results}
    assert statuses["SECRET"] == "only_left"


def test_format_compare_report_contains_summary():
    results = [CompareResult("A", "match", "1", "1"), CompareResult("B", "only_left", "2")]
    report = format_compare_report(results)
    assert "Summary" in report
    assert "1 match" in report


def test_format_compare_report_show_values():
    results = [CompareResult("KEY", "mismatch", "old", "new")]
    report = format_compare_report(results, show_values=True)
    assert "old" in report
    assert "new" in report
