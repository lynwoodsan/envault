"""CLI commands for variable strength scoring."""
import click
from pathlib import Path

from envault.cli import get_password
from envault.scoring import score_vault, score_value, format_score_report


@click.group(name="score")
def score_group():
    """Score the strength of stored secrets."""


@score_group.command("run")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, help="Vault password")
@click.option("--min-grade", default=None, help="Exit non-zero if any key is below this grade (A-F)")
def score_run(vault, password, min_grade):
    """Score all variables and print a report."""
    vault_path = Path(vault)
    if not vault_path.exists():
        click.echo("Vault not found.", err=True)
        raise SystemExit(1)
    pw = password or get_password(confirm=False)
    try:
        results = score_vault(vault_path, pw)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(format_score_report(results))

    if min_grade:
        order = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}
        threshold = order.get(min_grade.upper(), 0)
        failing = [r for r in results if order.get(r.grade, 0) < threshold]
        if failing:
            click.echo(
                f"\n{len(failing)} variable(s) below grade {min_grade.upper()}.", err=True
            )
            raise SystemExit(1)


@score_group.command("check")
@click.argument("key")
@click.argument("value")
def score_check(key, value):
    """Score a single KEY=VALUE pair without touching the vault."""
    result = score_value(key, value)
    click.echo(f"[{result.grade}] {key}: {result.score}/100")
    for issue in result.issues:
        click.echo(f"  - {issue}")
    if result.grade in ("D", "F"):
        raise SystemExit(1)
