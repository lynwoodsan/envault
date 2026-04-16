import sys
import click
from envault.vault import load_vault, save_vault, set_var, delete_var, list_vars
from envault.export import export_dotenv, import_dotenv


def get_password(ctx):
    password = ctx.obj.get("password")
    if not password:
        password = click.prompt("Vault password", hide_input=True)
        ctx.obj["password"] = password
    return password


@click.group()
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, help="Vault password.")
@click.pass_context
def cli(ctx, vault, password):
    """envault — encrypted project environment variable manager."""
    ctx.ensure_object(dict)
    ctx.obj["vault_path"] = vault
    ctx.obj["password"] = password


@cli.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx, key, value):
    """Set an environment variable."""
    password = get_password(ctx)
    vault_path = ctx.obj["vault_path"]
    vault = load_vault(vault_path, password)
    set_var(vault, key, value)
    save_vault(vault_path, password, vault)
    click.echo(f"Set {key}")


@cli.command()
@click.argument("key")
@click.pass_context
def delete(ctx, key):
    """Delete an environment variable."""
    password = get_password(ctx)
    vault_path = ctx.obj["vault_path"]
    vault = load_vault(vault_path, password)
    delete_var(vault, key)
    save_vault(vault_path, password, vault)
    click.echo(f"Deleted {key}")


@cli.command(name="list")
@click.pass_context
def list_cmd(ctx):
    """List all environment variable keys."""
    password = get_password(ctx)
    vault_path = ctx.obj["vault_path"]
    vault = load_vault(vault_path, password)
    keys = list_vars(vault)
    if not keys:
        click.echo("No variables stored.")
    for key in keys:
        click.echo(key)


@cli.command()
@click.argument("output", default=".env")
@click.pass_context
def export(ctx, output):
    """Export variables to a .env file."""
    password = get_password(ctx)
    vault_path = ctx.obj["vault_path"]
    vault = load_vault(vault_path, password)
    export_dotenv(vault, output)
    click.echo(f"Exported to {output}")


@cli.command(name="import")
@click.argument("input", default=".env")
@click.pass_context
def import_cmd(ctx, input):
    """Import variables from a .env file."""
    password = get_password(ctx)
    vault_path = ctx.obj["vault_path"]
    vault = load_vault(vault_path, password)
    count = import_dotenv(vault, input)
    save_vault(vault_path, password, vault)
    click.echo(f"Imported {count} variable(s) from {input}")


if __name__ == "__main__":
    cli()
