"""CLI commands for managing variable visibility levels."""

import click
from envault.cli import get_password
from envault.visibility import (
    set_visibility,
    get_visibility,
    remove_visibility,
    list_visibility,
    filter_by_visibility,
    VISIBILITY_LEVELS,
)


@click.group("visibility", help="Manage variable visibility levels.")
def visibility_group():
    pass


@visibility_group.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(VISIBILITY_LEVELS))
@click.option("--vault", default=".envault", show_default=True)
def vis_set(key, level, vault):
    """Set the visibility level for a KEY."""
    try:
        set_visibility(vault, key, level)
        click.echo(f"Visibility for '{key}' set to '{level}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@visibility_group.command("get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def vis_get(key, vault):
    """Get the visibility level for a KEY."""
    level = get_visibility(vault, key)
    if level is None:
        click.echo(f"'{key}' has no visibility level set.")
    else:
        click.echo(f"{key}: {level}")


@visibility_group.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def vis_remove(key, vault):
    """Remove the visibility setting for a KEY."""
    removed = remove_visibility(vault, key)
    if removed:
        click.echo(f"Visibility setting for '{key}' removed.")
    else:
        click.echo(f"No visibility setting found for '{key}'.")


@visibility_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--filter", "level_filter", type=click.Choice(VISIBILITY_LEVELS), default=None)
def vis_list(vault, level_filter):
    """List all visibility settings, optionally filtered by LEVEL."""
    if level_filter:
        keys = filter_by_visibility(vault, level_filter)
        if not keys:
            click.echo(f"No keys with visibility '{level_filter}'.")
        else:
            for k in sorted(keys):
                click.echo(f"{k}: {level_filter}")
    else:
        data = list_visibility(vault)
        if not data:
            click.echo("No visibility settings configured.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
