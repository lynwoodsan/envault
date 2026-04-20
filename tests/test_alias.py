import pytest
from pathlib import Path
from envault.alias import add_alias, remove_alias, resolve_alias, list_aliases, reverse_lookup


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.env"


def test_add_and_resolve(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    assert resolve_alias(vault_file, "db") == "DATABASE_URL"


def test_resolve_missing_returns_none(vault_file):
    assert resolve_alias(vault_file, "nope") is None


def test_add_idempotent(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    add_alias(vault_file, "db", "DATABASE_URL")
    assert len(list_aliases(vault_file)) == 1


def test_overwrite_alias(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    add_alias(vault_file, "db", "OTHER_URL")
    assert resolve_alias(vault_file, "db") == "OTHER_URL"


def test_remove_alias(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    result = remove_alias(vault_file, "db")
    assert result is True
    assert resolve_alias(vault_file, "db") is None


def test_remove_nonexistent(vault_file):
    assert remove_alias(vault_file, "ghost") is False


def test_list_aliases(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    add_alias(vault_file, "redis", "REDIS_URL")
    aliases = list_aliases(vault_file)
    assert aliases == {"db": "DATABASE_URL", "redis": "REDIS_URL"}


def test_reverse_lookup(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    add_alias(vault_file, "database", "DATABASE_URL")
    add_alias(vault_file, "redis", "REDIS_URL")
    found = reverse_lookup(vault_file, "DATABASE_URL")
    assert set(found) == {"db", "database"}


def test_reverse_lookup_no_match(vault_file):
    assert reverse_lookup(vault_file, "MISSING") == []
