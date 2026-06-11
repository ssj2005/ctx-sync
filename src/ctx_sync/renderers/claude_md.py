"""Renderer for CLAUDE.md (Claude Code) format."""

from __future__ import annotations

from ctx_sync.models import SyncContext, ToolFormat
from ctx_sync.renderers import BaseRenderer, register_renderer


@register_renderer
class ClaudeMdRenderer(BaseRenderer):
    format = ToolFormat.CLAUDE_MD

    def render(self, ctx: SyncContext) -> str:
        lines: list[str] = []

        # Title and description
        title = ctx.project_name or "Project"
        lines.append(f"# {title}")
        lines.append("")

        if ctx.description:
            lines.append(ctx.description)
            lines.append("")

        # Stack
        if ctx.tech_stack or ctx.languages or ctx.frameworks:
            all_stack = ctx.tech_stack + ctx.languages + ctx.frameworks
            # Deduplicate while preserving order
            seen: set[str] = set()
            unique: list[str] = []
            for item in all_stack:
                if item.lower() not in seen:
                    seen.add(item.lower())
                    unique.append(item)
            lines.append("## Stack")
            lines.append(" / ".join(unique))
            lines.append("")

        # Commands
        if ctx.commands:
            lines.append("## Commands")
            for cmd in ctx.commands:
                desc = f" — {cmd.description}" if cmd.description else ""
                lines.append(f"- `{cmd.command}`{desc}")
            lines.append("")

        # Architecture
        if ctx.architecture:
            lines.append("## Architecture")
            for entry in ctx.architecture:
                lines.append(f"- `{entry.path}` — {entry.description}")
            lines.append("")

        # Conventions
        if ctx.conventions:
            lines.append("## Conventions")
            for conv in ctx.conventions:
                if conv.category and conv.category != "general":
                    lines.append(f"- **{conv.category}**: {conv.rule}")
                else:
                    lines.append(f"- {conv.rule}")
            lines.append("")

        # Git standards
        if ctx.git_standards:
            lines.append("## Git")
            lines.append(ctx.git_standards)
            lines.append("")

        # Raw sections (preserved unmapped content)
        for key, value in ctx.raw_sections.items():
            if key.startswith("_"):
                continue  # Skip internal metadata
            lines.append(f"## {key}")
            lines.append(value)
            lines.append("")

        return "\n".join(lines).strip() + "\n"
