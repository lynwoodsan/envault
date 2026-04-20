"""Tests for envault/access.py"""

import pytest
from pathlib import Path
from envault.access import (
    set_access,
    remove_access,
    get_access,
    list_access,
    actors_with_access,
    ACCESS_READ,
    ACCESS_WRITE,
    ACCESS_NONE,
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / ".envault"


def test_set_and_get_access(vault_file):
    set_access(vault_file, "DB_PASSWORD", "alice", ACCESS_READ)
    assert get_access(vault_file, "DB_PASSWORD", "alice") == ACCESS_READ


def test_get_access_missing_returns_none(vault_file):
    assert get_access(vault_file, "MISSING_KEY", "bob") is None


def test_set_access_overwrite(vault_file):
    set_access(vault_file, "API_KEY", "alice", ACCESS_READ)
    set_access(vault_file, "API_KEY", "alice", ACCESS_WRITE)
    assert get_access(vault_file, "API_KEY", "alice") == ACCESS_WRITE


def test_set_access_invalid_level_raises(vault_file):
    with pytest.raises(ValueError, match="Invalid access level"):
        set_access(vault_file, "API_KEY", "alice", "superadmin")


def test_remove_access_returns_true(vault_file):
    set_access(vault_file, "SECRET", "bob", ACCESS_WRITE)
    result = remove_access(vault_file, "SECRET", "bob")
    assert result is True
    assert get_access(vault_file, "SECRET", "bob") is None


def test_remove_access_nonexistent_returns_false(vault_file):
    result = remove_access(vault_file, "MISSING", "ghost")
    assert result is False


def test_remove_access_cleans_empty_key(vault_file):
    set_access(vault_file, "TOKEN", "alice", ACCESS_READ)
    remove_access(vault_file, "TOKEN", "alice")
    data = list_access(vault_file)
    assert "TOKEN" not in data


def test_list_access_all(vault_file):
    set_access(vault_file, "KEY1", "alice", ACCESS_READ)
    set_access(vault_file, "KEY2", "bob", ACCESS_WRITE)
    data = list_access(vault_file)
    assert "KEY1" in data
    assert "KEY2" in data


def test_list_access_filtered_by_key(vault_file):
    set_access(vault_file, "KEY1", "alice", ACCESS_READ)
    set_access(vault_file, "KEY2", "bob", ACCESS_WRITE)
    data = list_access(vault_file, key="KEY1")
    assert "KEY1" in data
    assert "KEY2" not in data


def test_actors_with_access_read_includes_write(vault_file):
    set_access(vault_file, "DB_URL", "alice", ACCESS_READ)
    set_access(vault_file, "DB_URL", "bob", ACCESS_WRITE)
    actors = actors_with_access(vault_file, "DB_URL", ACCESS_READ)
    assert "alice" in actors
    assert "bob" in actors


def test_actors_with_access_write_excludes_read(vault_file):
    set_access(vault_file, "DB_URL", "alice", ACCESS_READ)
    set_access(vault_file, "DB_URL", "bob", ACCESS_WRITE)
    actors = actors_with_access(vault_file, "DB_URL", ACCESS_WRITE)
    assert "alice" not in actors
    assert "bob" in actors


def test_actors_with_access_empty_key(vault_file):
    actors = actors_with_access(vault_file, "NONEXISTENT", ACCESS_READ)
    assert actors == []
