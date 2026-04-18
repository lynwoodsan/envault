"""Tests for envault/diff.py"""
import json
import os
import pytest

from envault.vault import save_vault
from envault.diff import diff_vaults, diff_vault_dotenv, format_diff


@pytest.fixture
def vault_a(tmp_path):
    path = str(tmp_path / "a.vault")
    save_vault(path, "passA", {"FOO": "foo", "BAR": "bar", "SHARED": "same"})
    return path


@pytest.fixture
def vault_b(tmp_path):
    path = str(tmp_path / "b.vault")
    save_vault(path, "passB", {"BAR": "baz", "SHARED": "same", "NEW": "new"})
    return path


def test_diff_vaults_added(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    added = [e for e in entries if e.status == "added"]
    assert len(added) == 1
    assert added[0].key == "NEW"


def test_diff_vaults_removed(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    removed = [e for e in entries if e.status == "removed"]
    assert len(removed) == 1
    assert removed[0].key == "FOO"


def test_diff_vaults_changed(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    changed = [e for e in entries if e.status == "changed"]
    assert len(changed) == 1
    assert changed[0].key == "BAR"
    assert changed[0].old_value == "bar"
    assert changed[0].new_value == "baz"


def test_diff_vaults_unchanged(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert len(unchanged) == 1
    assert unchanged[0].key == "SHARED"


def test_diff_vault_dotenv(vault_a, tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text("FOO=foo\nBAR=different\nEXTRA=extra\n")
    entries = diff_vault_dotenv(str(vault_a), "passA", str(dotenv))
    statuses = {e.key: e.status for e in entries}
    assert statuses["FOO"] == "unchanged"
    assert statuses["BAR"] == "changed"
    assert statuses["EXTRA"] == "added"
    assert statuses["SHARED"] == "removed"


def test_format_diff_symbols(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    output = format_diff(entries)
    assert "+ NEW" in output
    assert "- FOO" in output
    assert "~ BAR" in output
    assert "  SHARED" in output


def test_format_diff_show_values(vault_a, vault_b):
    entries = diff_vaults(vault_a, "passA", vault_b, "passB")
    output = format_diff(entries, show_values=True)
    assert "'bar'" in output
    assert "'baz'" in output
