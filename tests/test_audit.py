"""Tests for envault.audit module."""

import pytest
from envault.audit import log_event, get_events, clear_events, format_events


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_log_creates_event(vault_dir):
    log_event(vault_dir, "set", "API_KEY")
    events = get_events(vault_dir)
    assert len(events) == 1
    assert events[0]["action"] == "set"
    assert events[0]["key"] == "API_KEY"
    assert events[0]["actor"] == "local"


def test_log_multiple_events(vault_dir):
    log_event(vault_dir, "set", "FOO")
    log_event(vault_dir, "delete", "FOO")
    log_event(vault_dir, "set", "BAR")
    events = get_events(vault_dir)
    assert len(events) == 3
    assert events[1]["action"] == "delete"


def test_log_custom_actor(vault_dir):
    log_event(vault_dir, "set", "SECRET", actor="alice")
    events = get_events(vault_dir)
    assert events[0]["actor"] == "alice"


def test_get_events_missing_file(vault_dir):
    events = get_events(vault_dir)
    assert events == []


def test_clear_events(vault_dir):
    log_event(vault_dir, "set", "X")
    clear_events(vault_dir)
    assert get_events(vault_dir) == []


def test_clear_events_no_file(vault_dir):
    # Should not raise
    clear_events(vault_dir)


def test_format_events_empty():
    result = format_events([])
    assert "No audit" in result


def test_format_events_shows_action(vault_dir):
    log_event(vault_dir, "set", "MY_KEY", actor="bob")
    events = get_events(vault_dir)
    output = format_events(events)
    assert "SET" in output
    assert "MY_KEY" in output
    assert "bob" in output


def test_event_has_timestamp(vault_dir):
    log_event(vault_dir, "set", "TS_KEY")
    events = get_events(vault_dir)
    assert "timestamp" in events[0]
    assert "Z" in events[0]["timestamp"] or "+" in events[0]["timestamp"]
