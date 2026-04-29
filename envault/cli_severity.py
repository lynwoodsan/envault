"""CLI commands for managing variable severity levels."""

from __future__ import annotations

from pathlib import Path

import click

from envault.severity import (
    set_severity,
    remove_severity,
    get_severity,
    list_severity,
    get_keys_by_level,
    VALID_LEVELS,
)


@click.group("severity")
def severity_group():
    """Manage severity levels for vault variables."""


@severity_group.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--note", default=None, help="Optional note about this severity assignment.")
@click.option("--vault", default="envault.vault", show_default=True)
def sev_set(key: str, level: str, note: str, vault: str):
    """Assign a severity level to a variable."""
    try:
        entry = set_severity(Path(vault), key, level, note=note)
        click.echo(f"Severity for '{entry.key}' set to [{entry.level.upper()}]")
        if entry.note:
            click.echo(f"  Note: {entry.note}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@severity_group.command("remove")
@click.argument("key")
@click.option("--vault", default="envault.vault", show_default=True)
def sev_remove(key: str, vault: str):
    """Remove severity assignment from a variable."""
    removed = remove_severity(Path(vault), key)
    if removed:
        click.echo(f"Severity removed from '{key}'.")
    else:
        click.echo(f"No severity assigned to '{key}'.")


@severity_group.command("show")
@click.argument("key")
@click.option("--vault", default="envault.vault", show_default=True)
def sev_show(key: str, vault: str):
    """Show the severity level of a variable."""
    entry = get_severity(Path(vault), key)
    if entry is None:
        click.echo(f"No severity assigned to '{key}'.")
    else:
        click.echo(f"{entry.key}: [{entry.level.upper()}]")
        if entry.note:
            click.echo(f"  Note: {entry.note}")
        click.echo(f"  Set at: {entry.set_at}")


@severity_group.command("list")
@click.option("--level", type=click.Choice(VALID_LEVELS), default=None, help="Filter by level.")
@click.option("--vault", default="envault.vault", show_default=True)
def sev_list(level: str, vault: str):
    """List all severity assignments."""
    if level:
        keys = get_keys_by_level(Path(vault), level)
        if not keys:
            click.echo(f"No variables assigned level '{level}'.")
        else:
            for k in keys:
                click.echo(f"  [{level.upper()}] {k}")
    else:
        entries = list_severity(Path(vault))
        if not entries:
            click.echo("No severity assignments found.")
        else:
            for e in entries:
                note_str = f"  # {e.note}" if e.note else ""
                click.echo(f"  [{e.level.upper():8s}] {e.key}{note_str}")
