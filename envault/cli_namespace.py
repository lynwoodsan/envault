"""CLI commands for namespace management."""

import click
from pathlib import Path
from envault.namespace import (
    assign_namespace,
    unassign_namespace,
    get_namespace_keys,
    get_key_namespaces,
    list_namespaces,
    delete_namespace,
)


@click.group("namespace")
def namespace_group():
    """Manage namespaces for grouping environment variables."""


@namespace_group.command("assign")
@click.argument("key")
@click.argument("namespace")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def ns_assign(key, namespace, vault):
    """Assign a KEY to a NAMESPACE."""
    assign_namespace(Path(vault), key, namespace)
    click.echo(f"Assigned '{key}' to namespace '{namespace}'.")


@namespace_group.command("unassign")
@click.argument("key")
@click.argument("namespace")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def ns_unassign(key, namespace, vault):
    """Remove a KEY from a NAMESPACE."""
    removed = unassign_namespace(Path(vault), key, namespace)
    if removed:
        click.echo(f"Removed '{key}' from namespace '{namespace}'.")
    else:
        click.echo(f"Key '{key}' was not in namespace '{namespace}'.")
        raise SystemExit(1)


@namespace_group.command("list")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def ns_list(vault):
    """List all namespaces."""
    namespaces = list_namespaces(Path(vault))
    if not namespaces:
        click.echo("No namespaces defined.")
        return
    for ns in namespaces:
        keys = get_namespace_keys(Path(vault), ns)
        click.echo(f"{ns}: {', '.join(keys)}")


@namespace_group.command("show")
@click.argument("namespace")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def ns_show(namespace, vault):
    """Show all keys in a NAMESPACE."""
    keys = get_namespace_keys(Path(vault), namespace)
    if not keys:
        click.echo(f"Namespace '{namespace}' is empty or does not exist.")
        return
    for key in keys:
        click.echo(key)


@namespace_group.command("which")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def ns_which(key, vault):
    """Show which namespaces a KEY belongs to."""
    namespaces = get_key_namespaces(Path(vault), key)
    if not namespaces:
        click.echo(f"'{key}' is not assigned to any namespace.")
        return
    for ns in namespaces:
        click.echo(ns)


@namespace_group.command("delete")
@click.argument("namespace")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def ns_delete(namespace, vault):
    """Delete an entire NAMESPACE (keys are not deleted from vault)."""
    deleted = delete_namespace(Path(vault), namespace)
    if deleted:
        click.echo(f"Namespace '{namespace}' deleted.")
    else:
        click.echo(f"Namespace '{namespace}' not found.")
        raise SystemExit(1)
