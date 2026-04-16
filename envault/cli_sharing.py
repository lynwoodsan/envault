"""CLI commands for team sharing (bundle export/import)."""

import click
from pathlib import Path

from envault.cli import cli, get_password
from envault.sharing import export_bundle, import_bundle, bundle_note


@cli.command("share-export")
@click.argument("output", default="envault-bundle.json")
@click.option("--note", default="", help="Optional note to embed in the bundle.")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def share_export(output, note, vault):
    """Export vault as an encrypted shareable bundle."""
    password = get_password(confirm=False)
    vault_path = Path(vault)
    if not vault_path.exists():
        raise click.ClickException(f"Vault not found: {vault}")
    output_path = Path(output)
    export_bundle(vault_path, password, output_path, note=note or None)
    click.echo(f"Bundle exported to {output_path}")
    if note:
        click.echo(f"Note: {note}")


@cli.command("share-import")
@click.argument("bundle")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def share_import(bundle, vault):
    """Import an encrypted vault bundle."""
    bundle_path = Path(bundle)
    if not bundle_path.exists():
        raise click.ClickException(f"Bundle not found: {bundle}")
    note = bundle_note(bundle_path)
    if note:
        click.echo(f"Bundle note: {note}")
    password = get_password(confirm=False)
    vault_path = Path(vault)
    import_bundle(bundle_path, password, vault_path)
    click.echo(f"Vault imported from {bundle_path} to {vault_path}")
