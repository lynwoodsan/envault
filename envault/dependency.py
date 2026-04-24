"""Dependency tracking between environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Set


def _dep_path(vault_path: Path) -> Path:
    return vault_path.parent / ".envault_deps.json"


def _load_deps(vault_path: Path) -> Dict[str, List[str]]:
    p = _dep_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deps(vault_path: Path, deps: Dict[str, List[str]]) -> None:
    _dep_path(vault_path).write_text(json.dumps(deps, indent=2))


def add_dependency(vault_path: Path, key: str, depends_on: str) -> None:
    """Record that `key` depends on `depends_on`."""
    deps = _load_deps(vault_path)
    existing: List[str] = deps.get(key, [])
    if depends_on not in existing:
        existing.append(depends_on)
    deps[key] = existing
    _save_deps(vault_path, deps)


def remove_dependency(vault_path: Path, key: str, depends_on: str) -> bool:
    """Remove a specific dependency. Returns True if it existed."""
    deps = _load_deps(vault_path)
    existing = deps.get(key, [])
    if depends_on not in existing:
        return False
    existing.remove(depends_on)
    if existing:
        deps[key] = existing
    else:
        deps.pop(key, None)
    _save_deps(vault_path, deps)
    return True


def get_dependencies(vault_path: Path, key: str) -> List[str]:
    """Return all keys that `key` directly depends on."""
    return _load_deps(vault_path).get(key, [])


def get_dependents(vault_path: Path, key: str) -> List[str]:
    """Return all keys that depend on `key`."""
    deps = _load_deps(vault_path)
    return [k for k, v in deps.items() if key in v]


def resolve_order(vault_path: Path, keys: Optional[List[str]] = None) -> List[str]:
    """Topological sort of keys by dependency order.
    Raises ValueError on circular dependency.
    """
    deps = _load_deps(vault_path)
    all_keys: Set[str] = set(keys) if keys else (set(deps.keys()) | {d for v in deps.values() for d in v})

    visited: Set[str] = set()
    visiting: Set[str] = set()
    order: List[str] = []

    def visit(k: str) -> None:
        if k in visiting:
            raise ValueError(f"Circular dependency detected involving '{k}'")
        if k in visited:
            return
        visiting.add(k)
        for dep in deps.get(k, []):
            if dep in all_keys:
                visit(dep)
        visiting.discard(k)
        visited.add(k)
        order.append(k)

    for k in sorted(all_keys):
        visit(k)

    return order
