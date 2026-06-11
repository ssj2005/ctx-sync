"""Parser for .github/copilot-instructions.md (GitHub Copilot) files."""

from __future__ import annotations

from pathlib import Path

from ctx_sync.models import SyncContext, ToolFormat
from ctx_sync.parsers import BaseParser, register_parser
from ctx_sync.parsers.cursorrules import CursorrulesParser


@register_parser
class CopilotParser(BaseParser):
    """Parse GitHub Copilot instruction files.

    Copilot instructions are flat markdown, similar to .cursorrules.
    They rarely use ## sections — mostly bullet points and paragraphs.
    """

    format = ToolFormat.COPILOT

    def can_parse(self, path: Path) -> bool:
        return path.name == "copilot-instructions.md"

    def parse(self, content: str, path: Path) -> SyncContext:
        # Copilot format is similar to cursorrules — flat markdown
        cursor_parser = CursorrulesParser()
        ctx = cursor_parser.parse(content, path)

        ctx.source_format = self.format
        ctx.source_path = str(path)

        return ctx
