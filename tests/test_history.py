import pytest
from pathlib import Path
from envault.vault import set_var, delete_var
from envault.audit import log_event
from envault.history import get_history, format_history, history_summary, HistoryEntry

PASSWORD = "histpass"


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.json"
    set_var(str(p), PASSWORD, "API_KEY", "abc123")
    set_var(str(p), PASSWORD, "DB_URL", "postgres://localhost/dev")
    return p


def test_get_history_returns_entries(vault_file):
    log_event(str(vault_file), "set", "API_KEY", actor="alice")
    log_event(str(vault_file), "set", "API_KEY", actor="bob")
    history = get_history(str(vault_file), "API_KEY")
    assert len(history) >= 2
    assert all(isinstance(e, HistoryEntry) for e in history)


def test_get_history_empty_for_unknown_key(vault_file):
    history = get_history(str(vault_file), "NONEXISTENT_KEY")
    assert history == []


def test_get_history_actor_preserved(vault_file):
    log_event(str(vault_file), "set", "DB_URL", actor="carol")
    history = get_history(str(vault_file), "DB_URL")
    actors = [e.actor for e in history]
    assert "carol" in actors


def test_get_history_entries_are_ordered_by_timestamp(vault_file):
    """Verify that history entries are returned in chronological order."""
    log_event(str(vault_file), "set", "API_KEY", actor="first")
    log_event(str(vault_file), "set", "API_KEY", actor="second")
    history = get_history(str(vault_file), "API_KEY")
    timestamps = [e.timestamp for e in history]
    assert timestamps == sorted(timestamps)


def test_format_history_no_entries():
    result = format_history([])
    assert result == "No history found."


def test_format_history_with_entries(vault_file):
    log_event(str(vault_file), "set", "API_KEY", actor="alice", note="initial")
    history = get_history(str(vault_file), "API_KEY")
    output = format_history(history)
    assert "set" in output
    assert "alice" in output


def test_format_history_includes_note(vault_file):
    log_event(str(vault_file), "set", "API_KEY", actor="dev", note="rotated key")
    history = get_history(str(vault_file), "API_KEY")
    output = format_history(history)
    assert "rotated key" in output


def test_history_summary_counts(vault_file):
    log_event(str(vault_file), "set", "API_KEY", actor="x")
    log_event(str(vault_file), "set", "API_KEY", actor="x")
    log_event(str(vault_file), "set", "DB_URL", actor="x")
    summary = history_summary(str(vault_file), PASSWORD)
    assert summary["API_KEY"] >= 2
    assert summary["DB_URL"] >= 1
