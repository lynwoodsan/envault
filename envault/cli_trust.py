"""CLI commands for managing variable trust levels."""

import click
from pathlib import Path
from envault.trust import (
    set_trust,
    remove_trust,
    get_trust,
    list_trust,
    get_keys_by_level,
    VALID_LEVELS,
)


@click.group("trust")
def trust_group():
    """Manage trust levels for vault variables."""


@trust_group.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--note", default="", help="Optional note about this trust assignment.")
@click.option("--actor", default="user", help="Who is setting the trust level.")
@click.option("--vault", "vault_file", default="vault.enc", show_default=True)
def trust_set(key, level, note, actor, vault_file):
    """Assign a trust level to a variable."""
    try:
        entry = set_trust(Path(vault_file), key, level, note=note, actor=actor)
        click.echo(f"Trust level '{entry.level}' set for '{key}' by {entry.set_by}.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@trust_group.command("remove")
@click.argument("key")
@click.option("--vault", "vault_file", default="vault.enc", show_default=True)
def trust_remove(key, vault_file):
    """Remove the trust level for a variable."""
    removed = remove_trust(Path(vault_file), key)
    if removed:
        click.echo(f"Trust entry removed for '{key}'.")
    else:
        click.echo(f"No trust entry found for '{key}'.")
        raise SystemExit(1)


@trust_group.command("show")
@click.argument("key")
@click.option("--vault", "vault_file", default="vault.enc", show_default=True)
def trust_show(key, vault_file):
    """Show the trust level for a variable."""
    entry = get_trust(Path(vault_file), key)
    if entry is None:
        click.echo(f"No trust entry for '{key}'.")
        raise SystemExit(1)
    click.echo(f"Key:   {entry.key}")
    click.echo(f"Level: {entry.level}")
    click.echo(f"By:    {entry.set_by}")
    click.echo(f"At:    {entry.set_at}")
    if entry.note:
        click.echo(f"Note:  {entry.note}")


@trust_group.command("list")
@click.option("--level", default=None, type=click.Choice(VALID_LEVELS), help="Filter by trust level.")
@click.option("--vault", "vault_file", default="vault.enc", show_default=True)
def trust_list(level, vault_file):
    """List all trust assignments, optionally filtered by level."""
    if level:
        keys = get_keys_by_level(Path(vault_file), level)
        if not keys:
            click.echo(f"No variables with trust level '{level}'.")
        for k in keys:
            click.echo(k)
    else:
        entries = list_trust(Path(vault_file))
        if not entries:
            click.echo("No trust entries found.")
        for e in entries:
            note_str = f"  # {e.note}" if e.note else ""
            click.echo(f"{e.key:<30} {e.level:<12}{note_str}")
