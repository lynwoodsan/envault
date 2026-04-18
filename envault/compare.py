"""Compare two vault files or a vault against a .env file."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
from envault.vault import load_vault
from envault.export import import_dotenv


@dataclass
class CompareResult:
    key: str
    status: str  # 'match', 'mismatch', 'only_left', 'only_right'
    left: Optional[str] = None
    right: Optional[str] = None


def compare_dicts(left: Dict[str, str], right: Dict[str, str]) -> List[CompareResult]:
    results = []
    all_keys = set(left) | set(right)
    for key in sorted(all_keys):
        if key in left and key not in right:
            results.append(CompareResult(key=key, status="only_left", left=left[key]))
        elif key in right and key not in left:
            results.append(CompareResult(key=key, status="only_right", right=right[key]))
        elif left[key] == right[key]:
            results.append(CompareResult(key=key, status="match", left=left[key], right=right[key]))
        else:
            results.append(CompareResult(key=key, status="mismatch", left=left[key], right=right[key]))
    return results


def compare_vaults(vault_a: str, password_a: str, vault_b: str, password_b: str) -> List[CompareResult]:
    left = load_vault(vault_a, password_a)
    right = load_vault(vault_b, password_b)
    return compare_dicts(left, right)


def compare_vault_dotenv(vault_path: str, password: str, dotenv_path: str) -> List[CompareResult]:
    left = load_vault(vault_path, password)
    right = import_dotenv(dotenv_path)
    return compare_dicts(left, right)


def format_compare_report(results: List[CompareResult], show_values: bool = False) -> str:
    lines = []
    counts = {"match": 0, "mismatch": 0, "only_left": 0, "only_right": 0}
    for r in results:
        counts[r.status] += 1
        if r.status == "match":
            lines.append(f"  = {r.key}")
        elif r.status == "mismatch":
            if show_values:
                lines.append(f"  ~ {r.key}  (left={r.left!r}, right={r.right!r})")
            else:
                lines.append(f"  ~ {r.key}  [values differ]")
        elif r.status == "only_left":
            lines.append(f"  < {r.key}  [only in left]")
        elif r.status == "only_right":
            lines.append(f"  > {r.key}  [only in right]")
    summary = (f"\nSummary: {counts['match']} match, {counts['mismatch']} mismatch, "
               f"{counts['only_left']} only-left, {counts['only_right']} only-right")
    return "\n".join(lines) + summary
