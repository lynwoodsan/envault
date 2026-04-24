"""Webhook notification support for envault events."""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

_WEBHOOK_FILE = ".envault_webhooks.json"


def _webhook_path(vault_path: Path) -> Path:
    return vault_path.parent / _WEBHOOK_FILE


def _load_webhooks(vault_path: Path) -> dict:
    p = _webhook_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_webhooks(vault_path: Path, data: dict) -> None:
    _webhook_path(vault_path).write_text(json.dumps(data, indent=2))


def add_webhook(vault_path: Path, name: str, url: str, events: Optional[list] = None) -> None:
    """Register a webhook URL, optionally filtering by event types."""
    data = _load_webhooks(vault_path)
    data[name] = {"url": url, "events": events or []}
    _save_webhooks(vault_path, data)


def remove_webhook(vault_path: Path, name: str) -> bool:
    """Remove a webhook by name. Returns True if it existed."""
    data = _load_webhooks(vault_path)
    if name not in data:
        return False
    del data[name]
    _save_webhooks(vault_path, data)
    return True


def list_webhooks(vault_path: Path) -> dict:
    """Return all registered webhooks."""
    return _load_webhooks(vault_path)


def fire_event(vault_path: Path, event: str, payload: dict) -> list:
    """Send event payload to all matching webhooks. Returns list of (name, success) tuples."""
    data = _load_webhooks(vault_path)
    results = []
    body = json.dumps({"event": event, "payload": payload}).encode()
    for name, cfg in data.items():
        allowed = cfg.get("events", [])
        if allowed and event not in allowed:
            continue
        req = urllib.request.Request(
            cfg["url"],
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5):
                results.append((name, True))
        except (urllib.error.URLError, OSError):
            results.append((name, False))
    return results
