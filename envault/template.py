"""Template rendering: substitute env vars from vault into template files."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")


class RenderError(Exception):
    pass


def render_template(template_text: str, variables: dict[str, str], strict: bool = True) -> str:
    """Replace {{VAR}} placeholders with values from variables dict."""
    missing: list[str] = []

    def replacer(m: re.Match) -> str:
        key = m.group(1)
        if key in variables:
            return variables[key]
        missing.append(key)
        return m.group(0)

    result = PLACEHOLDER_RE.sub(replacer, template_text)
    if strict and missing:
        raise RenderError(f"Missing variables in template: {', '.join(sorted(missing))}")
    return result


def render_file(
    template_path: Path,
    variables: dict[str, str],
    output_path: Optional[Path] = None,
    strict: bool = True,
) -> str:
    """Render a template file and optionally write output. Returns rendered text."""
    text = template_path.read_text(encoding="utf-8")
    rendered = render_template(text, variables, strict=strict)
    if output_path is not None:
        output_path.write_text(rendered, encoding="utf-8")
    return rendered


def find_placeholders(template_text: str) -> list[str]:
    """Return sorted unique placeholder names found in template."""
    return sorted(set(PLACEHOLDER_RE.findall(template_text)))
