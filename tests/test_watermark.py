"""Tests for envault.watermark module."""

import pytest
from pathlib import Path
from envault.watermark import (
    create_watermark,
    list_watermarks,
    get_watermark,
    remove_watermark,
    format_watermark,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_create_watermark_returns_entry(vault_dir):
    entry = create_watermark(vault_dir, actor="alice")
    assert entry["actor"] == "alice"
    assert "token" in entry
    assert "timestamp" in entry
    assert "hostname" in entry


def test_create_watermark_with_note(vault_dir):
    entry = create_watermark(vault_dir, actor="bob", note="staging export")
    assert entry["note"] == "staging export"


def test_create_watermark_persists(vault_dir):
    entry = create_watermark(vault_dir, actor="carol")
    token = entry["token"]
    found = get_watermark(vault_dir, token)
    assert found is not None
    assert found["actor"] == "carol"


def test_list_watermarks_empty(vault_dir):
    result = list_watermarks(vault_dir)
    assert result == []


def test_list_watermarks_multiple(vault_dir):
    create_watermark(vault_dir, actor="alice")
    create_watermark(vault_dir, actor="bob")
    entries = list_watermarks(vault_dir)
    assert len(entries) == 2
    actors = {e["actor"] for e in entries}
    assert actors == {"alice", "bob"}


def test_list_watermarks_sorted_descending(vault_dir):
    create_watermark(vault_dir, actor="first")
    create_watermark(vault_dir, actor="second")
    entries = list_watermarks(vault_dir)
    # Most recent should appear first
    assert entries[0]["timestamp"] >= entries[1]["timestamp"]


def test_get_watermark_missing_returns_none(vault_dir):
    result = get_watermark(vault_dir, "nonexistent")
    assert result is None


def test_remove_watermark_returns_true(vault_dir):
    entry = create_watermark(vault_dir, actor="dave")
    token = entry["token"]
    assert remove_watermark(vault_dir, token) is True
    assert get_watermark(vault_dir, token) is None


def test_remove_watermark_nonexistent_returns_false(vault_dir):
    assert remove_watermark(vault_dir, "ghost") is False


def test_format_watermark_contains_fields(vault_dir):
    entry = create_watermark(vault_dir, actor="eve", note="prod release")
    output = format_watermark(entry)
    assert "eve" in output
    assert entry["token"] in output
    assert "prod release" in output


def test_format_watermark_no_note(vault_dir):
    entry = create_watermark(vault_dir, actor="frank")
    output = format_watermark(entry)
    assert "Note" not in output
