"""Tests for envault.tags."""
import pytest
from pathlib import Path
from envault.vault import set_var
from envault.tags import add_tag, remove_tag, get_tags, list_by_tag, all_tags

PASSWORD = "test-pass"


@pytest.fixture
def vault_file(tmp_path):
    vf = str(tmp_path / "vault.json")
    set_var(vf, PASSWORD, "DB_HOST", "localhost")
    set_var(vf, PASSWORD, "DB_PORT", "5432")
    set_var(vf, PASSWORD, "API_KEY", "secret")
    return vf


def test_add_tag_and_get(vault_file):
    add_tag(vault_file, PASSWORD, "DB_HOST", "database")
    assert "database" in get_tags(vault_file, PASSWORD, "DB_HOST")


def test_add_tag_idempotent(vault_file):
    add_tag(vault_file, PASSWORD, "DB_HOST", "database")
    add_tag(vault_file, PASSWORD, "DB_HOST", "database")
    assert get_tags(vault_file, PASSWORD, "DB_HOST").count("database") == 1


def test_add_multiple_tags(vault_file):
    add_tag(vault_file, PASSWORD, "DB_HOST", "database")
    add_tag(vault_file, PASSWORD, "DB_HOST", "production")
    tags = get_tags(vault_file, PASSWORD, "DB_HOST")
    assert "database" in tags and "production" in tags


def test_remove_tag(vault_file):
    add_tag(vault_file, PASSWORD, "API_KEY", "secret")
    result = remove_tag(vault_file, PASSWORD, "API_KEY", "secret")
    assert result is True
    assert "secret" not in get_tags(vault_file, PASSWORD, "API_KEY")


def test_remove_nonexistent_tag(vault_file):
    result = remove_tag(vault_file, PASSWORD, "API_KEY", "ghost")
    assert result is False


def test_list_by_tag(vault_file):
    add_tag(vault_file, PASSWORD, "DB_HOST", "database")
    add_tag(vault_file, PASSWORD, "DB_PORT", "database")
    add_tag(vault_file, PASSWORD, "API_KEY", "external")
    keys = list_by_tag(vault_file, PASSWORD, "database")
    assert set(keys) == {"DB_HOST", "DB_PORT"}


def test_list_by_tag_empty(vault_file):
    assert list_by_tag(vault_file, PASSWORD, "nonexistent") == []


def test_all_tags(vault_file):
    add_tag(vault_file, PASSWORD, "DB_HOST", "database")
    add_tag(vault_file, PASSWORD, "API_KEY", "external")
    result = all_tags(vault_file, PASSWORD)
    assert "DB_HOST" in result
    assert "API_KEY" in result


def test_get_tags_unknown_key(vault_file):
    assert get_tags(vault_file, PASSWORD, "UNKNOWN") == []
