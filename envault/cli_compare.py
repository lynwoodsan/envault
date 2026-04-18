"""CLI commands for vault comparison."""
import click
from envault.compare import compare_vaults, compare_vault_dotenv, format_compare_report
from envault.cli import get_password


@click.group("compare")
def compare_group():
    """Compare vaults or vault vs .env file."""


@compare_group.command("vaults")
@click.argument("vault_a")
@click.argument("vault_b")
@click.option("--password-a", envvar="ENVAULT_PASSWORD_A", default=None, help="Password for vault A")
@click.option("--password-b", envvar="ENVAULT_PASSWORD_B", default=None, help="Password for vault B")
@click.option("--show-values", is_flag=True, default=False, help="Show differing values")
def cmp_vaults(vault_a, vault_b, password_a, password_b, show_values):
    """Compare two vault files."""
    if not password_a:
        password_a = get_password(f"Password for {vault_a}: ")
    if not password_b:
        password_b = get_password(f"Password for {vault_b}: ")
    try:
        results = compare_vaults(vault_a, password_a, vault_b, password_b)
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(format_compare_report(results, show_values=show_values))
    has_diff = any(r.status != "match" for r in results)
    raise SystemExit(1 if has_diff else 0)


@compare_group.command("dotenv")
@click.argument("vault_path")
@click.argument("dotenv_path")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None)
@click.option("--show-values", is_flag=True, default=False)
def cmp_dotenv(vault_path, dotenv_path, password, show_values):
    """Compare a vault against a .env file."""
    if not password:
        password = get_password()
    try:
        results = compare_vault_dotenv(vault_path, password, dotenv_path)
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(format_compare_report(results, show_values=show_values))
    has_diff = any(r.status != "match" for r in results)
    raise SystemExit(1 if has_diff else 0)
