"""CLI commands for alias management."""
import click
from pathlib import Path
from envault.alias import add_alias, remove_alias, resolve_alias, list_aliases, reverse_lookup


@click.group("alias")
def alias_group():
    """Manage short aliases for vault keys."""


@alias_group.command("add")
@click.argument("alias")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def alias_add(alias, key, vault):
    """Add or update an alias mapping ALIAS -> KEY."""
    vf = Path(vault)
    add_alias(vf, alias, key)
    click.echo(f"Alias '{alias}' -> '{key}' saved.")


@alias_group.command("remove")
@click.argument("alias")
@click.option("--vault", default=".envault", show_default=True)
def alias_remove(alias, vault):
    """Remove an alias."""
    vf = Path(vault)
    if remove_alias(vf, alias):
        click.echo(f"Alias '{alias}' removed.")
    else:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)


@alias_group.command("resolve")
@click.argument("alias")
@click.option("--vault", default=".envault", show_default=True)
def alias_resolve(alias, vault):
    """Resolve an alias to its vault key."""
    vf = Path(vault)
    key = resolve_alias(vf, alias)
    if key is None:
        click.echo(f"No alias '{alias}' found.", err=True)
        raise SystemExit(1)
    click.echo(key)


@alias_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
def alias_list(vault):
    """List all aliases."""
    vf = Path(vault)
    aliases = list_aliases(vf)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, key in sorted(aliases.items()):
        click.echo(f"  {alias:20s} -> {key}")


@alias_group.command("reverse")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def alias_reverse(key, vault):
    """Find all aliases pointing to KEY."""
    vf = Path(vault)
    found = reverse_lookup(vf, key)
    if not found:
        click.echo(f"No aliases for '{key}'.")
    else:
        for a in sorted(found):
            click.echo(f"  {a}")
