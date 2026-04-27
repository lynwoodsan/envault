"""Tests for envault.visibility module."""

import pytest
from pathlib import Path
from envault.visibility import (
    set_visibility,
    get_visibility,
    remove_visibility,
    list_visibility,
    filter_by_visibility,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "test.vault")


def test_get_visibility_missing_returns_none(vault_file):
    assert get_visibility(vault_file, "MY_KEY") is None


def test_set_and_get_visibility(vault_file):
    level = set_visibility(vault_file, "MY_KEY", "private")
    assert level == "private"
    assert get_visibility(vault_file, "MY_KEY") == "private"


def test_set_visibility_all_levels(vault_file):
    for level in ("public", "private", "secret"):
        set_visibility(vault_file, "KEY", level)
        assert get_visibility(vault_file, "KEY") == level


def test_set_visibility_invalid_level_raises(vault_file):
    with pytest.raises(ValueError, match="Invalid visibility level"):
        set_visibility(vault_file, "KEY", "hidden")


def test_set_visibility_overwrites(vault_file):
    set_visibility(vault_file, "KEY", "public")
    set_visibility(vault_file, "KEY", "secret")
    assert get_visibility(vault_file, "KEY") == "secret"


def test_remove_visibility_returns_true(vault_file):
    set_visibility(vault_file, "KEY", "private")
    assert remove_visibility(vault_file, "KEY") is True
    assert get_visibility(vault_file, "KEY") is None


def test_remove_visibility_nonexistent_returns_false(vault_file):
    assert remove_visibility(vault_file, "GHOST") is False


def test_list_visibility_empty(vault_file):
    assert list_visibility(vault_file) == {}


def test_list_visibility_multiple_keys(vault_file):
    set_visibility(vault_file, "A", "public")
    set_visibility(vault_file, "B", "secret")
    result = list_visibility(vault_file)
    assert result == {"A": "public", "B": "secret"}


def test_filter_by_visibility(vault_file):
    set_visibility(vault_file, "PUB1", "public")
    set_visibility(vault_file, "PUB2", "public")
    set_visibility(vault_file, "SEC1", "secret")
    public_keys = filter_by_visibility(vault_file, "public")
    assert sorted(public_keys) == ["PUB1", "PUB2"]


def test_filter_by_visibility_invalid_level_raises(vault_file):
    with pytest.raises(ValueError, match="Invalid visibility level"):
        filter_by_visibility(vault_file, "invisible")


def test_filter_by_visibility_no_matches(vault_file):
    set_visibility(vault_file, "KEY", "private")
    assert filter_by_visibility(vault_file, "secret") == []


def test_visibility_file_created_alongside_vault(vault_file, tmp_path):
    set_visibility(vault_file, "KEY", "public")
    vis_file = tmp_path / "test.visibility.json"
    assert vis_file.exists()
