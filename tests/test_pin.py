import pytest
from pathlib import Path
from envault.pin import pin_var, unpin_var, is_pinned, list_pins, get_pin_reason


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    vf.write_text("dummy")
    return vf


def test_pin_var_marks_key(vault_file):
    pin_var(vault_file, "SECRET_KEY")
    assert is_pinned(vault_file, "SECRET_KEY")


def test_unpin_var_removes_key(vault_file):
    pin_var(vault_file, "SECRET_KEY")
    result = unpin_var(vault_file, "SECRET_KEY")
    assert result is True
    assert not is_pinned(vault_file, "SECRET_KEY")


def test_unpin_nonexistent_returns_false(vault_file):
    assert unpin_var(vault_file, "MISSING") is False


def test_pin_with_reason(vault_file):
    pin_var(vault_file, "DB_PASSWORD", reason="Do not change in prod")
    assert get_pin_reason(vault_file, "DB_PASSWORD") == "Do not change in prod"


def test_list_pins_empty(vault_file):
    assert list_pins(vault_file) == []


def test_list_pins_multiple(vault_file):
    pin_var(vault_file, "KEY_A", reason="reason a")
    pin_var(vault_file, "KEY_B")
    pins = list_pins(vault_file)
    keys = [p["key"] for p in pins]
    assert "KEY_A" in keys
    assert "KEY_B" in keys


def test_is_pinned_false_for_unknown(vault_file):
    assert not is_pinned(vault_file, "NOPE")


def test_pin_idempotent(vault_file):
    pin_var(vault_file, "X", reason="first")
    pin_var(vault_file, "X", reason="second")
    assert get_pin_reason(vault_file, "X") == "second"
    pins = list_pins(vault_file)
    assert len([p for p in pins if p["key"] == "X"]) == 1
