"""Tests for envault/namespace.py"""

import pytest
from pathlib import Path
from envault.namespace import (
    assign_namespace,
    unassign_namespace,
    get_namespace_keys,
    get_key_namespaces,
    list_namespaces,
    delete_namespace,
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / ".envault"


def test_assign_and_get_keys(vault_file):
    assign_namespace(vault_file, "DB_HOST", "database")
    assign_namespace(vault_file, "DB_PORT", "database")
    keys = get_namespace_keys(vault_file, "database")
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_assign_idempotent(vault_file):
    assign_namespace(vault_file, "DB_HOST", "database")
    assign_namespace(vault_file, "DB_HOST", "database")
    keys = get_namespace_keys(vault_file, "database")
    assert keys.count("DB_HOST") == 1


def test_get_keys_missing_namespace(vault_file):
    result = get_namespace_keys(vault_file, "nonexistent")
    assert result == []


def test_unassign_removes_key(vault_file):
    assign_namespace(vault_file, "API_KEY", "external")
    removed = unassign_namespace(vault_file, "API_KEY", "external")
    assert removed is True
    assert get_namespace_keys(vault_file, "external") == []


def test_unassign_removes_empty_namespace(vault_file):
    assign_namespace(vault_file, "SOLO", "lone")
    unassign_namespace(vault_file, "SOLO", "lone")
    assert "lone" not in list_namespaces(vault_file)


def test_unassign_nonexistent_returns_false(vault_file):
    result = unassign_namespace(vault_file, "GHOST", "nowhere")
    assert result is False


def test_get_key_namespaces(vault_file):
    assign_namespace(vault_file, "SHARED", "alpha")
    assign_namespace(vault_file, "SHARED", "beta")
    ns = get_key_namespaces(vault_file, "SHARED")
    assert "alpha" in ns
    assert "beta" in ns


def test_get_key_namespaces_none(vault_file):
    result = get_key_namespaces(vault_file, "ORPHAN")
    assert result == []


def test_list_namespaces_sorted(vault_file):
    assign_namespace(vault_file, "Z", "zebra")
    assign_namespace(vault_file, "A", "apple")
    assign_namespace(vault_file, "M", "mango")
    ns = list_namespaces(vault_file)
    assert ns == ["apple", "mango", "zebra"]


def test_delete_namespace(vault_file):
    assign_namespace(vault_file, "DB_HOST", "database")
    result = delete_namespace(vault_file, "database")
    assert result is True
    assert "database" not in list_namespaces(vault_file)


def test_delete_nonexistent_namespace(vault_file):
    result = delete_namespace(vault_file, "ghost")
    assert result is False
