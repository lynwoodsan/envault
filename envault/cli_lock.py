"""CLI commands for vault and key locking."""

from __future__ import annotations

import click
from pathlib import Path
from envault.lock import (
    lock_vault,
    unlock_vault,
    lock_key,
    unlock_key,
    is_vault_locked,
    list_locked_keys,
    get_vault_lock_reason,
)


@click.group("lock")
def lock_group():
    """Manage vault and key locks."""


@lock_group.command("vault")
@click.option("--reason", default="", help="Reason for locking the vault.")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def lk_vault(reason, vault_path):
    """Lock the entire vault against writes."""
    p = Path(vault_path)
    lock_vault(p, reason=reason or None)
    msg = "Vault locked."
    if reason:
        msg += f" Reason: {reason}"
    click.echo(msg)


@lock_group.command("unlock-vault")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def lk_unlock_vault(vault_path):
    """Unlock the entire vault."""
    p = Path(vault_path)
    unlock_vault(p)
    click.echo("Vault unlocked.")


@lock_group.command("key")
@click.argument("key")
@click.option("--reason", default="", help="Reason for locking this key.")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def lk_key(key, reason, vault_path):
    """Lock a specific KEY against modification."""
    p = Path(vault_path)
    lock_key(p, key, reason=reason or None)
    msg = f"Key '{key}' locked."
    if reason:
        msg += f" Reason: {reason}"
    click.echo(msg)


@lock_group.command("unlock-key")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def lk_unlock_key(key, vault_path):
    """Unlock a specific KEY."""
    p = Path(vault_path)
    ok = unlock_key(p, key)
    if ok:
        click.echo(f"Key '{key}' unlocked.")
    else:
        click.echo(f"Key '{key}' was not locked.", err=True)
        raise SystemExit(1)


@lock_group.command("status")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def lk_status(vault_path):
    """Show lock status for vault and all locked keys."""
    p = Path(vault_path)
    vault_locked = is_vault_locked(p)
    reason = get_vault_lock_reason(p)
    status = "LOCKED" if vault_locked else "unlocked"
    click.echo(f"Vault: {status}" + (f" ({reason})" if reason else ""))
    locked_keys = list_locked_keys(p)
    if locked_keys:
        click.echo("Locked keys:")
        for k, r in sorted(locked_keys.items()):
            click.echo(f"  {k}" + (f" — {r}" if r else ""))
    else:
        click.echo("No keys locked.")
