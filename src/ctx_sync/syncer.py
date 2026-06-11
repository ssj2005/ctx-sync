"""Sync engine: parse source config → render to target formats."""

from __future__ import annotations

from pathlib import Path

from ctx_sync.models import SyncContext, ToolFormat
from ctx_sync.parsers import get_parser


def sync(
    source_path: Path,
    target_formats: list[ToolFormat],
) -> dict[ToolFormat, str]:
    """Read a source config file and render it into all target formats.

    Returns {ToolFormat: rendered_content_string}.
    """
    # Lazy import to avoid circular dependency at module level
    from ctx_sync.renderers import get_renderer

    # Auto-detect source format
    detected_fmt: ToolFormat | None = None
    for fmt in ToolFormat:
        parser = get_parser(fmt)
        if parser.can_parse(source_path):
            detected_fmt = fmt
            break

    if detected_fmt is None:
        raise ValueError(f"Cannot detect format of: {source_path}")

    # Parse
    parser = get_parser(detected_fmt)
    content = source_path.read_text(encoding="utf-8")
    ctx = parser.parse(content, source_path)

    # Render to each target format
    results: dict[ToolFormat, str] = {}
    for target_fmt in target_formats:
        if target_fmt == detected_fmt:
            continue  # Skip rendering to same format
        renderer = get_renderer(target_fmt)
        results[target_fmt] = renderer.render(ctx)

    return results


def get_output_path(fmt: ToolFormat, project_root: Path) -> Path:
    """Return the canonical file path for a given format in a project."""
    mapping: dict[ToolFormat, str] = {
        ToolFormat.CLAUDE_MD: "CLAUDE.md",
        ToolFormat.AGENTS_MD: "AGENTS.md",
        ToolFormat.CURSOR_RULES: ".cursorrules",
        ToolFormat.COPILOT: ".github/copilot-instructions.md",
    }
    if fmt in mapping:
        return project_root / mapping[fmt]
    raise ValueError(f"No default output path for format: {fmt.value}")
