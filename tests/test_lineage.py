"""Tests for envault.lineage."""

import pytest

from envault.lineage import (
    LineageEntry,
    get_derived_keys,
    get_lineage,
    list_lineage,
    remove_lineage,
    set_lineage,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def test_set_lineage_returns_entry(vault_file):
    entry = set_lineage(vault_file, "DB_URL", source="infra-team", origin_type="external")
    assert isinstance(entry, LineageEntry)
    assert entry.key == "DB_URL"
    assert entry.source == "infra-team"
    assert entry.origin_type == "external"


def test_get_lineage_returns_entry(vault_file):
    set_lineage(vault_file, "API_KEY", source="ci-pipeline", origin_type="import")
    result = get_lineage(vault_file, "API_KEY")
    assert result is not None
    assert result.source == "ci-pipeline"
    assert result.origin_type == "import"


def test_get_lineage_missing_returns_none(vault_file):
    assert get_lineage(vault_file, "MISSING") is None


def test_set_lineage_invalid_origin_type_raises(vault_file):
    with pytest.raises(ValueError, match="origin_type"):
        set_lineage(vault_file, "X", source="s", origin_type="unknown")


def test_set_lineage_with_derived_from(vault_file):
    entry = set_lineage(
        vault_file, "DERIVED_KEY", source="script",
        origin_type="derived", derived_from=["BASE_KEY", "OTHER_KEY"]
    )
    assert "BASE_KEY" in entry.derived_from
    assert "OTHER_KEY" in entry.derived_from


def test_set_lineage_with_note(vault_file):
    entry = set_lineage(vault_file, "TOKEN", source="vault", origin_type="manual", note="rotated weekly")
    assert entry.note == "rotated weekly"


def test_set_lineage_overwrites_existing(vault_file):
    set_lineage(vault_file, "KEY", source="old-source", origin_type="manual")
    set_lineage(vault_file, "KEY", source="new-source", origin_type="external")
    result = get_lineage(vault_file, "KEY")
    assert result.source == "new-source"
    assert result.origin_type == "external"


def test_remove_lineage_returns_true(vault_file):
    set_lineage(vault_file, "K", source="s", origin_type="manual")
    assert remove_lineage(vault_file, "K") is True
    assert get_lineage(vault_file, "K") is None


def test_remove_lineage_missing_returns_false(vault_file):
    assert remove_lineage(vault_file, "NOPE") is False


def test_list_lineage_empty(vault_file):
    assert list_lineage(vault_file) == []


def test_list_lineage_returns_all(vault_file):
    set_lineage(vault_file, "A", source="s1", origin_type="manual")
    set_lineage(vault_file, "B", source="s2", origin_type="import")
    entries = list_lineage(vault_file)
    assert len(entries) == 2
    keys = {e.key for e in entries}
    assert keys == {"A", "B"}


def test_get_derived_keys(vault_file):
    set_lineage(vault_file, "CHILD", source="x", origin_type="derived", derived_from=["PARENT"])
    set_lineage(vault_file, "OTHER", source="y", origin_type="manual")
    derived = get_derived_keys(vault_file, "PARENT")
    assert "CHILD" in derived
    assert "OTHER" not in derived


def test_recorded_at_is_set(vault_file):
    entry = set_lineage(vault_file, "Z", source="auto", origin_type="external")
    assert entry.recorded_at is not None
    assert "T" in entry.recorded_at  # ISO format
