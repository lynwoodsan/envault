"""Tests for envault.search."""

import pytest

from envault.vault import set_var
from envault.search import search_vars, search_by_value


PASSWORD = "test-pass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    set_var(path, PASSWORD, "DB_HOST", "localhost")
    set_var(path, PASSWORD, "DB_PORT", "5432")
    set_var(path, PASSWORD, "API_KEY", "supersecret")
    set_var(path, PASSWORD, "API_SECRET", "topsecret")
    set_var(path, PASSWORD, "APP_ENV", "production")
    return path


def test_search_exact_prefix(vault_file):
    result = search_vars(vault_file, PASSWORD, "DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_search_wildcard_middle(vault_file):
    result = search_vars(vault_file, PASSWORD, "*SECRET*")
    assert set(result.keys()) == {"API_SECRET"}


def test_search_case_insensitive_default(vault_file):
    result = search_vars(vault_file, PASSWORD, "api_*")
    assert set(result.keys()) == {"API_KEY", "API_SECRET"}


def test_search_case_sensitive_no_match(vault_file):
    result = search_vars(vault_file, PASSWORD, "api_*", case_sensitive=True)
    assert result == {}


def test_search_case_sensitive_match(vault_file):
    result = search_vars(vault_file, PASSWORD, "API_*", case_sensitive=True)
    assert set(result.keys()) == {"API_KEY", "API_SECRET"}


def test_search_no_match(vault_file):
    result = search_vars(vault_file, PASSWORD, "MISSING_*")
    assert result == {}


def test_search_returns_values(vault_file):
    result = search_vars(vault_file, PASSWORD, "DB_HOST")
    assert result["DB_HOST"] == "localhost"


def test_search_by_value_basic(vault_file):
    matches = search_by_value(vault_file, PASSWORD, "secret")
    assert "API_KEY" in matches
    assert "API_SECRET" in matches


def test_search_by_value_case_insensitive(vault_file):
    matches = search_by_value(vault_file, PASSWORD, "SECRET")
    assert "API_KEY" in matches


def test_search_by_value_case_sensitive_no_match(vault_file):
    matches = search_by_value(vault_file, PASSWORD, "SECRET", case_sensitive=True)
    # values are lowercase 'supersecret' / 'topsecret'
    assert matches == []


def test_search_by_value_no_match(vault_file):
    matches = search_by_value(vault_file, PASSWORD, "nonexistent")
    assert matches == []
