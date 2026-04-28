"""changelog.py — Track and display a human-readable changelog for vault variables.

Builds on top of the audit log to produce structured change summaries
per key, including what changed, when, and who made the change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from envault.audit import get_events_for_key, get_events


@dataclass
class ChangeEntry:
    """A single changelog entry for a variable."""
    key: str
    action: str          # e.g. "set", "delete", "rotate"
    actor: str
    timestamp: datetime
    note: Optional[str] = None


@dataclass
class KeyChangelog:
    """Full changelog for a single key."""
    key: str
    entries: List[ChangeEntry] = field(default_factory=list)

    @property
    def last_modified(self) -> Optional[datetime]:
        if not self.entries:
            return None
        return max(e.timestamp for e in self.entries)

    @property
    def created_at(self) -> Optional[datetime]:
        if not self.entries:
            return None
        return min(e.timestamp for e in self.entries)

    @property
    def change_count(self) -> int:
        return len(self.entries)


def get_key_changelog(vault_path: Path, key: str) -> KeyChangelog:
    """Return the changelog for a specific key, derived from audit events."""
    events = get_events_for_key(vault_path, key)
    entries = [
        ChangeEntry(
            key=e["key"],
            action=e["action"],
            actor=e.get("actor", "unknown"),
            timestamp=datetime.fromisoformat(e["timestamp"]),
            note=e.get("note"),
        )
        for e in events
    ]
    # Chronological order
    entries.sort(key=lambda e: e.timestamp)
    return KeyChangelog(key=key, entries=entries)


def get_vault_changelog(vault_path: Path) -> List[KeyChangelog]:
    """Return changelogs for all keys that have audit events."""
    events = get_events(vault_path)
    keys = {e["key"] for e in events if "key" in e}
    changelogs = [get_key_changelog(vault_path, k) for k in sorted(keys)]
    # Sort by most recently modified first
    changelogs.sort(key=lambda c: c.last_modified or datetime.min, reverse=True)
    return changelogs


def format_key_changelog(changelog: KeyChangelog, max_entries: int = 0) -> str:
    """Format a KeyChangelog as a human-readable string.

    Args:
        changelog: The KeyChangelog to format.
        max_entries: If > 0, show only the most recent N entries.

    Returns:
        A formatted multi-line string.
    """
    lines = [f"Changelog for {changelog.key}  ({changelog.change_count} change(s))"]
    lines.append("-" * len(lines[0]))

    entries = changelog.entries
    if max_entries > 0:
        entries = entries[-max_entries:]

    if not entries:
        lines.append("  (no recorded changes)")
        return "\n".join(lines)

    for entry in reversed(entries):  # newest first
        ts = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        note_part = f"  — {entry.note}" if entry.note else ""
        lines.append(f"  [{ts}] {entry.action:<10} by {entry.actor}{note_part}")

    return "\n".join(lines)


def format_vault_changelog(vault_path: Path, max_entries: int = 5) -> str:
    """Format changelogs for all keys in the vault."""
    changelogs = get_vault_changelog(vault_path)
    if not changelogs:
        return "No changelog entries found."
    sections = [format_key_changelog(cl, max_entries=max_entries) for cl in changelogs]
    return "\n\n".join(sections)
