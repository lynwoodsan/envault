"""CLI commands for variable group management."""

from __future__ import annotations

import click

from envault.grouping import (
    add_to_group,
    remove_from_group,
    get_group,
    list_groups,
    get_groups_for_key,
    delete_group,
)


@click.group("group")
def group_group() -> None:
    """Manage variable groups."""


@group_group.command("add")
@click.argument("group")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def grp_add(group: str, key: str, vault: str) -> None:
    """Add KEY to GROUP."""
    members = add_to_group(vault, group, key)
    click.echo(f"Added '{key}' to group '{group}'. Members: {', '.join(members)}")


@group_group.command("remove")
@click.argument("group")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def grp_remove(group: str, key: str, vault: str) -> None:
    """Remove KEY from GROUP."""
    removed = remove_from_group(vault, group, key)
    if removed:
        click.echo(f"Removed '{key}' from group '{group}'.")
    else:
        click.echo(f"Key '{key}' not found in group '{group}'.")
        raise SystemExit(1)


@group_group.command("show")
@click.argument("group")
@click.option("--vault", default="vault.enc", show_default=True)
def grp_show(group: str, vault: str) -> None:
    """Show all keys in GROUP."""
    members = get_group(vault, group)
    if not members:
        click.echo(f"Group '{group}' is empty or does not exist.")
        return
    for key in members:
        click.echo(key)


@group_group.command("list")
@click.option("--vault", default="vault.enc", show_default=True)
def grp_list(vault: str) -> None:
    """List all groups."""
    groups = list_groups(vault)
    if not groups:
        click.echo("No groups defined.")
        return
    for name, members in groups.items():
        click.echo(f"{name}: {', '.join(members)}")


@group_group.command("find")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def grp_find(key: str, vault: str) -> None:
    """Find all groups containing KEY."""
    groups = get_groups_for_key(vault, key)
    if not groups:
        click.echo(f"'{key}' is not in any group.")
        return
    for g in groups:
        click.echo(g)


@group_group.command("delete")
@click.argument("group")
@click.option("--vault", default="vault.enc", show_default=True)
def grp_delete(group: str, vault: str) -> None:
    """Delete an entire GROUP."""
    deleted = delete_group(vault, group)
    if deleted:
        click.echo(f"Deleted group '{group}'.")
    else:
        click.echo(f"Group '{group}' does not exist.")
        raise SystemExit(1)
