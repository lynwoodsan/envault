"""CLI commands for variable deprecation management."""

from pathlib import Path

import click

from envault.deprecation import (
    deprecate_var,
    undeprecate_var,
    get_deprecation,
    list_deprecated,
    is_deprecated,
)


@click.group("deprecation")
def deprecation_group():
    """Manage deprecated vault variables."""


@deprecation_group.command("mark")
@click.argument("key")
@click.option("--reason", default="", help="Why this variable is deprecated.")
@click.option("--replacement", default=None, help="Suggested replacement key.")
@click.option("--sunset", default=None, help="Planned removal date (YYYY-MM-DD).")
@click.option("--vault", default="vault.enc", show_default=True)
def dep_mark(key, reason, replacement, sunset, vault):
    """Mark a variable as deprecated."""
    vault_file = Path(vault)
    entry = deprecate_var(vault_file, key, reason=reason, replacement=replacement, sunset_date=sunset)
    click.echo(f"Marked '{key}' as deprecated.")
    if reason:
        click.echo(f"  Reason: {reason}")
    if replacement:
        click.echo(f"  Replacement: {replacement}")
    if sunset:
        click.echo(f"  Sunset date: {sunset}")


@deprecation_group.command("unmark")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def dep_unmark(key, vault):
    """Remove deprecation from a variable."""
    vault_file = Path(vault)
    if undeprecate_var(vault_file, key):
        click.echo(f"Removed deprecation from '{key}'.")
    else:
        click.echo(f"'{key}' was not marked as deprecated.", err=True)
        raise SystemExit(1)


@deprecation_group.command("show")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def dep_show(key, vault):
    """Show deprecation details for a variable."""
    vault_file = Path(vault)
    entry = get_deprecation(vault_file, key)
    if entry is None:
        click.echo(f"'{key}' is not deprecated.")
        return
    click.echo(f"Key:         {entry['key']}")
    click.echo(f"Deprecated:  {entry['deprecated_at']}")
    click.echo(f"Reason:      {entry['reason'] or '(none)'}")
    click.echo(f"Replacement: {entry['replacement'] or '(none)'}")
    click.echo(f"Sunset date: {entry['sunset_date'] or '(none)'}")


@deprecation_group.command("list")
@click.option("--vault", default="vault.enc", show_default=True)
def dep_list(vault):
    """List all deprecated variables."""
    vault_file = Path(vault)
    items = list_deprecated(vault_file)
    if not items:
        click.echo("No deprecated variables.")
        return
    for entry in items:
        replacement = f" -> {entry['replacement']}" if entry["replacement"] else ""
        sunset = f" (sunset: {entry['sunset_date']})" if entry["sunset_date"] else ""
        click.echo(f"  {entry['key']}{replacement}{sunset}")
