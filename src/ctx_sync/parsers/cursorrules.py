"""Parser for .cursorrules (Cursor legacy) files."""

from __future__ import annotations

import re
from pathlib import Path

from ctx_sync.models import (
    ArchitectureEntry,
    Command,
    Convention,
    SyncContext,
    ToolFormat,
)
from ctx_sync.parsers import BaseParser, register_parser


@register_parser
class CursorrulesParser(BaseParser):
    """Parse .cursorrules files.

    .cursorrules uses a flat format with label-based sections like:
      Commands:
        pnpm build # build
      Project structure:
      - src/: description
    """

    format = ToolFormat.CURSOR_RULES

    def can_parse(self, path: Path) -> bool:
        return path.name == ".cursorrules"

    def parse(self, content: str, path: Path) -> SyncContext:
        ctx = SyncContext(
            source_format=self.format,
            source_path=str(path),
        )

        lines = content.split("\n")

        # Parse label-based sections: "Label:" followed by content
        sections = self._parse_labeled_sections(lines)

        # Title
        if "title" in sections:
            ctx.project_name = sections["title"].strip("# ").strip()

        # Tech stack (from intro paragraph)
        intro = sections.get("", "")
        if not intro:
            # Try first non-empty, non-label line
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.endswith(":") and not stripped.startswith("#"):
                    intro = stripped
                    break

        if intro:
            # Extract tech names from "uses X, Y, Z." patterns
            m = re.search(r"uses?\s+(.+?)\.", intro)
            if m:
                stack_str = m.group(1)
                ctx.tech_stack = [s.strip().strip(",") for s in re.split(r"[,/]", stack_str) if s.strip()]

        # Commands
        if "commands" in sections:
            for line in sections["commands"].split("\n"):
                line = line.strip()
                if not line:
                    continue
                # "pnpm build # build the project"
                m = re.match(r"`?([^`#\n]+)`?\s*(?:#\s*(.+))?", line)
                if m:
                    cmd = m.group(1).strip()
                    desc = (m.group(2) or "").strip()
                    name = self._infer_name(cmd)
                    ctx.commands.append(Command(name=name, command=cmd, description=desc))

        # Architecture / Project structure
        for key in ("project structure", "structure", "architecture"):
            if key in sections:
                for line in sections[key].split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    # "- src/app/: Next.js pages" or "- `src/app/` — pages"
                    m = re.match(r"[-*]\s*`?([^`:\n]+)`?\s*(?:[—\u2013\u2014:]\s*)?(.+)", line)
                    if m:
                        ctx.architecture.append(
                            ArchitectureEntry(path=m.group(1).strip().rstrip(":"), description=m.group(2).strip())
                        )
                break

        # Conventions
        for key in ("coding conventions", "conventions", "style"):
            if key in sections:
                for line in sections[key].split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    text = line.lstrip("-* ").strip()
                    m = re.match(r"\*\*([^*]+)\*\*:?\s*(.+)", text)
                    if m:
                        ctx.conventions.append(Convention(category=m.group(1).strip(), rule=m.group(2).strip()))
                    elif len(text) > 3:
                        ctx.conventions.append(Convention(category="general", rule=text))
                break

        # Git standards
        for key in ("git", "git standards"):
            if key in sections:
                ctx.git_standards = sections[key]
                break

        # Store unmapped sections as raw
        mapped_keys = {"", "title", "commands", "project structure", "structure",
                       "architecture", "coding conventions", "conventions", "style",
                       "git", "git standards"}
        for key, value in sections.items():
            if key.lower() not in mapped_keys and value.strip():
                ctx.raw_sections[key] = value

        return ctx

    def _parse_labeled_sections(self, lines: list[str]) -> dict[str, str]:
        """Parse flat format into labeled sections.

        Handles both:
          Label:
            content lines
        And content before any label (stored under "").
        """
        sections: dict[str, str] = {}
        current_label = ""
        current_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines but keep them in current section
            if not stripped:
                current_lines.append("")
                continue

            # Title line
            if stripped.startswith("# ") and not current_label:
                sections["title"] = stripped[2:].strip()
                continue

            # Label line: "Commands:" or "Project structure:"
            if stripped.endswith(":") and not stripped.startswith("-") and not stripped.startswith("*"):
                # Save previous section
                if current_label or current_lines:
                    text = "\n".join(current_lines).strip()
                    if text:
                        sections[current_label.lower()] = text
                current_label = stripped.rstrip(":").strip()
                current_lines = []
                continue

            current_lines.append(stripped)

        # Last section
        if current_label or current_lines:
            text = "\n".join(current_lines).strip()
            if text:
                sections[current_label.lower()] = text

        return sections

    def _infer_name(self, cmd: str) -> str:
        """Infer a command name from the command string."""
        parts = cmd.split()
        if not parts:
            return "unknown"
        runners = {"pnpm", "npm", "yarn", "bun", "npx", "uv", "python", "go", "cargo", "mvn", "gradle", "make", "docker"}
        filtered = [p for p in parts if p not in runners]
        return filtered[0] if filtered else parts[0]
