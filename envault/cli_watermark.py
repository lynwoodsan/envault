"""CLI commands for managing vault watermarks."""

import click
from pathlib import Path
from envault.watermark import (
    create_watermark,
    list_watermarks,
    get_watermark,
    remove_watermark,
    format_watermark,
)


@click.group("watermark", help="Manage export watermarks for traceability.")
def watermark_group():
    pass


@watermark_group.command("create")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--actor", required=True, help="Name or ID of the actor creating the watermark.")
@click.option("--note", default="", help="Optional note to attach.")
def wm_create(vault_dir, actor, note):
    """Create a new watermark entry."""
    entry = create_watermark(Path(vault_dir), actor=actor, note=note or None)
    click.echo(f"Watermark created: {entry['token']}")
    click.echo(format_watermark(entry))


@watermark_group.command("list")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def wm_list(vault_dir):
    """List all watermarks."""
    entries = list_watermarks(Path(vault_dir))
    if not entries:
        click.echo("No watermarks found.")
        return
    for entry in entries:
        click.echo("-" * 40)
        click.echo(format_watermark(entry))
    click.echo("-" * 40)
    click.echo(f"Total: {len(entries)}")


@watermark_group.command("show")
@click.argument("token")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def wm_show(token, vault_dir):
    """Show details of a specific watermark by token."""
    entry = get_watermark(Path(vault_dir), token)
    if entry is None:
        click.echo(f"No watermark found with token: {token}", err=True)
        raise SystemExit(1)
    click.echo(format_watermark(entry))


@watermark_group.command("remove")
@click.argument("token")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def wm_remove(token, vault_dir):
    """Remove a watermark entry by token."""
    removed = remove_watermark(Path(vault_dir), token)
    if removed:
        click.echo(f"Watermark {token} removed.")
    else:
        click.echo(f"Watermark {token} not found.", err=True)
        raise SystemExit(1)
