"""Team sharing support: export/import encrypted vault bundles."""

import json
import base64
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt


BUNDLE_VERSION = 1


def export_bundle(vault_path: Path, password: str, output_path: Path, note: Optional[str] = None) -> None:
    """Export the encrypted vault as a shareable JSON bundle."""
    raw = vault_path.read_bytes()
    encoded = base64.b64encode(raw).decode()
    # Re-encrypt the bundle with the same password for portability
    bundle_payload = encrypt(encoded, password)
    bundle = {
        "version": BUNDLE_VERSION,
        "note": note or "",
        "payload": bundle_payload,
    }
    output_path.write_text(json.dumps(bundle, indent=2))


def import_bundle(bundle_path: Path, password: str, vault_path: Path) -> None:
    """Import an encrypted vault bundle and write it to the vault path."""
    bundle = json.loads(bundle_path.read_text())
    version = bundle.get("version")
    if version != BUNDLE_VERSION:
        raise ValueError(f"Unsupported bundle version: {version}")
    payload = bundle["payload"]
    encoded = decrypt(payload, password)
    raw = base64.b64decode(encoded.encode())
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    vault_path.write_bytes(raw)


def bundle_note(bundle_path: Path) -> str:
    """Return the note embedded in a bundle file."""
    bundle = json.loads(bundle_path.read_text())
    return bundle.get("note", "")
