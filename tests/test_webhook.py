"""Tests for envault.webhook module."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from envault.webhook import (
    add_webhook,
    remove_webhook,
    list_webhooks,
    fire_event,
    _webhook_path,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    vf.write_text("{}")
    return vf


def test_add_webhook_creates_entry(vault_file):
    add_webhook(vault_file, "ci", "https://example.com/hook")
    data = json.loads(_webhook_path(vault_file).read_text())
    assert "ci" in data
    assert data["ci"]["url"] == "https://example.com/hook"
    assert data["ci"]["events"] == []


def test_add_webhook_with_events(vault_file):
    add_webhook(vault_file, "notify", "https://example.com/n", events=["set", "delete"])
    data = json.loads(_webhook_path(vault_file).read_text())
    assert data["notify"]["events"] == ["set", "delete"]


def test_add_webhook_idempotent_overwrite(vault_file):
    add_webhook(vault_file, "ci", "https://old.example.com/hook")
    add_webhook(vault_file, "ci", "https://new.example.com/hook")
    hooks = list_webhooks(vault_file)
    assert hooks["ci"]["url"] == "https://new.example.com/hook"


def test_remove_webhook_returns_true(vault_file):
    add_webhook(vault_file, "ci", "https://example.com/hook")
    result = remove_webhook(vault_file, "ci")
    assert result is True
    assert "ci" not in list_webhooks(vault_file)


def test_remove_nonexistent_returns_false(vault_file):
    result = remove_webhook(vault_file, "ghost")
    assert result is False


def test_list_webhooks_empty(vault_file):
    assert list_webhooks(vault_file) == {}


def test_list_webhooks_multiple(vault_file):
    add_webhook(vault_file, "a", "https://a.example.com")
    add_webhook(vault_file, "b", "https://b.example.com")
    hooks = list_webhooks(vault_file)
    assert set(hooks.keys()) == {"a", "b"}


def test_fire_event_calls_all_matching(vault_file):
    add_webhook(vault_file, "all", "https://all.example.com")
    add_webhook(vault_file, "set_only", "https://set.example.com", events=["set"])
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        results = fire_event(vault_file, "set", {"key": "FOO"})
    assert len(results) == 2
    assert all(ok for _, ok in results)


def test_fire_event_skips_non_matching(vault_file):
    add_webhook(vault_file, "delete_only", "https://del.example.com", events=["delete"])
    with patch("urllib.request.urlopen") as mock_open:
        results = fire_event(vault_file, "set", {"key": "FOO"})
    mock_open.assert_not_called()
    assert results == []


def test_fire_event_handles_failure(vault_file):
    import urllib.error
    add_webhook(vault_file, "broken", "https://broken.example.com")
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        results = fire_event(vault_file, "set", {"key": "FOO"})
    assert results == [("broken", False)]
