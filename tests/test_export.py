import os
import pytest
from envault.export import export_dotenv, import_dotenv


def test_export_creates_file(tmp_path):
    vault = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    out = tmp_path / ".env"
    export_dotenv(vault, str(out))
    assert out.exists()


def test_export_content(tmp_path):
    vault = {"API_KEY": "secret"}
    out = tmp_path / ".env"
    export_dotenv(vault, str(out))
    content = out.read_text()
    assert 'API_KEY="secret"' in content


def test_export_escapes_quotes(tmp_path):
    vault = {"MSG": 'say "hello"'}
    out = tmp_path / ".env"
    export_dotenv(vault, str(out))
    content = out.read_text()
    assert '\\"' in content


def test_import_basic(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    vault = {}
    count = import_dotenv(vault, str(env_file))
    assert count == 2
    assert vault["FOO"] == "bar"
    assert vault["BAZ"] == "qux"


def test_import_strips_quotes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('KEY="quoted value"\n')
    vault = {}
    import_dotenv(vault, str(env_file))
    assert vault["KEY"] == "quoted value"


def test_import_skips_comments(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nREAL=value\n")
    vault = {}
    count = import_dotenv(vault, str(env_file))
    assert count == 1
    assert "REAL" in vault


def test_import_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        import_dotenv({}, str(tmp_path / "missing.env"))


def test_import_merges_into_existing(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("NEW=val\n")
    vault = {"OLD": "existing"}
    import_dotenv(vault, str(env_file))
    assert "OLD" in vault
    assert "NEW" in vault
