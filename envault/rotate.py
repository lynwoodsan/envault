"""Key rotation: re-encrypt all vault variables with a new password."""

from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.audit import log_event


def rotate_password(
    vault_path: Path,
    old_password: str,
    new_password: str,
    actor: Optional[str] = None,
) -> int:
    """Re-encrypt every variable in the vault under *new_password*.

    Returns the number of variables that were rotated.
    Raises ValueError / cryptography errors if *old_password* is wrong.
    """
    data = load_vault(vault_path, old_password)

    if not data:
        return 0

    # save_vault re-encrypts each value with the new password
    save_vault(vault_path, new_password, data)

    count = len(data)
    log_event(
        vault_path,
        "rotate",
        key="*",
        actor=actor,
        extra={"variables_rotated": count},
    )
    return count


def rotation_preview(vault_path: Path, old_password: str) -> list[str]:
    """Return the list of variable names that would be rotated.

    Useful for a --dry-run flag in the CLI.
    Raises on wrong password.
    """
    data = load_vault(vault_path, old_password)
    return list(data.keys())
