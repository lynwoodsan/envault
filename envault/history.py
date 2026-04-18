"""Variable history: track value changes over time using the audit log."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from envault.audit import get_events_for_key, log_event
from envault.vault import load_vault, set_var


@dataclass
class HistoryEntry:
    timestamp: str
    action: str
    actor: str
    note: Optional[str] = None


def get_history(vault_path: str, key: str) -> List[HistoryEntry]:
    """Return history entries for a given key."""
    events = get_events_for_key(vault_path, key)
    return [
        HistoryEntry(
            timestamp=e["timestamp"],
            action=e["action"],
            actor=e.get("actor", "unknown"),
            note=e.get("note"),
        )
        for e in events
    ]


def format_history(entries: List[HistoryEntry]) -> str:
    """Format history entries as a human-readable string."""
    if not entries:
        return "No history found."
    lines = []
    for e in entries:
        line = f"[{e.timestamp}] {e.action} by {e.actor}"
        if e.note:
            line += f" — {e.note}"
        lines.append(line)
    return "\n".join(lines)


def history_summary(vault_path: str, password: str) -> dict:
    """Return a summary of change counts per key."""
    vars_ = load_vault(vault_path, password)
    summary = {}
    for key in vars_:
        events = get_events_for_key(vault_path, key)
        summary[key] = len(events)
    return summary
