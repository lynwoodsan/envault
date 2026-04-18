"""Audit log for envault — records vault operations with timestamps."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILENAME = ".envault_audit.json"


def _audit_path(vault_dir: str) -> Path:
    return Path(vault_dir) / AUDIT_FILENAME


def log_event(vault_dir: str, action: str, key: str, actor: str = "local") -> None:
    """Append an audit event to the log file."""
    path = _audit_path(vault_dir)
    events = _load_events(path)
    events.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
        "actor": actor,
    })
    with open(path, "w") as f:
        json.dump(events, f, indent=2)


def _load_events(path: Path) -> list:
    if not path.exists():
        return []
    with open(path) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def get_events(vault_dir: str) -> list:
    """Return all audit events for the given vault directory."""
    return _load_events(_audit_path(vault_dir))


def get_events_for_key(vault_dir: str, key: str) -> list:
    """Return all audit events related to a specific key."""
    return [e for e in get_events(vault_dir) if e.get("key") == key]


def clear_events(vault_dir: str) -> None:
    """Clear the audit log."""
    path = _audit_path(vault_dir)
    if path.exists():
        os.remove(path)


def format_events(events: list) -> str:
    """Format events for display."""
    if not events:
        return "No audit events recorded."
    lines = []
    for e in events:
        lines.append(f"[{e['timestamp']}] {e['action'].upper():8s} key={e['key']}  actor={e['actor']}")
    return "\n".join(lines)
