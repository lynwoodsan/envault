"""Additional edge-case tests for classification level logic."""

import pytest
from envault.classification import (
    classify_var,
    get_keys_by_level,
    list_classifications,
    unclassify_var,
    VALID_LEVELS,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "edge.vault")


def test_valid_levels_tuple_contains_four():
    assert len(VALID_LEVELS) == 4


def test_valid_levels_ordered_by_sensitivity():
    assert VALID_LEVELS == ("public", "internal", "confidential", "secret")


def test_get_keys_by_level_empty_vault(vault_file):
    assert get_keys_by_level(vault_file, "secret") == []


def test_classify_and_unclassify_leaves_empty(vault_file):
    classify_var(vault_file, "TEMP", "public")
    unclassify_var(vault_file, "TEMP")
    assert list_classifications(vault_file) == {}


def test_multiple_keys_same_level(vault_file):
    for i in range(5):
        classify_var(vault_file, f"KEY_{i}", "confidential")
    keys = get_keys_by_level(vault_file, "confidential")
    assert len(keys) == 5


def test_level_change_reflected_in_get_keys(vault_file):
    classify_var(vault_file, "MUTABLE", "public")
    classify_var(vault_file, "MUTABLE", "secret")
    assert "MUTABLE" in get_keys_by_level(vault_file, "secret")
    assert "MUTABLE" not in get_keys_by_level(vault_file, "public")


def test_note_preserved_across_reload(vault_file):
    classify_var(vault_file, "NOTED", "internal", note="keep this")
    from envault.classification import get_classification
    entry = get_classification(vault_file, "NOTED")
    assert entry["note"] == "keep this"


def test_classification_file_is_separate_from_vault(tmp_path):
    vault = str(tmp_path / "my.vault")
    classify_var(vault, "K", "secret")
    cls_file = tmp_path / "my.classifications.json"
    assert cls_file.exists()
