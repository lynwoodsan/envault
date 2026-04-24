"""CLI commands for managing key reminders."""

import click
from pathlib import Path
from datetime import datetime

from envault.reminder import (
    set_reminder,
    remove_reminder,
    list_reminders,
    due_reminders,
)


@click.group("reminder", help="Manage rotation/review reminders for vault keys.")
def reminder_group():
    pass


@reminder_group.command("set")
@click.argument("key")
@click.option("--days", "-d", required=True, type=int, help="Days until reminder is due.")
@click.option("--note", "-n", default="", help="Optional note for the reminder.")
@click.option("--vault", default="vault.env", show_default=True, help="Path to vault file.")
def rem_set(key, days, note, vault):
    """Schedule a reminder for KEY in DAYS days."""
    try:
        due = set_reminder(Path(vault), key, days, note)
        click.echo(f"Reminder set for '{key}' — due {due.strftime('%Y-%m-%d %H:%M')} UTC")
    except ValueError as e:
        raise click.ClickException(str(e))


@reminder_group.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.env", show_default=True, help="Path to vault file.")
def rem_remove(key, vault):
    """Remove the reminder for KEY."""
    removed = remove_reminder(Path(vault), key)
    if removed:
        click.echo(f"Reminder for '{key}' removed.")
    else:
        click.echo(f"No reminder found for '{key}'.")


@reminder_group.command("list")
@click.option("--vault", default="vault.env", show_default=True, help="Path to vault file.")
def rem_list(vault):
    """List all scheduled reminders."""
    reminders = list_reminders(Path(vault))
    if not reminders:
        click.echo("No reminders set.")
        return
    for r in reminders:
        note_str = f"  ({r['note']})" if r["note"] else ""
        click.echo(f"{r['key']:<30} due {r['due'][:10]}{note_str}")


@reminder_group.command("due")
@click.option("--vault", default="vault.env", show_default=True, help="Path to vault file.")
def rem_due(vault):
    """Show reminders that are past due."""
    overdue = due_reminders(Path(vault))
    if not overdue:
        click.echo("No overdue reminders.")
        return
    click.echo(f"{'KEY':<30} {'DUE':<20} NOTE")
    click.echo("-" * 65)
    for r in overdue:
        click.echo(f"{r['key']:<30} {r['due'][:16]:<20} {r['note']}")
    raise SystemExit(1)
