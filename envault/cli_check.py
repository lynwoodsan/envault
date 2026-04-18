"""CLI commands for environment variable schema checking."""
import json
from pathlib import Path

import click

from envault.cli import get_password
from envault.vault import list_vars
from envault.env_check import load_rules, check_vars, format_check_report


@click.group("check")
def check_group():
    """Validate vault variables against a schema."""


@check_group.command("run")
@click.argument("schema", type=click.Path(exists=True))
@click.option("--vault", default=".envault", show_default=True)
@click.option("--fail-fast", is_flag=True, default=False)
def check_run(schema, vault, fail_fast):
    """Run checks defined in a JSON schema file against the vault."""
    password = get_password()
    vault_path = Path(vault)

    try:
        variables = list_vars(vault_path, password)
    except Exception as e:
        raise click.ClickException(str(e))

    with open(schema) as f:
        rules_data = json.load(f)

    rules = load_rules(rules_data)
    results = check_vars(variables, rules)
    report = format_check_report(results)
    click.echo(report)

    issues = [r for r in results if r.status != "ok"]
    if issues:
        raise click.exceptions.Exit(1)


@check_group.command("init-schema")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--output", default="envault-schema.json", show_default=True)
def check_init_schema(vault, output):
    """Generate a starter schema from current vault keys."""
    password = get_password()
    vault_path = Path(vault)

    try:
        variables = list_vars(vault_path, password)
    except Exception as e:
        raise click.ClickException(str(e))

    rules = [{"key": k, "required": True, "pattern": None, "min_length": 0, "description": ""}
             for k in sorted(variables)]

    with open(output, "w") as f:
        json.dump(rules, f, indent=2)

    click.echo(f"Schema written to {output} ({len(rules)} keys).")
