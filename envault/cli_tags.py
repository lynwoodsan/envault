"""CLI commands for variable tagging."""
import click
from envault.cli import get_password, cli
from envault.tags import add_tag, remove_tag, get_tags, list_by_tag, all_tags


@cli.group("tag")
def tag_group():
    """Manage tags on environment variables."""


@tag_group.command("add")
@click.argument("key")
@click.argument("tag")
@click.option("--vault", default=".envault", show_default=True)
def tag_add(key, tag, vault):
    """Add TAG to KEY."""
    password = get_password()
    add_tag(vault, password, key, tag)
    click.echo(f"Tagged {key} with '{tag}'.")


@tag_group.command("remove")
@click.argument("key")
@click.argument("tag")
@click.option("--vault", default=".envault", show_default=True)
def tag_remove(key, tag, vault):
    """Remove TAG from KEY."""
    password = get_password()
    removed = remove_tag(vault, password, key, tag)
    if removed:
        click.echo(f"Removed tag '{tag}' from {key}.")
    else:
        click.echo(f"Tag '{tag}' not found on {key}.", err=True)


@tag_group.command("list")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def tag_list(key, vault):
    """List tags for KEY."""
    password = get_password()
    tags = get_tags(vault, password, key)
    if tags:
        click.echo(", ".join(tags))
    else:
        click.echo(f"No tags for {key}.")


@tag_group.command("find")
@click.argument("tag")
@click.option("--vault", default=".envault", show_default=True)
def tag_find(tag, vault):
    """Find all variables with TAG."""
    password = get_password()
    keys = list_by_tag(vault, password, tag)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No variables tagged '{tag}'.")
