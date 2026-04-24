"""Tests for envault.dependency module."""

import pytest
from pathlib import Path

from envault.dependency import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    resolve_order,
)


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / "vault.enc"
    vf.write_text("placeholder")
    return vf


def test_add_and_get_dependency(vault_file):
    add_dependency(vault_file, "DATABASE_URL", "DB_HOST")
    deps = get_dependencies(vault_file, "DATABASE_URL")
    assert "DB_HOST" in deps


def test_add_dependency_idempotent(vault_file):
    add_dependency(vault_file, "DATABASE_URL", "DB_HOST")
    add_dependency(vault_file, "DATABASE_URL", "DB_HOST")
    assert get_dependencies(vault_file, "DATABASE_URL").count("DB_HOST") == 1


def test_add_multiple_dependencies(vault_file):
    add_dependency(vault_file, "DATABASE_URL", "DB_HOST")
    add_dependency(vault_file, "DATABASE_URL", "DB_PORT")
    deps = get_dependencies(vault_file, "DATABASE_URL")
    assert "DB_HOST" in deps
    assert "DB_PORT" in deps


def test_remove_dependency_returns_true(vault_file):
    add_dependency(vault_file, "DATABASE_URL", "DB_HOST")
    result = remove_dependency(vault_file, "DATABASE_URL", "DB_HOST")
    assert result is True
    assert get_dependencies(vault_file, "DATABASE_URL") == []


def test_remove_nonexistent_dependency_returns_false(vault_file):
    result = remove_dependency(vault_file, "DATABASE_URL", "DB_HOST")
    assert result is False


def test_get_dependencies_missing_key(vault_file):
    assert get_dependencies(vault_file, "NONEXISTENT") == []


def test_get_dependents(vault_file):
    add_dependency(vault_file, "DATABASE_URL", "DB_HOST")
    add_dependency(vault_file, "REPLICA_URL", "DB_HOST")
    dependents = get_dependents(vault_file, "DB_HOST")
    assert "DATABASE_URL" in dependents
    assert "REPLICA_URL" in dependents


def test_get_dependents_none(vault_file):
    assert get_dependents(vault_file, "ORPHAN_KEY") == []


def test_resolve_order_respects_deps(vault_file):
    add_dependency(vault_file, "C", "B")
    add_dependency(vault_file, "B", "A")
    order = resolve_order(vault_file)
    assert order.index("A") < order.index("B")
    assert order.index("B") < order.index("C")


def test_resolve_order_circular_raises(vault_file):
    add_dependency(vault_file, "A", "B")
    add_dependency(vault_file, "B", "A")
    with pytest.raises(ValueError, match="Circular dependency"):
        resolve_order(vault_file)


def test_resolve_order_subset(vault_file):
    add_dependency(vault_file, "C", "B")
    add_dependency(vault_file, "B", "A")
    order = resolve_order(vault_file, keys=["B", "A"])
    assert "C" not in order
    assert order.index("A") < order.index("B")
