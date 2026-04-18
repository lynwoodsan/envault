import pytest
from pathlib import Path
from envault.template import render_template, render_file, find_placeholders, RenderError


VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


def test_render_simple():
    out = render_template("host={{ DB_HOST }}", VARS)
    assert out == "host=localhost"


def test_render_multiple():
    out = render_template("{{DB_HOST}}:{{DB_PORT}}", VARS)
    assert out == "localhost:5432"


def test_render_missing_strict_raises():
    with pytest.raises(RenderError, match="MISSING_VAR"):
        render_template("val={{MISSING_VAR}}", VARS, strict=True)


def test_render_missing_non_strict_keeps_placeholder():
    out = render_template("val={{MISSING_VAR}}", VARS, strict=False)
    assert "{{MISSING_VAR}}" in out


def test_render_no_placeholders():
    out = render_template("plain text", VARS)
    assert out == "plain text"


def test_find_placeholders():
    text = "{{DB_HOST}} and {{DB_PORT}} and {{DB_HOST}}"
    found = find_placeholders(text)
    assert found == ["DB_HOST", "DB_PORT"]


def test_find_placeholders_empty():
    assert find_placeholders("no placeholders here") == []


def test_render_file_writes_output(tmp_path):
    tpl = tmp_path / "config.tpl"
    tpl.write_text("host={{DB_HOST}}\nport={{DB_PORT}}")
    out = tmp_path / "config.txt"
    result = render_file(tpl, VARS, output_path=out)
    assert out.read_text() == result
    assert "localhost" in result
    assert "5432" in result


def test_render_file_no_output(tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("key={{API_KEY}}")
    result = render_file(tpl, VARS)
    assert result == "key=secret"


def test_render_file_missing_strict(tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{UNDEFINED}}")
    with pytest.raises(RenderError):
        render_file(tpl, VARS, strict=True)
