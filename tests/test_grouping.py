"""Tests for envault.grouping module."""

import pytest
from pathlib import Path

from envault.grouping import (
    add_to_group,
    remove_from_group,
    get_group,
    list_groups,
    get_groups_for_key,
    delete_group,
)


@pytest.fixture
def vault_file(tmp_path: Path) -> str:
    vf = tmp_path / "vault.enc"
    vf.write_text("placeholder")
    return str(vf)


def test_add_to_group_returns_members(vault_file):
    members = add_to_group(vault_file, "infra", "DB_HOST")
    assert "DB_HOST" in members


def test_add_to_group_idempotent(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    members = add_to_group(vault_file, "infra", "DB_HOST")
    assert members.count("DB_HOST") == 1


def test_add_multiple_keys_to_group(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    add_to_group(vault_file, "infra", "DB_PORT")
    members = get_group(vault_file, "infra")
    assert "DB_HOST" in members
    assert "DB_PORT" in members


def test_get_group_missing_returns_empty(vault_file):
    result = get_group(vault_file, "nonexistent")
    assert result == []


def test_remove_from_group_returns_true(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    removed = remove_from_group(vault_file, "infra", "DB_HOST")
    assert removed is True


def test_remove_from_group_key_gone(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    remove_from_group(vault_file, "infra", "DB_HOST")
    assert get_group(vault_file, "infra") == []


def test_remove_nonexistent_key_returns_false(vault_file):
    result = remove_from_group(vault_file, "infra", "MISSING")
    assert result is False


def test_remove_last_key_deletes_group(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    remove_from_group(vault_file, "infra", "DB_HOST")
    assert "infra" not in list_groups(vault_file)


def test_list_groups_returns_all(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    add_to_group(vault_file, "auth", "SECRET_KEY")
    groups = list_groups(vault_file)
    assert "infra" in groups
    assert "auth" in groups


def test_get_groups_for_key(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    add_to_group(vault_file, "all", "DB_HOST")
    groups = get_groups_for_key(vault_file, "DB_HOST")
    assert "infra" in groups
    assert "all" in groups


def test_get_groups_for_key_not_member(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    groups = get_groups_for_key(vault_file, "OTHER_KEY")
    assert groups == []


def test_delete_group_returns_true(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    result = delete_group(vault_file, "infra")
    assert result is True


def test_delete_group_removes_entries(vault_file):
    add_to_group(vault_file, "infra", "DB_HOST")
    delete_group(vault_file, "infra")
    assert get_group(vault_file, "infra") == []


def test_delete_nonexistent_group_returns_false(vault_file):
    result = delete_group(vault_file, "ghost")
    assert result is False
