import json
import pytest
from pathlib import Path
from envault.vault import set_var
from envault.snapshot import create_snapshot, list_snapshots, load_snapshot, diff_snapshot


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.json"
    password = "snapshotpass"
    set_var(vf, password, "DB_HOST", "localhost")
    set_var(vf, password, "DB_PORT", "5432")
    return vf, password


def test_create_snapshot_returns_path(vault_file):
    vf, pw = vault_file
    path = create_snapshot(vf, pw)
    assert path.exists()
    assert path.suffix == ".json"


def test_create_snapshot_with_label(vault_file):
    vf, pw = vault_file
    path = create_snapshot(vf, pw, label="before-deploy")
    assert "before-deploy" in path.name


def test_snapshot_contains_vars(vault_file):
    vf, pw = vault_file
    path = create_snapshot(vf, pw)
    data = json.loads(path.read_text())
    assert data["vars"]["DB_HOST"] == "localhost"
    assert data["vars"]["DB_PORT"] == "5432"


def test_list_snapshots_empty(tmp_path):
    vf = tmp_path / "vault.json"
    set_var(vf, "pw", "X", "1")
    snaps = list_snapshots(vf)
    assert snaps == []


def test_list_snapshots_returns_metadata(vault_file):
    vf, pw = vault_file
    create_snapshot(vf, pw, label="s1")
    create_snapshot(vf, pw, label="s2")
    snaps = list_snapshots(vf)
    assert len(snaps) == 2
    assert snaps[0]["count"] == 2
    labels = {s["label"] for s in snaps}
    assert "s1" in labels and "s2" in labels


def test_load_snapshot_roundtrip(vault_file):
    vf, pw = vault_file
    path = create_snapshot(vf, pw)
    vars_ = load_snapshot(vf, path.name)
    assert vars_["DB_HOST"] == "localhost"


def test_load_snapshot_missing_raises(vault_file):
    vf, pw = vault_file
    with pytest.raises(FileNotFoundError):
        load_snapshot(vf, "nonexistent.json")


def test_diff_snapshot_detects_added(vault_file):
    vf, pw = vault_file
    path = create_snapshot(vf, pw)
    set_var(vf, pw, "NEW_KEY", "newval")
    diffs = diff_snapshot(vf, pw, path.name)
    keys = [d["key"] for d in diffs]
    assert "NEW_KEY" in keys
