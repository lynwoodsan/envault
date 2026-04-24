"""Tests for envault/masking.py"""

import pytest
from pathlib import Path

from envault.masking import (
    mask_var,
    unmask_var,
    is_masked,
    get_masked_keys,
    apply_masks,
    get_mask_reason,
    MASK_PLACEHOLDER,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    vf.write_text("{}")
    return vf


def test_mask_var_marks_key(vault_file):
    mask_var(vault_file, "SECRET_KEY")
    assert is_masked(vault_file, "SECRET_KEY")


def test_unmask_var_removes_key(vault_file):
    mask_var(vault_file, "SECRET_KEY")
    result = unmask_var(vault_file, "SECRET_KEY")
    assert result is True
    assert not is_masked(vault_file, "SECRET_KEY")


def test_unmask_nonexistent_returns_false(vault_file):
    result = unmask_var(vault_file, "NONEXISTENT")
    assert result is False


def test_mask_with_reason(vault_file):
    mask_var(vault_file, "DB_PASSWORD", reason="contains PII")
    reason = get_mask_reason(vault_file, "DB_PASSWORD")
    assert reason == "contains PII"


def test_mask_without_reason_returns_none(vault_file):
    mask_var(vault_file, "API_KEY")
    reason = get_mask_reason(vault_file, "API_KEY")
    assert reason is None


def test_get_masked_keys_empty(vault_file):
    assert get_masked_keys(vault_file) == []


def test_get_masked_keys_multiple(vault_file):
    mask_var(vault_file, "KEY_A")
    mask_var(vault_file, "KEY_B")
    keys = get_masked_keys(vault_file)
    assert set(keys) == {"KEY_A", "KEY_B"}


def test_apply_masks_replaces_masked(vault_file):
    mask_var(vault_file, "SECRET")
    variables = {"SECRET": "my_secret_value", "PLAIN": "visible"}
    result = apply_masks(vault_file, variables)
    assert result["SECRET"] == MASK_PLACEHOLDER
    assert result["PLAIN"] == "visible"


def test_apply_masks_no_masks(vault_file):
    variables = {"KEY": "value", "OTHER": "data"}
    result = apply_masks(vault_file, variables)
    assert result == variables


def test_apply_masks_does_not_mutate_input(vault_file):
    mask_var(vault_file, "TOKEN")
    variables = {"TOKEN": "abc123"}
    result = apply_masks(vault_file, variables)
    assert variables["TOKEN"] == "abc123"
    assert result["TOKEN"] == MASK_PLACEHOLDER


def test_mask_idempotent(vault_file):
    mask_var(vault_file, "KEY")
    mask_var(vault_file, "KEY")
    assert get_masked_keys(vault_file).count("KEY") == 1


def test_get_mask_reason_not_masked_returns_none(vault_file):
    assert get_mask_reason(vault_file, "UNMASKED_KEY") is None
