"""CLI commands for variable annotations."""

import click
from envault.annotation import (
    set_annotation,
    get_annotation,
    remove_annotation,
    list_annotations,
    clear_annotations,
)


@click.group("annotate", help="Attach notes/comments to vault variables.")
def annotation_group():
    pass


@annotation_group.command("set")
@click.argument("key")
@click.argument("note")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
@click.option("--author", default="envault", show_default=True, help="Author name.")
def ann_set(key, note, vault, author):
    """Set or update an annotation for KEY."""
    entry = set_annotation(vault, key, note, author=author)
    click.echo(f"Annotation set for '{key}' by {entry['author']} at {entry['updated_at']}")


@annotation_group.command("get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def ann_get(key, vault):
    """Show the annotation for KEY."""
    entry = get_annotation(vault, key)
    if entry is None:
        click.echo(f"No annotation found for '{key}'.")
        raise SystemExit(1)
    click.echo(f"Key:     {key}")
    click.echo(f"Note:    {entry['note']}")
    click.echo(f"Author:  {entry['author']}")
    click.echo(f"Updated: {entry['updated_at']}")


@annotation_group.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def ann_remove(key, vault):
    """Remove the annotation for KEY."""
    if remove_annotation(vault, key):
        click.echo(f"Annotation removed for '{key}'.")
    else:
        click.echo(f"No annotation found for '{key}'.")
        raise SystemExit(1)


@annotation_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
def ann_list(vault):
    """List all annotations in the vault."""
    data = list_annotations(vault)
    if not data:
        click.echo("No annotations found.")
        return
    for key, entry in sorted(data.items()):
        click.echo(f"{key}: {entry['note']}  (by {entry['author']})")


@annotation_group.command("clear")
@click.option("--vault", default=".envault", show_default=True)
@click.confirmation_option(prompt="Remove ALL annotations?")
def ann_clear(vault):
    """Clear all annotations from the vault."""
    count = clear_annotations(vault)
    click.echo(f"Cleared {count} annotation(s).")
