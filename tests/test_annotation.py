"""Tests for envault.annotation module."""

import pytest
from pathlib import Path
from envault.annotation import (
    set_annotation,
    get_annotation,
    remove_annotation,
    list_annotations,
    clear_annotations,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    vf.write_text("{}")  # minimal placeholder
    return str(vf)


def test_set_annotation_returns_entry(vault_file):
    entry = set_annotation(vault_file, "DB_HOST", "Primary database host")
    assert entry["note"] == "Primary database host"
    assert entry["author"] == "envault"
    assert "updated_at" in entry


def test_get_annotation_returns_note(vault_file):
    set_annotation(vault_file, "API_KEY", "Third-party API key", author="alice")
    result = get_annotation(vault_file, "API_KEY")
    assert result is not None
    assert result["note"] == "Third-party API key"
    assert result["author"] == "alice"


def test_get_annotation_missing_returns_none(vault_file):
    assert get_annotation(vault_file, "NONEXISTENT") is None


def test_set_annotation_overwrites(vault_file):
    set_annotation(vault_file, "DB_HOST", "old note")
    set_annotation(vault_file, "DB_HOST", "new note")
    result = get_annotation(vault_file, "DB_HOST")
    assert result["note"] == "new note"


def test_remove_annotation_returns_true(vault_file):
    set_annotation(vault_file, "SECRET", "some note")
    assert remove_annotation(vault_file, "SECRET") is True
    assert get_annotation(vault_file, "SECRET") is None


def test_remove_annotation_nonexistent_returns_false(vault_file):
    assert remove_annotation(vault_file, "GHOST") is False


def test_list_annotations_returns_all(vault_file):
    set_annotation(vault_file, "A", "note A")
    set_annotation(vault_file, "B", "note B")
    result = list_annotations(vault_file)
    assert "A" in result
    assert "B" in result
    assert len(result) == 2


def test_list_annotations_empty(vault_file):
    assert list_annotations(vault_file) == {}


def test_clear_annotations_returns_count(vault_file):
    set_annotation(vault_file, "X", "x")
    set_annotation(vault_file, "Y", "y")
    count = clear_annotations(vault_file)
    assert count == 2
    assert list_annotations(vault_file) == {}


def test_annotations_persist_across_calls(vault_file):
    set_annotation(vault_file, "PERSIST", "stays here")
    # Re-read from disk
    result = get_annotation(vault_file, "PERSIST")
    assert result["note"] == "stays here"
