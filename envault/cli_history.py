"""CLI commands for viewing variable change history."""
import click
from envault.cli import get_password
from envault.history import get_history, format_history, history_summary


@click.group("history")
def history_group():
    """Commands for viewing variable history."""


@history_group.command("show")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None)
def hist_show(key, vault, password):
    """Show change history for a specific KEY."""
    password = get_password(password)
    entries = get_history(vault, key)
    click.echo(format_history(entries))


@history_group.command("summary")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None)
@click.option("--sort", "sort_by", type=click.Choice(["key", "count"]), default="key", show_default=True)
def hist_summary(vault, password, sort_by):
    """Show event count summary for all variables."""
    password = get_password(password)
    summary = history_summary(vault, password)
    if not summary:
        click.echo("No variables found.")
        return
    items = sorted(
        summary.items(),
        key=(lambda x: x[0]) if sort_by == "key" else (lambda x: -x[1]),
    )
    for key, count in items:
        click.echo(f"{key}: {count} event(s)")
