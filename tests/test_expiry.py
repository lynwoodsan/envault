"""Tests for envault/expiry.py"""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from envault.expiry import (
    set_expiry,
    remove_expiry,
    get_expiry,
    is_expired,
    list_expiry,
    get_expired_keys,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    vf.write_text("{}")
    return str(vf)


def test_set_expiry_returns_datetime(vault_file):
    result = set_expiry(vault_file, "API_KEY", 30)
    assert isinstance(result, datetime)
    assert result.tzinfo is not None


def test_set_expiry_future_date(vault_file):
    result = set_expiry(vault_file, "API_KEY", 7)
    assert result > datetime.now(timezone.utc)


def test_set_expiry_invalid_days_raises(vault_file):
    with pytest.raises(ValueError):
        set_expiry(vault_file, "API_KEY", 0)
    with pytest.raises(ValueError):
        set_expiry(vault_file, "API_KEY", -5)


def test_get_expiry_returns_correct_date(vault_file):
    set_expiry(vault_file, "DB_PASS", 10)
    expiry = get_expiry(vault_file, "DB_PASS")
    assert expiry is not None
    delta = expiry - datetime.now(timezone.utc)
    assert 9 <= delta.days <= 10


def test_get_expiry_missing_returns_none(vault_file):
    assert get_expiry(vault_file, "NONEXISTENT") is None


def test_is_expired_not_yet(vault_file):
    set_expiry(vault_file, "TOKEN", 5)
    assert is_expired(vault_file, "TOKEN") is False


def test_is_expired_past(vault_file, monkeypatch):
    set_expiry(vault_file, "OLD_KEY", 1)
    # Monkeypatch the expiry data directly to a past date
    from envault import expiry as exp_mod
    import json
    from pathlib import Path
    p = Path(vault_file).parent / ".envault_expiry.json"
    past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    p.write_text(json.dumps({"OLD_KEY": past}))
    assert is_expired(vault_file, "OLD_KEY") is True


def test_is_expired_no_expiry_set(vault_file):
    assert is_expired(vault_file, "NO_EXPIRY") is False


def test_remove_expiry_returns_true(vault_file):
    set_expiry(vault_file, "KEY", 5)
    assert remove_expiry(vault_file, "KEY") is True
    assert get_expiry(vault_file, "KEY") is None


def test_remove_expiry_nonexistent_returns_false(vault_file):
    assert remove_expiry(vault_file, "GHOST") is False


def test_list_expiry_multiple_keys(vault_file):
    set_expiry(vault_file, "A", 1)
    set_expiry(vault_file, "B", 2)
    result = list_expiry(vault_file)
    assert set(result.keys()) == {"A", "B"}
    assert all(isinstance(v, datetime) for v in result.values())


def test_get_expired_keys(vault_file):
    import json
    from pathlib import Path
    p = Path(vault_file).parent / ".envault_expiry.json"
    now = datetime.now(timezone.utc)
    data = {
        "EXPIRED_KEY": (now - timedelta(days=1)).isoformat(),
        "VALID_KEY": (now + timedelta(days=5)).isoformat(),
    }
    p.write_text(json.dumps(data))
    expired = get_expired_keys(vault_file)
    assert "EXPIRED_KEY" in expired
    assert "VALID_KEY" not in expired
