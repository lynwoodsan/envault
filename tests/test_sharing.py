"""Tests for envault.sharing module."""

import pytest
from pathlib import Path

from envault.vault import set_var, load_vault
from envault.sharing import export_bundle, import_bundle, bundle_note


PASSWORD = "sharepass"


@pytest.fixture
def vault_file(tmp_path):
    vpath = tmp_path / ".envault"
    set_var(vpath, PASSWORD, "API_KEY", "secret123")
    set_var(vpath, PASSWORD, "DB_URL", "postgres://localhost/db")
    return vpath


def test_export_creates_bundle(vault_file, tmp_path):
    bundle = tmp_path / "bundle.json"
    export_bundle(vault_file, PASSWORD, bundle, note="test bundle")
    assert bundle.exists()


def test_bundle_note(vault_file, tmp_path):
    bundle = tmp_path / "bundle.json"
    export_bundle(vault_file, PASSWORD, bundle, note="for staging")
    assert bundle_note(bundle) == "for staging"


def test_bundle_note_empty(vault_file, tmp_path):
    bundle = tmp_path / "bundle.json"
    export_bundle(vault_file, PASSWORD, bundle)
    assert bundle_note(bundle) == ""


def test_import_bundle_roundtrip(vault_file, tmp_path):
    bundle = tmp_path / "bundle.json"
    export_bundle(vault_file, PASSWORD, bundle)

    new_vault = tmp_path / "new" / ".envault"
    import_bundle(bundle, PASSWORD, new_vault)

    vars_ = load_vault(new_vault, PASSWORD)
    assert vars_["API_KEY"] == "secret123"
    assert vars_["DB_URL"] == "postgres://localhost/db"


def test_import_wrong_password_raises(vault_file, tmp_path):
    bundle = tmp_path / "bundle.json"
    export_bundle(vault_file, PASSWORD, bundle)

    new_vault = tmp_path / "new" / ".envault"
    with pytest.raises(Exception):
        import_bundle(bundle, "wrongpass", new_vault)


def test_import_bad_version_raises(tmp_path):
    import json
    bundle = tmp_path / "bundle.json"
    bundle.write_text(json.dumps({"version": 99, "note": "", "payload": "x"}))
    with pytest.raises(ValueError, match="Unsupported bundle version"):
        import_bundle(bundle, PASSWORD, tmp_path / ".envault")
