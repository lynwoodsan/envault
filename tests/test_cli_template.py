import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.cli_template import template_group
from envault.vault import set_var


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def prepared_vault(tmp_path):
    vault = tmp_path / ".envault"
    password = "testpass"
    set_var(vault, password, "DB_HOST", "localhost")
    set_var(vault, password, "DB_PORT", "5432")
    return vault, password


def invoke(runner, vault, password, *args):
    return runner.invoke(template_group, list(args), input=password + "\n", env={"ENVAULT_VAULT": str(vault)})


def test_render_to_stdout(runner, prepared_vault, tmp_path):
    vault, password = prepared_vault
    tpl = tmp_path / "t.tpl"
    tpl.write_text("host={{DB_HOST}} port={{DB_PORT}}")
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--vault", str(vault)],
        input=password + "\n",
    )
    assert result.exit_code == 0
    assert "localhost" in result.output
    assert "5432" in result.output


def test_render_to_file(runner, prepared_vault, tmp_path):
    vault, password = prepared_vault
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{DB_HOST}}")
    out = tmp_path / "out.txt"
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--vault", str(vault), "--output", str(out)],
        input=password + "\n",
    )
    assert result.exit_code == 0
    assert out.read_text() == "localhost"


def test_render_missing_strict_fails(runner, prepared_vault, tmp_path):
    vault, password = prepared_vault
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{UNDEFINED_VAR}}")
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--vault", str(vault), "--strict"],
        input=password + "\n",
    )
    assert result.exit_code != 0
    assert "UNDEFINED_VAR" in result.output


def test_check_all_resolved(runner, prepared_vault, tmp_path):
    vault, password = prepared_vault
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{DB_HOST}}:{{DB_PORT}}")
    result = runner.invoke(
        template_group,
        ["check", str(tpl), "--vault", str(vault)],
        input=password + "\n",
    )
    assert result.exit_code == 0
    assert "All placeholders resolved" in result.output


def test_check_missing(runner, prepared_vault, tmp_path):
    vault, password = prepared_vault
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{DB_HOST}} {{MISSING_ONE}}")
    result = runner.invoke(
        template_group,
        ["check", str(tpl), "--vault", str(vault)],
        input=password + "\n",
    )
    assert result.exit_code == 1
    assert "MISSING_ONE" in result.output
