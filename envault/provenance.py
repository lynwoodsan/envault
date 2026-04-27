"""provenance.py — Track the origin/source of environment variables.

Each variable can be annotated with where it came from (e.g. 'manual',
'imported', 'generated', 'ci', 'secret-manager') along with optional
metadata such as a source URL or reference ID.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

VALID_SOURCES = ("manual", "imported", "generated", "ci", "secret-manager", "other")


def _provenance_path(vault_path: str | Path) -> Path:
    """Return the sidecar file that stores provenance records."""
    return Path(vault_path).parent / ".envault_provenance.json"


def _load_provenance(vault_path: str | Path) -> dict:
    path = _provenance_path(vault_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_provenance(vault_path: str | Path, data: dict) -> None:
    path = _provenance_path(vault_path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def set_provenance(
    vault_path: str | Path,
    key: str,
    source: str,
    reference: Optional[str] = None,
    actor: Optional[str] = None,
) -> dict:
    """Record the provenance of *key*.

    Args:
        vault_path: Path to the ``.envault`` file.
        key:        The variable name.
        source:     One of :data:`VALID_SOURCES`.
        reference:  Optional free-form reference (URL, ticket ID, etc.).
        actor:      Who recorded the provenance (defaults to ``'envault'``).

    Returns:
        The newly stored provenance entry as a dict.

    Raises:
        ValueError: If *source* is not one of the recognised values.
    """
    if source not in VALID_SOURCES:
        raise ValueError(
            f"Invalid source {source!r}. Must be one of: {', '.join(VALID_SOURCES)}"
        )

    data = _load_provenance(vault_path)
    entry = {
        "source": source,
        "reference": reference,
        "actor": actor or "envault",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    data[key] = entry
    _save_provenance(vault_path, data)
    return entry


def get_provenance(vault_path: str | Path, key: str) -> Optional[dict]:
    """Return the provenance entry for *key*, or ``None`` if not recorded."""
    return _load_provenance(vault_path).get(key)


def remove_provenance(vault_path: str | Path, key: str) -> bool:
    """Remove the provenance record for *key*.

    Returns:
        ``True`` if the record existed and was removed, ``False`` otherwise.
    """
    data = _load_provenance(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_provenance(vault_path, data)
    return True


def list_provenance(vault_path: str | Path) -> dict[str, dict]:
    """Return all provenance records keyed by variable name."""
    return _load_provenance(vault_path)


def get_keys_by_source(vault_path: str | Path, source: str) -> list[str]:
    """Return all variable names whose provenance source matches *source*."""
    data = _load_provenance(vault_path)
    return [k for k, v in data.items() if v.get("source") == source]
