"""Vault file management: read/write encrypted .envault files."""

import json
import os
from pathlib import Path
from typing import Dict

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_FILE = ".envault"


def load_vault(password: str, vault_path: str = DEFAULT_VAULT_FILE) -> Dict[str, str]:
    """Load and decrypt the vault file, returning a dict of env vars."""
    path = Path(vault_path)
    if not path.exists():
        return {}

    ciphertext = path.read_text(encoding="utf-8").strip()
    if not ciphertext:
        return {}

    plaintext = decrypt(ciphertext, password)
    return json.loads(plaintext)


def save_vault(
    data: Dict[str, str],
    password: str,
    vault_path: str = DEFAULT_VAULT_FILE,
) -> None:
    """Encrypt and save env vars dict to the vault file."""
    plaintext = json.dumps(data, indent=2, sort_keys=True)
    ciphertext = encrypt(plaintext, password)
    Path(vault_path).write_text(ciphertext + "\n", encoding="utf-8")


def set_var(
    key: str,
    value: str,
    password: str,
    vault_path: str = DEFAULT_VAULT_FILE,
) -> None:
    """Set a single environment variable in the vault."""
    data = load_vault(password, vault_path)
    data[key] = value
    save_vault(data, password, vault_path)


def delete_var(
    key: str,
    password: str,
    vault_path: str = DEFAULT_VAULT_FILE,
) -> bool:
    """Delete a variable from the vault. Returns True if it existed."""
    data = load_vault(password, vault_path)
    if key not in data:
        return False
    del data[key]
    save_vault(data, password, vault_path)
    return True


def list_vars(
    password: str,
    vault_path: str = DEFAULT_VAULT_FILE,
) -> Dict[str, str]:
    """Return all variables stored in the vault."""
    return load_vault(password, vault_path)


def inject_env(
    password: str,
    vault_path: str = DEFAULT_VAULT_FILE,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Load vault variables into the current process environment.

    Args:
        password: The vault password used for decryption.
        vault_path: Path to the vault file.
        overwrite: If True, overwrite existing environment variables.
                   If False (default), skip variables already set.

    Returns:
        A dict of the variables that were actually injected.
    """
    data = load_vault(password, vault_path)
    injected = {}
    for key, value in data.items():
        if overwrite or key not in os.environ:
            os.environ[key] = value
            injected[key] = value
    return injected
