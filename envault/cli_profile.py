"""CLI commands for profile management."""
import click
from envault.cli import get_password
from envault.vault import list_vars
from envault.profile import (
    create_profile, delete_profile, assign_key,
    unassign_key, get_profile_keys, list_profiles
)


@click.group("profile")
def profile_group():
    """Manage named variable profiles (dev, staging, prod, …)."""


@profile_group.command("create")
@click.argument("name")
@click.option("--vault", default=".envault", show_default=True)
def prof_create(name, vault):
    """Create a new profile."""
    create_profile(vault, name)
    click.echo(f"Profile '{name}' created.")


@profile_group.command("delete")
@click.argument("name")
@click.option("--vault", default=".envault", show_default=True)
def prof_delete(name, vault):
    """Delete a profile."""
    if delete_profile(vault, name):
        click.echo(f"Profile '{name}' deleted.")
    else:
        click.echo(f"Profile '{name}' not found.", err=True)
        raise SystemExit(1)


@profile_group.command("assign")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def prof_assign(profile, key, vault):
    """Assign a key to a profile."""
    assign_key(vault, profile, key)
    click.echo(f"Key '{key}' assigned to profile '{profile}'.")


@profile_group.command("unassign")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def prof_unassign(profile, key, vault):
    """Remove a key from a profile."""
    if unassign_key(vault, profile, key):
        click.echo(f"Key '{key}' removed from profile '{profile}'.")
    else:
        click.echo(f"Key '{key}' not in profile '{profile}'.", err=True)
        raise SystemExit(1)


@profile_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
def prof_list(vault):
    """List all profiles and their keys."""
    profiles = list_profiles(vault)
    if not profiles:
        click.echo("No profiles defined.")
        return
    for name, keys in profiles.items():
        key_str = ", ".join(keys) if keys else "(empty)"
        click.echo(f"{name}: {key_str}")


@profile_group.command("show")
@click.argument("name")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", default=None, hide_input=True)
def prof_show(name, vault, password):
    """Show decrypted values for all keys in a profile."""
    keys = get_profile_keys(vault, name)
    if keys is None:
        click.echo(f"Profile '{name}' not found.", err=True)
        raise SystemExit(1)
    if not keys:
        click.echo("Profile is empty.")
        return
    password = password or get_password()
    all_vars = list_vars(vault, password)
    for k in keys:
        val = all_vars.get(k, "<not set>")
        click.echo(f"{k}={val}")
