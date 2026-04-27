"""CLI commands for vault inheritance management."""

from pathlib import Path

import click

from envault.inheritance import (
    add_parent,
    remove_parent,
    list_parents,
    add_override,
    remove_override,
    get_overrides,
)


@click.group(name="inherit", help="Manage vault inheritance from parent vaults.")
def inheritance_group():
    pass


@inheritance_group.command("add-parent")
@click.argument("parent_path")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def inh_add_parent(parent_path: str, vault_dir: str):
    """Register a parent vault for inheritance."""
    add_parent(Path(vault_dir), parent_path)
    click.echo(f"Parent added: {parent_path}")


@inheritance_group.command("remove-parent")
@click.argument("parent_path")
@click.option("--vault-dir", default=".", show_default=True)
def inh_remove_parent(parent_path: str, vault_dir: str):
    """Remove a parent vault from the inheritance chain."""
    removed = remove_parent(Path(vault_dir), parent_path)
    if removed:
        click.echo(f"Parent removed: {parent_path}")
    else:
        click.echo(f"Parent not found: {parent_path}", err=True)
        raise SystemExit(1)


@inheritance_group.command("list-parents")
@click.option("--vault-dir", default=".", show_default=True)
def inh_list_parents(vault_dir: str):
    """List all registered parent vaults."""
    parents = list_parents(Path(vault_dir))
    if not parents:
        click.echo("No parent vaults registered.")
    else:
        for p in parents:
            click.echo(p)


@inheritance_group.command("override")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def inh_override(key: str, vault_dir: str):
    """Mark a key as locally overridden (never inherited)."""
    add_override(Path(vault_dir), key)
    click.echo(f"Key marked as override: {key}")


@inheritance_group.command("unoverride")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def inh_unoverride(key: str, vault_dir: str):
    """Remove override mark from a key."""
    removed = remove_override(Path(vault_dir), key)
    if removed:
        click.echo(f"Override removed for key: {key}")
    else:
        click.echo(f"Key not in overrides: {key}", err=True)
        raise SystemExit(1)


@inheritance_group.command("list-overrides")
@click.option("--vault-dir", default=".", show_default=True)
def inh_list_overrides(vault_dir: str):
    """List all keys marked as local overrides."""
    overrides = get_overrides(Path(vault_dir))
    if not overrides:
        click.echo("No overrides defined.")
    else:
        for key in overrides:
            click.echo(key)
