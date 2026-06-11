"""Parser for .cursor/rules/*.mdc (Cursor current format) files."""

from __future__ import annotations

from pathlib import Path

from ctx_sync.models import SyncContext, ToolFormat
from ctx_sync.parsers import BaseParser, register_parser
from ctx_sync.parsers.claude_md import ClaudeMdParser


@register_parser
class CursorMdcParser(BaseParser):
    """Parse .cursor/rules/*.mdc files.

    MDC files have optional YAML frontmatter + markdown body.
    The body uses ## sections similar to CLAUDE.md.
    """

    format = ToolFormat.CURSOR_MDC

    def can_parse(self, path: Path) -> bool:
        return path.suffix == ".mdc" and ".cursor" in str(path)

    def parse(self, content: str, path: Path) -> SyncContext:
        # Strip YAML frontmatter if present
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()

        # Delegate body parsing to ClaudeMdParser
        claude_parser = ClaudeMdParser()
        ctx = claude_parser.parse(body, path)

        ctx.source_format = self.format
        ctx.source_path = str(path)

        # Store frontmatter as a raw section
        if content.startswith("---") and len(parts) >= 3:
            ctx.raw_sections["_frontmatter"] = parts[1].strip()

        return ctx
