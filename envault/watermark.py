"""Watermark support: embed metadata into exported bundles for traceability."""

import json
import hashlib
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_WATERMARK_PATH = ".envault_watermark.json"


def _watermark_path(vault_dir: Path) -> Path:
    return vault_dir / _WATERMARK_PATH


def _load_watermarks(vault_dir: Path) -> dict:
    p = _watermark_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_watermarks(vault_dir: Path, data: dict) -> None:
    _watermark_path(vault_dir).write_text(json.dumps(data, indent=2))


def create_watermark(
    vault_dir: Path,
    actor: str,
    note: Optional[str] = None,
) -> dict:
    """Create and persist a watermark entry for the current export/share event."""
    data = _load_watermarks(vault_dir)
    ts = datetime.now(timezone.utc).isoformat()
    hostname = socket.gethostname()
    token = hashlib.sha256(f"{actor}{ts}{hostname}".encode()).hexdigest()[:16]
    entry = {
        "actor": actor,
        "timestamp": ts,
        "hostname": hostname,
        "token": token,
        "note": note or "",
    }
    data[token] = entry
    _save_watermarks(vault_dir, data)
    return entry


def list_watermarks(vault_dir: Path) -> list:
    """Return all watermark entries sorted by timestamp descending."""
    data = _load_watermarks(vault_dir)
    entries = list(data.values())
    entries.sort(key=lambda e: e["timestamp"], reverse=True)
    return entries


def get_watermark(vault_dir: Path, token: str) -> Optional[dict]:
    """Retrieve a single watermark by token."""
    data = _load_watermarks(vault_dir)
    return data.get(token)


def remove_watermark(vault_dir: Path, token: str) -> bool:
    """Delete a watermark entry. Returns True if it existed."""
    data = _load_watermarks(vault_dir)
    if token not in data:
        return False
    del data[token]
    _save_watermarks(vault_dir, data)
    return True


def format_watermark(entry: dict) -> str:
    lines = [
        f"Token   : {entry['token']}",
        f"Actor   : {entry['actor']}",
        f"Host    : {entry['hostname']}",
        f"Time    : {entry['timestamp']}",
    ]
    if entry.get("note"):
        lines.append(f"Note    : {entry['note']}")
    return "\n".join(lines)
