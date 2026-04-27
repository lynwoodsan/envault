"""Tests for envault.classification."""

import pytest
from pathlib import Path
from envault.classification import (
    classify_var,
    unclassify_var,
    get_classification,
    list_classifications,
    get_keys_by_level,
    VALID_LEVELS,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "test.vault")


def test_classify_var_returns_entry(vault_file):
    entry = classify_var(vault_file, "DB_PASSWORD", "secret")
    assert entry["level"] == "secret"
    assert entry["note"] is None


def test_classify_var_with_note(vault_file):
    entry = classify_var(vault_file, "API_KEY", "confidential", note="Third-party key")
    assert entry["note"] == "Third-party key"


def test_classify_var_invalid_level_raises(vault_file):
    with pytest.raises(ValueError, match="Invalid level"):
        classify_var(vault_file, "SOME_VAR", "ultra-secret")


def test_get_classification_returns_entry(vault_file):
    classify_var(vault_file, "DB_HOST", "internal")
    entry = get_classification(vault_file, "DB_HOST")
    assert entry is not None
    assert entry["level"] == "internal"


def test_get_classification_missing_returns_none(vault_file):
    assert get_classification(vault_file, "NONEXISTENT") is None


def test_unclassify_removes_entry(vault_file):
    classify_var(vault_file, "TOKEN", "secret")
    result = unclassify_var(vault_file, "TOKEN")
    assert result is True
    assert get_classification(vault_file, "TOKEN") is None


def test_unclassify_nonexistent_returns_false(vault_file):
    assert unclassify_var(vault_file, "GHOST") is False


def test_list_classifications_empty(vault_file):
    assert list_classifications(vault_file) == {}


def test_list_classifications_multiple(vault_file):
    classify_var(vault_file, "A", "public")
    classify_var(vault_file, "B", "secret")
    data = list_classifications(vault_file)
    assert len(data) == 2
    assert data["A"]["level"] == "public"
    assert data["B"]["level"] == "secret"


def test_get_keys_by_level(vault_file):
    classify_var(vault_file, "X", "secret")
    classify_var(vault_file, "Y", "secret")
    classify_var(vault_file, "Z", "public")
    keys = get_keys_by_level(vault_file, "secret")
    assert set(keys) == {"X", "Y"}


def test_get_keys_by_level_invalid_raises(vault_file):
    with pytest.raises(ValueError):
        get_keys_by_level(vault_file, "bogus")


def test_classify_overwrites_existing(vault_file):
    classify_var(vault_file, "KEY", "public")
    classify_var(vault_file, "KEY", "secret", note="Updated")
    entry = get_classification(vault_file, "KEY")
    assert entry["level"] == "secret"
    assert entry["note"] == "Updated"


def test_all_valid_levels_accepted(vault_file):
    for i, level in enumerate(VALID_LEVELS):
        classify_var(vault_file, f"VAR_{i}", level)
        assert get_classification(vault_file, f"VAR_{i}")["level"] == level
