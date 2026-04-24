"""CLI commands for managing webhooks in envault."""

import click
from pathlib import Path

from envault.webhook import add_webhook, remove_webhook, list_webhooks


@click.group(name="webhook")
def webhook_group():
    """Manage webhook notifications for vault events."""


@webhook_group.command("add")
@click.argument("name")
@click.argument("url")
@click.option(
    "--event",
    "events",
    multiple=True,
    help="Event type to filter on (e.g. set, delete, rotate). Repeatable.",
)
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
def wh_add(name, url, events, vault):
    """Register a webhook URL under NAME."""
    vault_path = Path(vault)
    add_webhook(vault_path, name, url, list(events) if events else [])
    if events:
        click.echo(f"Webhook '{name}' registered for events: {', '.join(events)}")
    else:
        click.echo(f"Webhook '{name}' registered for all events.")


@webhook_group.command("remove")
@click.argument("name")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
def wh_remove(name, vault):
    """Unregister a webhook by NAME."""
    vault_path = Path(vault)
    removed = remove_webhook(vault_path, name)
    if removed:
        click.echo(f"Webhook '{name}' removed.")
    else:
        click.echo(f"No webhook named '{name}' found.", err=True)
        raise SystemExit(1)


@webhook_group.command("list")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
def wh_list(vault):
    """List all registered webhooks."""
    vault_path = Path(vault)
    hooks = list_webhooks(vault_path)
    if not hooks:
        click.echo("No webhooks registered.")
        return
    for name, cfg in hooks.items():
        events_str = ", ".join(cfg["events"]) if cfg["events"] else "all"
        click.echo(f"  {name:20s}  {cfg['url']}  [{events_str}]")
