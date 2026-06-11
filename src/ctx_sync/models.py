"""Unified data model for all AI config formats.

Every parser converts its format into a SyncContext.
Every renderer converts a SyncContext into its format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ToolFormat(Enum):
    """Supported AI coding tool config formats."""

    CLAUDE_MD = "claude-md"  # CLAUDE.md (Claude Code)
    AGENTS_MD = "agents-md"  # AGENTS.md (OpenCode / Codex)
    CURSOR_RULES = "cursorrules"  # .cursorrules (Cursor legacy)
    CURSOR_MDC = "cursor-mdc"  # .cursor/rules/*.mdc (Cursor current)
    COPILOT = "copilot"  # .github/copilot-instructions.md

    @property
    def display_name(self) -> str:
        names = {
            ToolFormat.CLAUDE_MD: "Claude Code (CLAUDE.md)",
            ToolFormat.AGENTS_MD: "OpenCode/Codex (AGENTS.md)",
            ToolFormat.CURSOR_RULES: "Cursor (.cursorrules)",
            ToolFormat.CURSOR_MDC: "Cursor Rules (.cursor/rules/*.mdc)",
            ToolFormat.COPILOT: "GitHub Copilot (copilot-instructions.md)",
        }
        return names.get(self, self.value)


@dataclass
class Command:
    """A build/test/lint/dev command."""

    name: str  # "build" / "test" / "lint" / "dev"
    command: str  # "pnpm build"
    description: str = ""


@dataclass
class Convention:
    """A coding convention or rule."""

    category: str  # "naming" / "error-handling" / "imports" / "style"
    rule: str  # specific rule text
    example: str = ""


@dataclass
class ArchitectureEntry:
    """A directory or module description."""

    path: str  # "src/api/"
    description: str  # "REST API routes"


@dataclass
class SyncContext:
    """Universal intermediate representation for all config formats.

    Parsers produce this. Renderers consume this. The sync engine moves data
    through this layer to convert between formats.
    """

    # Metadata
    project_name: str = ""
    description: str = ""

    # Tech stack
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    package_manager: str = ""

    # Core sections — present across all formats
    commands: list[Command] = field(default_factory=list)
    architecture: list[ArchitectureEntry] = field(default_factory=list)
    conventions: list[Convention] = field(default_factory=list)
    tech_stack: list[str] = field(default_factory=list)
    git_standards: str = ""

    # Raw content — sections that don't map to structured fields
    raw_sections: dict[str, str] = field(default_factory=dict)

    # Source tracking
    source_format: ToolFormat | None = None
    source_path: str = ""
