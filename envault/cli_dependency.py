"""CLI commands for managing variable dependencies in envault."""

import click
from pathlib import Path
from envault.dependency import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    validate_dependencies,
)


@click.group("dep")
def dependency_group():
    """Manage variable dependencies."""
    pass


@dependency_group.command("add")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to the vault file.")
def dep_add(key, depends_on, vault_path):
    """Declare that KEY depends on DEPENDS_ON.

    Example: envault dep add DATABASE_URL DB_HOST
    """
    path = Path(vault_path)
    add_dependency(path, key, depends_on)
    click.echo(f"Added dependency: {key} -> {depends_on}")


@dependency_group.command("remove")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to the vault file.")
def dep_remove(key, depends_on, vault_path):
    """Remove the dependency of KEY on DEPENDS_ON."""
    path = Path(vault_path)
    removed = remove_dependency(path, key, depends_on)
    if removed:
        click.echo(f"Removed dependency: {key} -> {depends_on}")
    else:
        click.echo(f"No such dependency: {key} -> {depends_on}", err=True)
        raise SystemExit(1)


@dependency_group.command("list")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to the vault file.")
def dep_list(key, vault_path):
    """List all variables that KEY depends on."""
    path = Path(vault_path)
    deps = get_dependencies(path, key)
    if not deps:
        click.echo(f"{key} has no declared dependencies.")
    else:
        click.echo(f"Dependencies of {key}:")
        for dep in sorted(deps):
            click.echo(f"  {dep}")


@dependency_group.command("dependents")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to the vault file.")
def dep_dependents(key, vault_path):
    """List all variables that depend on KEY (reverse lookup)."""
    path = Path(vault_path)
    dependents = get_dependents(path, key)
    if not dependents:
        click.echo(f"No variables depend on {key}.")
    else:
        click.echo(f"Variables that depend on {key}:")
        for dep in sorted(dependents):
            click.echo(f"  {dep}")


@dependency_group.command("validate")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to the vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def dep_validate(vault_path, password):
    """Check that all declared dependency keys actually exist in the vault.

    Exits with code 1 if any dependencies reference missing keys.
    """
    path = Path(vault_path)
    issues = validate_dependencies(path, password)
    if not issues:
        click.echo("All dependencies are satisfied.")
    else:
        click.echo("Unsatisfied dependencies:", err=True)
        for key, missing in issues.items():
            for m in missing:
                click.echo(f"  {key} -> {m} (missing)", err=True)
        raise SystemExit(1)
