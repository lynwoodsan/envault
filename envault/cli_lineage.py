"""CLI commands for variable lineage tracking."""

import click

from envault.lineage import (
    get_derived_keys,
    get_lineage,
    list_lineage,
    remove_lineage,
    set_lineage,
)


@click.group("lineage")
def lineage_group():
    """Track and inspect variable lineage and origin."""


@lineage_group.command("set")
@click.argument("key")
@click.argument("source")
@click.option("--type", "origin_type", default="manual",
              type=click.Choice(["manual", "import", "derived", "external"]),
              show_default=True, help="Origin type of the variable.")
@click.option("--from", "derived_from", multiple=True, metavar="KEY",
              help="Keys this variable is derived from (repeatable).")
@click.option("--note", default=None, help="Optional note about the lineage.")
@click.option("--vault", default="vault.enc", show_default=True)
def lin_set(key, source, origin_type, derived_from, note, vault):
    """Record lineage for KEY with SOURCE origin."""
    try:
        entry = set_lineage(
            vault, key, source=source, origin_type=origin_type,
            derived_from=list(derived_from), note=note,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Lineage recorded for '{entry.key}' [{entry.origin_type}] from '{entry.source}'.")


@lineage_group.command("show")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def lin_show(key, vault):
    """Show lineage entry for KEY."""
    entry = get_lineage(vault, key)
    if entry is None:
        raise click.ClickException(f"No lineage recorded for '{key}'.")
    click.echo(f"Key:         {entry.key}")
    click.echo(f"Source:      {entry.source}")
    click.echo(f"Origin type: {entry.origin_type}")
    if entry.derived_from:
        click.echo(f"Derived from: {', '.join(entry.derived_from)}")
    if entry.note:
        click.echo(f"Note:        {entry.note}")
    click.echo(f"Recorded at: {entry.recorded_at}")


@lineage_group.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def lin_remove(key, vault):
    """Remove lineage entry for KEY."""
    if not remove_lineage(vault, key):
        raise click.ClickException(f"No lineage entry found for '{key}'.")
    click.echo(f"Lineage entry removed for '{key}'.")


@lineage_group.command("list")
@click.option("--vault", default="vault.enc", show_default=True)
def lin_list(vault):
    """List all lineage entries."""
    entries = list_lineage(vault)
    if not entries:
        click.echo("No lineage entries recorded.")
        return
    for e in entries:
        derived = f" <- {', '.join(e.derived_from)}" if e.derived_from else ""
        click.echo(f"  {e.key:30s} [{e.origin_type:8s}] {e.source}{derived}")


@lineage_group.command("derived")
@click.argument("source_key")
@click.option("--vault", default="vault.enc", show_default=True)
def lin_derived(source_key, vault):
    """List all keys derived from SOURCE_KEY."""
    keys = get_derived_keys(vault, source_key)
    if not keys:
        click.echo(f"No keys are derived from '{source_key}'.")
        return
    click.echo(f"Keys derived from '{source_key}':")
    for k in keys:
        click.echo(f"  {k}")
