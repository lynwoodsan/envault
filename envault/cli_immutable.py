"""CLI commands for immutable variable protection."""

import click
from envault.immutable import (
    mark_immutable,
    unmark_immutable,
    is_immutable,
    list_immutable,
)


@click.group(name="immutable", help="Protect variables from modification or deletion.")
def immutable_group():
    pass


@immutable_group.command("lock")
@click.argument("key")
@click.option("--reason", "-r", default=None, help="Reason for locking this key.")
@click.option("--vault", "vault_file", default="vault.enc", show_default=True)
def imm_lock(key, reason, vault_file):
    """Mark KEY as immutable."""
    entry = mark_immutable(vault_file, key, reason=reason)
    msg = f"🔒 '{key}' is now immutable."
    if reason:
        msg += f" Reason: {reason}"
    click.echo(msg)


@immutable_group.command("unlock")
@click.argument("key")
@click.option("--vault", "vault_file", default="vault.enc", show_default=True)
def imm_unlock(key, vault_file):
    """Remove immutability from KEY."""
    removed = unmark_immutable(vault_file, key)
    if removed:
        click.echo(f"🔓 '{key}' is no longer immutable.")
    else:
        click.echo(f"Key '{key}' was not immutable.", err=True)
        raise SystemExit(1)


@immutable_group.command("check")
@click.argument("key")
@click.option("--vault", "vault_file", default="vault.enc", show_default=True)
def imm_check(key, vault_file):
    """Check whether KEY is immutable."""
    if is_immutable(vault_file, key):
        click.echo(f"🔒 '{key}' is immutable.")
    else:
        click.echo(f"✅ '{key}' is not immutable.")


@immutable_group.command("list")
@click.option("--vault", "vault_file", default="vault.enc", show_default=True)
def imm_list(vault_file):
    """List all immutable variables."""
    entries = list_immutable(vault_file)
    if not entries:
        click.echo("No immutable variables.")
        return
    for e in entries:
        reason = e.get("reason") or ""
        line = f"  🔒 {e['key']}"
        if reason:
            line += f"  ({reason})"
        click.echo(line)
