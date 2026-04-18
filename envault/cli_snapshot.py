"""CLI commands for vault snapshots."""
import click
from pathlib import Path
from envault.cli import get_password
from envault.snapshot import create_snapshot, list_snapshots, load_snapshot, diff_snapshot


@click.group("snapshot")
def snapshot_group():
    """Manage vault snapshots."""


@snapshot_group.command("create")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--label", default=None, help="Optional label for this snapshot.")
def snap_create(vault, label):
    """Create a snapshot of the current vault state."""
    password = get_password()
    path = create_snapshot(Path(vault), password, label=label)
    click.echo(f"Snapshot saved: {path.name}")


@snapshot_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
def snap_list(vault):
    """List available snapshots."""
    snaps = list_snapshots(Path(vault))
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        label = f" [{s['label']}]" if s["label"] else ""
        click.echo(f"{s['file']}{label}  ({s['count']} vars)")


@snapshot_group.command("diff")
@click.argument("filename")
@click.option("--vault", default=".envault", show_default=True)
def snap_diff(filename, vault):
    """Diff current vault against a snapshot."""
    password = get_password()
    entries = diff_snapshot(Path(vault), password, filename)
    if not entries:
        click.echo("No differences.")
        return
    for e in entries:
        status = e.get("status", "?")
        key = e.get("key", "")
        if status == "added":
            click.echo(f"+ {key}")
        elif status == "removed":
            click.echo(f"- {key}")
        elif status == "changed":
            click.echo(f"~ {key}")
