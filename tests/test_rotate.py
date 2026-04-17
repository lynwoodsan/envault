"""Tests for envault.rotate (key-rotation feature)."""

import pytest
from pathlib import Path

from envault.vault import set_var, load_vault
from envault.rotate import rotate_password, rotation_preview


OLD_PASS = "old-secret"
NEW_PASS = "new-secret"


@pytest.fixture()
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    set_var(vf, OLD_PASS, "API_KEY", "abc123")
    set_var(vf, OLD_PASS, "DB_URL", "postgres://localhost/db")
    return vf


def test_rotate_returns_variable_count(vault_file):
    count = rotate_password(vault_file, OLD_PASS, NEW_PASS)
    assert count == 2


def test_rotate_new_password_decrypts(vault_file):
    rotate_password(vault_file, OLD_PASS, NEW_PASS)
    data = load_vault(vault_file, NEW_PASS)
    assert data["API_KEY"] == "abc123"
    assert data["DB_URL"] == "postgres://localhost/db"


def test_rotate_old_password_fails_after_rotation(vault_file):
    rotate_password(vault_file, OLD_PASS, NEW_PASS)
    with pytest.raises(Exception):
        load_vault(vault_file, OLD_PASS)


def test_rotate_wrong_old_password_raises(vault_file):
    with pytest.raises(Exception):
        rotate_password(vault_file, "wrong-pass", NEW_PASS)


def test_rotate_empty_vault(tmp_path):
    vf = tmp_path / ".envault"
    count = rotate_password(vf, OLD_PASS, NEW_PASS)
    assert count == 0


def test_rotation_preview_returns_keys(vault_file):
    keys = rotation_preview(vault_file, OLD_PASS)
    assert set(keys) == {"API_KEY", "DB_URL"}


def test_rotation_preview_wrong_password_raises(vault_file):
    with pytest.raises(Exception):
        rotation_preview(vault_file, "bad-pass")


def test_rotate_writes_audit_log(vault_file):
    from envault.audit import get_events
    rotate_password(vault_file, OLD_PASS, NEW_PASS, actor="alice")
    events = get_events(vault_file)
    assert any(e["action"] == "rotate" and e["actor"] == "alice" for e in events)
