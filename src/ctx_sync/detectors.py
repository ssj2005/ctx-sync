"""Detect existing AI config files in a project directory."""

from __future__ import annotations

from pathlib import Path

from ctx_sync.models import ToolFormat

# Maps each format to the file(s)/directory it uses
DETECTION_RULES: dict[ToolFormat, list[str]] = {
    ToolFormat.CLAUDE_MD: ["CLAUDE.md"],
    ToolFormat.AGENTS_MD: ["AGENTS.md"],
    ToolFormat.CURSOR_RULES: [".cursorrules"],
    ToolFormat.CURSOR_MDC: [".cursor/rules/"],
    ToolFormat.COPILOT: [".github/copilot-instructions.md"],
}


def detect_configs(project_root: Path) -> list[tuple[ToolFormat, Path]]:
    """Scan a project directory for AI config files.

    Returns a list of (format, path) tuples for every config file found.
    """
    if not project_root.is_dir():
        return []

    found: list[tuple[ToolFormat, Path]] = []

    for fmt, relative_paths in DETECTION_RULES.items():
        for relative in relative_paths:
            full_path = project_root / relative

            if relative.endswith("/"):
                # Directory-based format (e.g. .cursor/rules/)
                if full_path.is_dir():
                    for mdc_file in sorted(full_path.glob("*.mdc")):
                        found.append((fmt, mdc_file))
            else:
                if full_path.is_file():
                    found.append((fmt, full_path))

    return found
