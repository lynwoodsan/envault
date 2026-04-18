"""Snapshot support: save and compare vault state at a point in time."""
import json
import time
from pathlib import Path
from typing import Optional

from envault.vault import load_vault


def _snapshot_dir(vault_path: Path) -> Path:
    d = vault_path.parent / ".envault_snapshots"
    d.mkdir(exist_ok=True)
    return d


def create_snapshot(vault_path: Path, password: str, label: Optional[str] = None) -> Path:
    """Decrypt vault and save a plaintext JSON snapshot."""
    vars_ = load_vault(vault_path, password)
    ts = int(time.time())
    name = f"{ts}_{label}.json" if label else f"{ts}.json"
    snap_path = _snapshot_dir(vault_path) / name
    snap_path.write_text(json.dumps({"ts": ts, "label": label, "vars": vars_}, indent=2))
    return snap_path


def list_snapshots(vault_path: Path) -> list[dict]:
    """Return metadata for all snapshots, newest first."""
    snaps = []
    for p in sorted(_snapshot_dir(vault_path).glob("*.json"), reverse=True):
        try:
            data = json.loads(p.read_text())
            snaps.append({"file": p.name, "ts": data.get("ts"), "label": data.get("label"), "count": len(data.get("vars", {}))})
        except Exception:
            pass
    return snaps


def load_snapshot(vault_path: Path, filename: str) -> dict:
    """Load a snapshot by filename and return its vars dict."""
    p = _snapshot_dir(vault_path) / filename
    if not p.exists():
        raise FileNotFoundError(f"Snapshot not found: {filename}")
    data = json.loads(p.read_text())
    return data.get("vars", {})


def diff_snapshot(vault_path: Path, password: str, filename: str) -> list[dict]:
    """Compare current vault against a snapshot using diff logic."""
    from envault.diff import diff_vaults, format_diff
    snap_vars = load_snapshot(vault_path, filename)
    current_vars = load_vault(vault_path, password)
    entries = diff_vaults(vault_path, vault_path, password, password)
    # Re-implement with raw dicts
    from envault.diff import _compare_dicts, DiffEntry
    raw = _compare_dicts(snap_vars, current_vars)
    return raw
