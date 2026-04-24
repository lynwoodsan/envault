"""cli_expiry.py — CLI commands for managing variable expiry dates."""

import click
from datetime import timezone

from envault.expiry import (
    set_expiry,
    remove_expiry,
    get_expiry,
    list_expiry,
    get_expired_keys,
    is_expired,
)


@click.group(name="expiry")
def expiry_group():
    """Manage expiry dates for vault variables."""


@expiry_group.command("set")
@click.argument("key")
@click.argument("days", type=int)
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def exp_set(key, days, vault):
    """Set an expiry of DAYS days from now on KEY."""
    try:
        expiry = set_expiry(vault, key, days)
        click.echo(f"Expiry set for '{key}': {expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@expiry_group.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def exp_remove(key, vault):
    """Remove expiry from KEY."""
    removed = remove_expiry(vault, key)
    if removed:
        click.echo(f"Expiry removed for '{key}'.")
    else:
        click.echo(f"No expiry set for '{key}'.")


@expiry_group.command("get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def exp_get(key, vault):
    """Show expiry date for KEY."""
    expiry = get_expiry(vault, key)
    if expiry is None:
        click.echo(f"No expiry set for '{key}'.")
    else:
        expired = is_expired(vault, key)
        status = " [EXPIRED]" if expired else ""
        click.echo(f"{key}: {expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC{status}")


@expiry_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--expired-only", is_flag=True, default=False, help="Show only expired keys.")
def exp_list(vault, expired_only):
    """List all variables with expiry dates."""
    from datetime import datetime
    now = datetime.now(timezone.utc)
    entries = list_expiry(vault)
    if not entries:
        click.echo("No expiry dates set.")
        return
    for key, expiry in sorted(entries.items()):
        expired = now >= expiry
        if expired_only and not expired:
            continue
        status = " [EXPIRED]" if expired else ""
        click.echo(f"  {key}: {expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC{status}")


@expiry_group.command("purge")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--dry-run", is_flag=True, default=False)
def exp_purge(vault, dry_run):
    """Remove expiry records for all expired keys."""
    expired = get_expired_keys(vault)
    if not expired:
        click.echo("No expired keys found.")
        return
    for key in expired:
        if dry_run:
            click.echo(f"[dry-run] Would remove expiry for '{key}'.")
        else:
            remove_expiry(vault, key)
            click.echo(f"Removed expiry for '{key}'.")
