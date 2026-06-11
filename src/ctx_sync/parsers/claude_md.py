"""Parser for CLAUDE.md (Claude Code) files."""

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
from ctx_sync.parsers._markdown import (
    find_section,
    parse_bullet_commands,
    parse_bullet_list,
    split_sections,
)


@register_parser
class ClaudeMdParser(BaseParser):
    format = ToolFormat.CLAUDE_MD

    def can_parse(self, path: Path) -> bool:
        return path.name.upper() == "CLAUDE.MD"

    def parse(self, content: str, path: Path) -> SyncContext:
        ctx = SyncContext(
            source_format=self.format,
            source_path=str(path),
        )

        sections = split_sections(content)

        # Project description (content before first ##)
        if "" in sections:
            pre = sections[""]
            # First line might be a # heading
            lines = pre.strip().split("\n")
            for line in lines:
                if line.startswith("# "):
                    ctx.project_name = line[2:].strip()
                elif line.strip() and not ctx.description:
                    ctx.description = line.strip()

        # Commands
        raw_cmds = find_section(sections, "Commands", "commands", "Build & Run", "Key Commands")
        if raw_cmds:
            for name, cmd, desc in parse_bullet_commands(raw_cmds):
                ctx.commands.append(Command(name=name, command=cmd, description=desc))

        # Architecture
        raw_arch = find_section(sections, "Architecture", "architecture", "Structure", "Project Structure", "Directory Structure")
        if raw_arch:
            for line in raw_arch.split("\n"):
                line = line.strip()
                # `- \`src/api/\` — REST API routes`
                m = re.match(r"[-*]\s*`([^`]+)`\s*[—\u2013-]+\s*(.+)", line)
                if m:
                    ctx.architecture.append(
                        ArchitectureEntry(path=m.group(1).strip(), description=m.group(2).strip())
                    )

        # Conventions
        raw_conv = find_section(sections, "Conventions", "conventions", "Code Style", "Style", "Coding Standards")
        if raw_conv:
            for line in raw_conv.split("\n"):
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    text = line[2:].strip()
                    # Extract category if bolded: **naming**: ...
                    m = re.match(r"\*\*([^*]+)\*\*:\s*(.+)", text)
                    if m:
                        ctx.conventions.append(Convention(category=m.group(1).strip(), rule=m.group(2).strip()))
                    else:
                        ctx.conventions.append(Convention(category="general", rule=text))

        # Tech Stack
        raw_stack = find_section(sections, "Stack", "Tech Stack", "Technology", "stack")
        if raw_stack:
            # Might be "TypeScript / Next.js / Prisma" or bullet list
            if "/" in raw_stack and "\n" not in raw_stack.strip():
                ctx.tech_stack = [s.strip() for s in raw_stack.split("/") if s.strip()]
            else:
                bullets = parse_bullet_list(raw_stack)
                if bullets:
                    ctx.tech_stack = bullets
                else:
                    ctx.tech_stack = [raw_stack.strip()]

        # Git standards
        raw_git = find_section(sections, "Git", "git", "Git Standards")
        if raw_git:
            ctx.git_standards = raw_git

        # Preserve unmapped sections as raw
        mapped = {
            "", "Commands", "commands", "Build & Run", "Key Commands",
            "Architecture", "architecture", "Structure", "Project Structure", "Directory Structure",
            "Conventions", "conventions", "Code Style", "Style", "Coding Standards",
            "Stack", "Tech Stack", "Technology", "stack",
            "Git", "git", "Git Standards",
        }
        for key, value in sections.items():
            if key not in mapped and value.strip():
                ctx.raw_sections[key] = value

        return ctx
