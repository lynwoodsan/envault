"""CLI commands for vault rollback."""

from __future__ import annotations

import click

from envault.cli import get_password
from envault.rollback import rollback_to_snapshot, list_rollback_points
from envault.snapshot import _snapshot_dir
from pathlib import Path


@click.group("rollback")
def rollback_group() -> None:
    """Rollback the vault to a previous snapshot."""


@rollback_group.command("list")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def rb_list(vault: str) -> None:
    """List available rollback points (snapshots)."""
    vault_path = Path(vault)
    points = list_rollback_points(vault_path)
    if not points:
        click.echo("No snapshots available.")
        return
    for entry in points:
        label_part = f"  [{entry['label']}]" if entry.get("label") else ""
        click.echo(f"{entry['id']}  {entry.get('created_at', '')}  vars={entry.get('var_count', '?')}{label_part}")


@rollback_group.command("run")
@click.argument("snapshot_id")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
@click.option("--actor", default="envault", show_default=True, help="Actor name for audit log.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def rb_run(snapshot_id: str, vault: str, actor: str, yes: bool) -> None:
    """Restore the vault to the state of SNAPSHOT_ID."""
    vault_path = Path(vault)
    if not yes:
        click.confirm(
            f"Roll back vault to snapshot '{snapshot_id}'? This will overwrite current state.",
            abort=True,
        )
    password = get_password()
    try:
        result = rollback_to_snapshot(vault_path, password, snapshot_id, actor=actor)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(f"Rollback failed: {exc}") from exc

    label_part = f" (label: {result.label})" if result.label else ""
    click.echo(
        f"Rolled back to snapshot {result.snapshot_id}{label_part}.\n"
        f"  Keys restored : {result.keys_restored}\n"
        f"  Keys removed  : {result.keys_removed}"
    )
