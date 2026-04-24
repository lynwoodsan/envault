"""CLI commands for vault quota management."""

import click
from pathlib import Path

from envault.quota import (
    set_quota,
    remove_quota,
    get_quota,
    check_quota,
    format_quota_status,
)
from envault.vault import list_vars
from envault.cli import get_password


@click.group("quota", help="Manage variable quota for a vault.")
def quota_group():
    pass


@quota_group.command("set")
@click.argument("limit", type=int)
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
def quota_set(limit: int, vault: str):
    """Set the maximum number of variables allowed in the vault."""
    vault_file = Path(vault)
    try:
        set_quota(vault_file, limit)
        click.echo(f"Quota set to {limit} variable(s).")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@quota_group.command("remove")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
def quota_remove(vault: str):
    """Remove the quota limit from the vault."""
    vault_file = Path(vault)
    if remove_quota(vault_file):
        click.echo("Quota removed.")
    else:
        click.echo("No quota was set.")


@quota_group.command("show")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
def quota_show(vault: str):
    """Show the current quota configuration."""
    vault_file = Path(vault)
    limit = get_quota(vault_file)
    if limit is None:
        click.echo("No quota configured for this vault.")
    else:
        click.echo(f"Quota limit: {limit} variable(s)")


@quota_group.command("check")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
def quota_check(vault: str):
    """Check current variable count against the quota."""
    vault_file = Path(vault)
    password = get_password()
    try:
        variables = list_vars(vault_file, password)
    except Exception as exc:
        click.echo(f"Error reading vault: {exc}", err=True)
        raise SystemExit(1)

    status = check_quota(vault_file, len(variables))
    click.echo(format_quota_status(status))
    if status.exceeded:
        raise SystemExit(1)
