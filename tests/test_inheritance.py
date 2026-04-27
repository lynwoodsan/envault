"""Tests for envault.inheritance module."""

import pytest
from pathlib import Path

from envault.inheritance import (
    add_parent,
    remove_parent,
    list_parents,
    add_override,
    remove_override,
    get_overrides,
    resolve_vars,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_list_parents_empty(vault_dir):
    assert list_parents(vault_dir) == []


def test_add_parent_and_list(vault_dir):
    add_parent(vault_dir, "/shared/vault")
    assert "/shared/vault" in list_parents(vault_dir)


def test_add_parent_idempotent(vault_dir):
    add_parent(vault_dir, "/shared/vault")
    add_parent(vault_dir, "/shared/vault")
    assert list_parents(vault_dir).count("/shared/vault") == 1


def test_add_multiple_parents_ordered(vault_dir):
    add_parent(vault_dir, "/base")
    add_parent(vault_dir, "/overlay")
    parents = list_parents(vault_dir)
    assert parents == ["/base", "/overlay"]


def test_remove_parent_returns_true(vault_dir):
    add_parent(vault_dir, "/base")
    result = remove_parent(vault_dir, "/base")
    assert result is True
    assert "/base" not in list_parents(vault_dir)


def test_remove_parent_missing_returns_false(vault_dir):
    result = remove_parent(vault_dir, "/nonexistent")
    assert result is False


def test_add_override_and_get(vault_dir):
    add_override(vault_dir, "DB_URL")
    assert "DB_URL" in get_overrides(vault_dir)


def test_add_override_idempotent(vault_dir):
    add_override(vault_dir, "DB_URL")
    add_override(vault_dir, "DB_URL")
    assert get_overrides(vault_dir).count("DB_URL") == 1


def test_remove_override_returns_true(vault_dir):
    add_override(vault_dir, "API_KEY")
    assert remove_override(vault_dir, "API_KEY") is True
    assert "API_KEY" not in get_overrides(vault_dir)


def test_remove_override_missing_returns_false(vault_dir):
    assert remove_override(vault_dir, "MISSING") is False


def test_resolve_vars_parent_fills_missing(vault_dir):
    local = {"LOCAL_KEY": "local"}
    parent = {"PARENT_KEY": "parent", "LOCAL_KEY": "should_be_overridden"}
    merged = resolve_vars(local, parent)
    assert merged["LOCAL_KEY"] == "local"
    assert merged["PARENT_KEY"] == "parent"


def test_resolve_vars_override_blocks_parent(vault_dir):
    local = {}
    parent = {"SECRET": "from_parent"}
    merged = resolve_vars(local, parent, overrides=["SECRET"])
    assert "SECRET" not in merged


def test_resolve_vars_no_parent(vault_dir):
    local = {"A": "1"}
    merged = resolve_vars(local, {})
    assert merged == {"A": "1"}
