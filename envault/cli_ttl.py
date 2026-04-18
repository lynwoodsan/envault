"""CLI commands for managing variable TTLs."""

import click
from pathlib import Path
from datetime import datetime
from envault.ttl import set_ttl, remove_ttl, list_ttls, purge_expired, is_expired
from envault.cli import get_password


@click.group("ttl")
def ttl_group():
    """Manage expiry (TTL) for environment variables."""


@ttl_group.command("set")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--vault", default=".envault", show_default=True)
def ttl_set(key, seconds, vault):
    """Set a TTL (in seconds) for KEY."""
    vault_path = Path(vault)
    expires_at = set_ttl(vault_path, key, seconds)
    dt = datetime.fromtimestamp(expires_at).strftime("%Y-%m-%d %H:%M:%S")
    click.echo(f"TTL set for '{key}': expires at {dt}")


@ttl_group.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def ttl_remove(key, vault):
    """Remove TTL for KEY."""
    remove_ttl(Path(vault), key)
    click.echo(f"TTL removed for '{key}'.")


@ttl_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
def ttl_list(vault):
    """List all keys with TTLs."""
    ttls = list_ttls(Path(vault))
    if not ttls:
        click.echo("No TTLs configured.")
        return
    for key, exp in sorted(ttls.items()):
        dt = datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M:%S")
        status = " [EXPIRED]" if is_expired(Path(vault), key) else ""
        click.echo(f"{key}: {dt}{status}")


@ttl_group.command("purge")
@click.option("--vault", default=".envault", show_default=True)
def ttl_purge(vault):
    """Remove TTL records for all expired keys."""
    purged = purge_expired(Path(vault))
    if not purged:
        click.echo("Nothing to purge.")
    else:
        for key in purged:
            click.echo(f"Purged TTL for expired key: {key}")
