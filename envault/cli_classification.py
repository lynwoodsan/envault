"""CLI commands for variable classification."""

import click
from envault.classification import (
    classify_var,
    unclassify_var,
    get_classification,
    list_classifications,
    get_keys_by_level,
    VALID_LEVELS,
)


@click.group("classify")
def classification_group():
    """Manage variable sensitivity classifications."""


@classification_group.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--note", default=None, help="Optional note about this classification.")
@click.option("--vault", default=".envault", show_default=True)
def cls_set(key, level, note, vault):
    """Classify KEY at a sensitivity LEVEL."""
    try:
        classify_var(vault, key, level, note=note)
        click.echo(f"Classified '{key}' as '{level}'.")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@classification_group.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cls_remove(key, vault):
    """Remove classification from KEY."""
    removed = unclassify_var(vault, key)
    if removed:
        click.echo(f"Removed classification for '{key}'.")
    else:
        click.echo(f"No classification found for '{key}'.")


@classification_group.command("show")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cls_show(key, vault):
    """Show classification for KEY."""
    entry = get_classification(vault, key)
    if entry is None:
        click.echo(f"No classification for '{key}'.")
    else:
        note_str = f"  note: {entry['note']}" if entry["note"] else ""
        click.echo(f"{key}: {entry['level']}{note_str}")


@classification_group.command("list")
@click.option("--level", default=None, type=click.Choice(VALID_LEVELS))
@click.option("--vault", default=".envault", show_default=True)
def cls_list(level, vault):
    """List all classified variables, optionally filtered by LEVEL."""
    if level:
        keys = get_keys_by_level(vault, level)
        for k in keys:
            click.echo(f"{k}: {level}")
        if not keys:
            click.echo(f"No keys classified as '{level}'.")
    else:
        data = list_classifications(vault)
        if not data:
            click.echo("No classifications defined.")
        for k, v in sorted(data.items()):
            note_str = f"  ({v['note']})" if v.get("note") else ""
            click.echo(f"{k}: {v['level']}{note_str}")
