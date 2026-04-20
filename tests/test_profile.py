import pytest
from pathlib import Path
from envault.profile import (
    create_profile, delete_profile, assign_key,
    unassign_key, get_profile_keys, list_profiles
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / ".envault")


def test_create_profile(vault_file):
    create_profile(vault_file, "dev")
    assert "dev" in list_profiles(vault_file)


def test_create_profile_idempotent(vault_file):
    create_profile(vault_file, "dev")
    create_profile(vault_file, "dev")
    assert list_profiles(vault_file)["dev"] == []


def test_delete_profile(vault_file):
    create_profile(vault_file, "dev")
    result = delete_profile(vault_file, "dev")
    assert result is True
    assert "dev" not in list_profiles(vault_file)


def test_delete_nonexistent_profile(vault_file):
    assert delete_profile(vault_file, "ghost") is False


def test_assign_key(vault_file):
    create_profile(vault_file, "prod")
    assign_key(vault_file, "prod", "API_KEY")
    assert "API_KEY" in get_profile_keys(vault_file, "prod")


def test_assign_key_idempotent(vault_file):
    assign_key(vault_file, "prod", "API_KEY")
    assign_key(vault_file, "prod", "API_KEY")
    assert get_profile_keys(vault_file, "prod").count("API_KEY") == 1


def test_unassign_key(vault_file):
    assign_key(vault_file, "dev", "SECRET")
    result = unassign_key(vault_file, "dev", "SECRET")
    assert result is True
    assert "SECRET" not in get_profile_keys(vault_file, "dev")


def test_unassign_missing_key(vault_file):
    create_profile(vault_file, "dev")
    assert unassign_key(vault_file, "dev", "NOPE") is False


def test_get_profile_keys_missing_profile(vault_file):
    assert get_profile_keys(vault_file, "missing") is None


def test_list_profiles_empty(vault_file):
    assert list_profiles(vault_file) == {}


def test_list_profiles_multiple(vault_file):
    create_profile(vault_file, "dev")
    create_profile(vault_file, "prod")
    profiles = list_profiles(vault_file)
    assert "dev" in profiles and "prod" in profiles
