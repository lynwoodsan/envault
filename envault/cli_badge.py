"""CLI commands for vault badge / health-card reporting."""

import click
from pathlib import Path

from .badge import generate_badge, format_badge_report
from .cli import get_password


@click.group("badge", help="Generate a health badge / summary card for the vault.")
def badge_group() -> None:
    pass


@badge_group.command("show")
@click.option("--vault", "vault_path", default=".envault", show_default=True,
              help="Path to the vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None,
              help="Vault password (or set ENVAULT_PASSWORD).")
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output raw JSON instead of the formatted report.")
def badge_show(vault_path: str, password: str | None, as_json: bool) -> None:
    """Display a health badge summarising the vault's overall quality."""
    import json as _json

    path = Path(vault_path)
    if not path.exists():
        click.echo(f"Vault not found: {vault_path}", err=True)
        raise SystemExit(1)

    pw = password or get_password(confirm=False)

    try:
        summary = generate_badge(path, pw)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error generating badge: {exc}", err=True)
        raise SystemExit(1)

    if as_json:
        click.echo(
            _json.dumps(
                {
                    "grade": summary.grade,
                    "avg_score": round(summary.avg_score, 2),
                    "total_vars": summary.total_vars,
                    "strong": summary.strong,
                    "moderate": summary.moderate,
                    "weak": summary.weak,
                    "unscored": summary.unscored,
                },
                indent=2,
            )
        )
    else:
        click.echo(format_badge_report(summary))


@badge_group.command("grade")
@click.option("--vault", "vault_path", default=".envault", show_default=True,
              help="Path to the vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None,
              help="Vault password (or set ENVAULT_PASSWORD).")
@click.option("--min-grade", "min_grade", default=None,
              type=click.Choice(["A", "B", "C", "D", "F"], case_sensitive=False),
              help="Exit with code 1 if the vault grade is below this threshold.")
def badge_grade(vault_path: str, password: str | None, min_grade: str | None) -> None:
    """Print the single-letter health grade for the vault.

    Useful in CI pipelines::

        envault badge grade --min-grade B
    """
    _grade_order = ["A", "B", "C", "D", "F"]

    path = Path(vault_path)
    if not path.exists():
        click.echo(f"Vault not found: {vault_path}", err=True)
        raise SystemExit(1)

    pw = password or get_password(confirm=False)

    try:
        summary = generate_badge(path, pw)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error generating badge: {exc}", err=True)
        raise SystemExit(1)

    click.echo(summary.grade)

    if min_grade:
        actual_idx = _grade_order.index(summary.grade.upper())
        threshold_idx = _grade_order.index(min_grade.upper())
        # Lower index == better grade; fail if actual is worse than threshold
        if actual_idx > threshold_idx:
            raise SystemExit(1)
