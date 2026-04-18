"""CLI commands for pinning/unpinning vault variables."""
import click
from pathlib import Path
from envault.pin import pin_var, unpin_var, is_pinned, list_pins


@click.group("pin")
def pin_group():
    """Pin variables to prevent accidental overwrites."""


@pin_group.command("add")
@click.argument("key")
@click.option("--reason", "-r", default="", help="Reason for pinning")
@click.option("--vault", default="vault.enc", show_default=True)
def pin_add(key, reason, vault):
    """Pin a variable KEY."""
    vf = Path(vault)
    pin_var(vf, key, reason=reason)
    msg = f"Pinned '{key}'."
    if reason:
        msg += f" Reason: {reason}"
    click.echo(msg)


@pin_group.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def pin_remove(key, vault):
    """Unpin a variable KEY."""
    vf = Path(vault)
    if unpin_var(vf, key):
        click.echo(f"Unpinned '{key}'.")
    else:
        click.echo(f"'{key}' was not pinned.", err=True)
        raise SystemExit(1)


@pin_group.command("list")
@click.option("--vault", default="vault.enc", show_default=True)
def pin_list(vault):
    """List all pinned variables."""
    vf = Path(vault)
    pins = list_pins(vf)
    if not pins:
        click.echo("No pinned variables.")
        return
    for entry in pins:
        line = entry["key"]
        if entry["reason"]:
            line += f"  # {entry['reason']}"
        click.echo(line)


@pin_group.command("check")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def pin_check(key, vault):
    """Check if KEY is pinned."""
    vf = Path(vault)
    if is_pinned(vf, key):
        click.echo(f"'{key}' is pinned.")
    else:
        click.echo(f"'{key}' is not pinned.")
