"""Track variable lineage — source origin and transformation history."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


def _lineage_path(vault_file: str) -> Path:
    return Path(vault_file).parent / ".envault_lineage.json"


def _load_lineage(vault_file: str) -> dict:
    p = _lineage_path(vault_file)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_lineage(vault_file: str, data: dict) -> None:
    p = _lineage_path(vault_file)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


@dataclass
class LineageEntry:
    key: str
    source: str
    origin_type: str  # e.g. "manual", "import", "derived", "external"
    derived_from: List[str] = field(default_factory=list)
    note: Optional[str] = None
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def set_lineage(
    vault_file: str,
    key: str,
    source: str,
    origin_type: str = "manual",
    derived_from: Optional[List[str]] = None,
    note: Optional[str] = None,
) -> LineageEntry:
    valid_types = ("manual", "import", "derived", "external")
    if origin_type not in valid_types:
        raise ValueError(f"origin_type must be one of {valid_types}")
    entry = LineageEntry(
        key=key,
        source=source,
        origin_type=origin_type,
        derived_from=derived_from or [],
        note=note,
    )
    data = _load_lineage(vault_file)
    data[key] = asdict(entry)
    _save_lineage(vault_file, data)
    return entry


def get_lineage(vault_file: str, key: str) -> Optional[LineageEntry]:
    data = _load_lineage(vault_file)
    raw = data.get(key)
    if raw is None:
        return None
    return LineageEntry(**raw)


def remove_lineage(vault_file: str, key: str) -> bool:
    data = _load_lineage(vault_file)
    if key not in data:
        return False
    del data[key]
    _save_lineage(vault_file, data)
    return True


def list_lineage(vault_file: str) -> List[LineageEntry]:
    data = _load_lineage(vault_file)
    return [LineageEntry(**v) for v in data.values()]


def get_derived_keys(vault_file: str, source_key: str) -> List[str]:
    """Return all keys that declare source_key in their derived_from list."""
    data = _load_lineage(vault_file)
    return [
        k for k, v in data.items()
        if source_key in v.get("derived_from", [])
    ]
