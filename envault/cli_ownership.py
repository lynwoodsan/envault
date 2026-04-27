"""CLI commands for variable ownership management."""

import click
from envault.ownership import (
    set_owner,
    remove_owner,
    get_owner,
    list_owned,
    get_keys_by_owner,
)


@click.group("ownership")
def ownership_group():
    """Manage variable ownership."""


@ownership_group.command("set")
@click.argument("key")
@click.argument("owner")
@click.option("--note", default="", help="Optional note about the ownership.")
@click.option("--vault", default="vault.enc", show_default=True)
def own_set(key, owner, note, vault):
    """Assign OWNER to KEY."""
    entry = set_owner(vault, key, owner, note=note)
    click.echo(f"Owner of '{key}' set to '{owner}' at {entry['assigned_at']}.")


@ownership_group.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def own_remove(key, vault):
    """Remove ownership record for KEY."""
    if remove_owner(vault, key):
        click.echo(f"Ownership record for '{key}' removed.")
    else:
        click.echo(f"No ownership record found for '{key}'.")
        raise SystemExit(1)


@ownership_group.command("show")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def own_show(key, vault):
    """Show ownership details for KEY."""
    entry = get_owner(vault, key)
    if not entry:
        click.echo(f"No ownership record for '{key}'.")
        raise SystemExit(1)
    click.echo(f"Key:         {key}")
    click.echo(f"Owner:       {entry['owner']}")
    click.echo(f"Assigned at: {entry['assigned_at']}")
    if entry.get("note"):
        click.echo(f"Note:        {entry['note']}")


@ownership_group.command("list")
@click.option("--owner", default=None, help="Filter by owner name.")
@click.option("--vault", default="vault.enc", show_default=True)
def own_list(owner, vault):
    """List all owned variables, optionally filtered by owner."""
    if owner:
        keys = get_keys_by_owner(vault, owner)
        if not keys:
            click.echo(f"No variables owned by '{owner}'.")
            return
        for k in keys:
            click.echo(k)
    else:
        owned = list_owned(vault)
        if not owned:
            click.echo("No ownership records found.")
            return
        for key, entry in owned.items():
            click.echo(f"{key:<30} {entry['owner']:<20} {entry['assigned_at']}")
