"""CLI commands for template rendering."""
import click
from pathlib import Path
from envault.cli import get_password
from envault.vault import list_vars
from envault.template import render_file, find_placeholders, RenderError


@click.group("template")
def template_group():
    """Render templates using vault variables."""


@template_group.command("render")
@click.argument("template", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None, help="Output file path")
@click.option("--vault", "-v", type=click.Path(path_type=Path), default=Path(".envault"), show_default=True)
@click.option("--strict/--no-strict", default=True, show_default=True, help="Fail on missing variables")
def tpl_render(template: Path, output: Path, vault: Path, strict: bool):
    """Render a template file substituting vault variables."""
    password = get_password()
    try:
        variables = list_vars(vault, password)
    except Exception as e:
        raise click.ClickException(str(e))
    try:
        rendered = render_file(template, variables, output_path=output, strict=strict)
    except RenderError as e:
        raise click.ClickException(str(e))
    if output:
        click.echo(f"Rendered to {output}")
    else:
        click.echo(rendered, nl=False)


@template_group.command("check")
@click.argument("template", type=click.Path(exists=True, path_type=Path))
@click.option("--vault", "-v", type=click.Path(path_type=Path), default=Path(".envault"), show_default=True)
def tpl_check(template: Path, vault: Path):
    """Check which template placeholders are missing from the vault."""
    password = get_password()
    try:
        variables = list_vars(vault, password)
    except Exception as e:
        raise click.ClickException(str(e))
    text = template.read_text(encoding="utf-8")
    placeholders = find_placeholders(text)
    missing = [p for p in placeholders if p not in variables]
    if not placeholders:
        click.echo("No placeholders found in template.")
        return
    click.echo(f"Placeholders : {len(placeholders)}")
    click.echo(f"Resolved     : {len(placeholders) - len(missing)}")
    if missing:
        click.echo("Missing:")
        for m in missing:
            click.echo(f"  - {m}")
        raise SystemExit(1)
    else:
        click.echo("All placeholders resolved.")
