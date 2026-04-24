"""CLI commands for managing vault policies."""

import click
from pathlib import Path
from envault.policy import PolicyRule, add_rule, remove_rule, load_policy, check_policy, format_policy_report
from envault.vault import load_vault
from envault.cli import get_password


@click.group("policy")
def policy_group():
    """Manage vault variable policies."""


@policy_group.command("add")
@click.argument("name")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--required-prefix", default=None, help="Keys must start with this prefix.")
@click.option("--forbidden-pattern", default=None, help="Values must not match this regex.")
@click.option("--max-length", default=None, type=int, help="Maximum value length.")
def pol_add(name, vault, required_prefix, forbidden_pattern, max_length):
    """Add or update a policy rule."""
    vault_path = Path(vault)
    rule = PolicyRule(
        name=name,
        required_prefix=required_prefix,
        forbidden_pattern=forbidden_pattern,
        max_length=max_length,
    )
    add_rule(vault_path, rule)
    click.echo(f"Policy rule '{name}' saved.")


@policy_group.command("remove")
@click.argument("name")
@click.option("--vault", default=".envault", show_default=True)
def pol_remove(name, vault):
    """Remove a policy rule by name."""
    vault_path = Path(vault)
    if remove_rule(vault_path, name):
        click.echo(f"Policy rule '{name}' removed.")
    else:
        click.echo(f"Rule '{name}' not found.", err=True)
        raise SystemExit(1)


@policy_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
def pol_list(vault):
    """List all policy rules."""
    vault_path = Path(vault)
    rules = load_policy(vault_path)
    if not rules:
        click.echo("No policy rules defined.")
        return
    for r in rules:
        parts = [f"[{r.name}]"]
        if r.required_prefix:
            parts.append(f"prefix={r.required_prefix}")
        if r.forbidden_pattern:
            parts.append(f"forbidden={r.forbidden_pattern}")
        if r.max_length:
            parts.append(f"max_len={r.max_length}")
        click.echo("  " + "  ".join(parts))


@policy_group.command("check")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None)
def pol_check(vault, password):
    """Check current vault variables against all policy rules."""
    vault_path = Path(vault)
    password = get_password(password)
    variables = load_vault(vault_path, password)
    violations = check_policy(vault_path, variables)
    report = format_policy_report(violations)
    click.echo(report)
    if violations:
        raise SystemExit(1)
