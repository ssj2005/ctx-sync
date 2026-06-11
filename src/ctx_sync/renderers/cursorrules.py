"""Renderer for .cursorrules (Cursor legacy) format."""

from __future__ import annotations

from ctx_sync.models import SyncContext, ToolFormat
from ctx_sync.renderers import BaseRenderer, register_renderer


@register_renderer
class CursorrulesRenderer(BaseRenderer):
    """Render SyncContext as a flat .cursorrules file.

    .cursorrules uses a simpler, flatter format than CLAUDE.md.
    No ## sections — just descriptive text and bullet points.
    """

    format = ToolFormat.CURSOR_RULES

    def render(self, ctx: SyncContext) -> str:
        lines: list[str] = []

        # Header
        if ctx.project_name:
            lines.append(f"# {ctx.project_name} - Cursor Rules")
        else:
            lines.append("# Cursor Rules")
        lines.append("")

        # Tech Stack
        if ctx.tech_stack or ctx.languages or ctx.frameworks:
            all_stack = ctx.tech_stack + ctx.languages + ctx.frameworks
            seen: set[str] = set()
            unique: list[str] = []
            for item in all_stack:
                if item.lower() not in seen:
                    seen.add(item.lower())
                    unique.append(item)
            lines.append("This project uses " + ", ".join(unique) + ".")
            lines.append("")

        # Commands as a code block
        if ctx.commands:
            lines.append("Commands:")
            for cmd in ctx.commands:
                desc = f" # {cmd.description}" if cmd.description else ""
                lines.append(f"  {cmd.command}{desc}")
            lines.append("")

        # Architecture
        if ctx.architecture:
            lines.append("Project structure:")
            for entry in ctx.architecture:
                lines.append(f"- {entry.path}: {entry.description}")
            lines.append("")

        # Conventions as bullet points (no ## headings)
        if ctx.conventions:
            lines.append("Coding conventions:")
            for conv in ctx.conventions:
                if conv.category and conv.category != "general":
                    lines.append(f"- **{conv.category}**: {conv.rule}")
                else:
                    lines.append(f"- {conv.rule}")
            lines.append("")

        # Git standards
        if ctx.git_standards:
            lines.append("Git standards:")
            for line in ctx.git_standards.strip().split("\n"):
                stripped = line.strip()
                if stripped:
                    lines.append(f"- {stripped.lstrip('- ').lstrip('* ')}")
            lines.append("")

        # Raw sections
        for key, value in ctx.raw_sections.items():
            if key.startswith("_"):
                continue
            lines.append(f"{key}:")
            for line in value.strip().split("\n"):
                stripped = line.strip()
                if stripped:
                    lines.append(f"- {stripped.lstrip('- ').lstrip('* ')}")
            lines.append("")

        return "\n".join(lines).strip() + "\n"
