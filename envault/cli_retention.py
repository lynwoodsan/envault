"""CLI commands for retention policy management."""
import click
from envault.retention import (
    set_retention,
    remove_retention,
    get_retention,
    list_retention,
    get_due_keys,
)
from envault.cli import get_password


@click.group("retention", help="Manage variable retention policies.")
def retention_group():
    pass


@retention_group.command("set")
@click.argument("key")
@click.option("--days", required=True, type=int, help="Retention period in days.")
@click.option(
    "--action",
    default="warn",
    type=click.Choice(["warn", "archive", "delete"]),
    show_default=True,
    help="Action to take when retention period elapses.",
)
@click.option("--vault", default="vault.enc", show_default=True)
def ret_set(key, days, action, vault):
    """Set a retention policy for KEY."""
    try:
        entry = set_retention(vault, key, days, action=action)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Retention set for '{key}': {days} day(s), action={action}, due={entry['due_at']}")


@retention_group.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def ret_remove(key, vault):
    """Remove the retention policy for KEY."""
    if remove_retention(vault, key):
        click.echo(f"Retention policy removed for '{key}'.")
    else:
        raise click.ClickException(f"No retention policy found for '{key}'.")


@retention_group.command("show")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def ret_show(key, vault):
    """Show the retention policy for KEY."""
    entry = get_retention(vault, key)
    if not entry:
        raise click.ClickException(f"No retention policy for '{key}'.")
    click.echo(f"Key:    {entry['key']}")
    click.echo(f"Days:   {entry['days']}")
    click.echo(f"Action: {entry['action']}")
    click.echo(f"Set at: {entry['set_at']}")
    click.echo(f"Due at: {entry['due_at']}")


@retention_group.command("list")
@click.option("--vault", default="vault.enc", show_default=True)
def ret_list(vault):
    """List all retention policies."""
    entries = list_retention(vault)
    if not entries:
        click.echo("No retention policies defined.")
        return
    for e in entries:
        click.echo(f"{e['key']:<30} {e['days']:>5}d  action={e['action']}  due={e['due_at']}")


@retention_group.command("due")
@click.option("--vault", default="vault.enc", show_default=True)
def ret_due(vault):
    """List keys whose retention period has elapsed."""
    entries = get_due_keys(vault)
    if not entries:
        click.echo("No keys past their retention date.")
        return
    for e in entries:
        click.echo(f"{e['key']:<30} action={e['action']}  due={e['due_at']}")
