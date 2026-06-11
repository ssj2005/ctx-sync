"""Parser for AGENTS.md (OpenCode / Codex) files."""

from __future__ import annotations

from pathlib import Path

from ctx_sync.models import SyncContext, ToolFormat
from ctx_sync.parsers import BaseParser, register_parser
from ctx_sync.parsers.claude_md import ClaudeMdParser


@register_parser
class AgentsMdParser(BaseParser):
    """AGENTS.md is structurally very similar to CLAUDE.md.

    We reuse ClaudeMdParser for the heavy lifting and just change
    the file detection logic.
    """

    format = ToolFormat.AGENTS_MD

    def can_parse(self, path: Path) -> bool:
        return path.name == "AGENTS.md"

    def parse(self, content: str, path: Path) -> SyncContext:
        # Delegate to ClaudeMdParser — same markdown structure
        claude_parser = ClaudeMdParser()
        ctx = claude_parser.parse(content, path)

        # Override source format
        ctx.source_format = self.format
        ctx.source_path = str(path)

        return ctx
