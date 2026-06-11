"""Markdown utility functions shared across parsers."""

from __future__ import annotations

import re


def split_sections(content: str) -> dict[str, str]:
    """Split markdown content by ## headings into a dict.

    Returns {heading_text: body_text, ...}.
    Content before the first ## is stored under key "" (empty string).
    """
    sections: dict[str, str] = {}
    current_header = ""
    current_lines: list[str] = []

    for line in content.split("\n"):
        # Match ## headings (but not ### or deeper)
        if re.match(r"^## \S", line):
            if current_header or current_lines:
                sections[current_header] = "\n".join(current_lines).strip()
            current_header = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Last section
    if current_header or current_lines:
        sections[current_header] = "\n".join(current_lines).strip()

    return sections


def parse_bullet_commands(raw: str) -> list[tuple[str, str, str]]:
    """Parse command-like bullet points from a section body.

    Returns list of (name, command, description) tuples.

    Handles patterns like:
      - `pnpm build` — build the project
      - build: `pnpm build` - compile everything
      - `pnpm test` to run tests
    """
    results: list[tuple[str, str, str]] = []

    for line in raw.split("\n"):
        line = line.strip()
        if not line or not line.startswith("-"):
            continue

        # Remove leading bullet
        line = line.lstrip("- ").strip()

        # Pattern 1: `command` — description
        m = re.match(r"`([^`]+)`\s*[—\u2013-]+\s*(.+)", line)
        if m:
            cmd = m.group(1).strip()
            desc = m.group(2).strip()
            name = _infer_command_name(cmd)
            results.append((name, cmd, desc))
            continue

        # Pattern 2: name: `command` — description
        m = re.match(r"(\w[\w\s]*?):\s*`([^`]+)`\s*[—\u2013-]*\s*(.*)", line)
        if m:
            results.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
            continue

        # Pattern 3: name: command (no backticks)
        m = re.match(r"(\w[\w\s]*?):\s*(.+)", line)
        if m:
            name = m.group(1).strip()
            rest = m.group(2).strip()
            results.append((name, rest, ""))

    return results


def _infer_command_name(cmd: str) -> str:
    """Infer a command name from the command string."""
    parts = cmd.split()
    if not parts:
        return "unknown"

    # Skip package manager / runner
    runners = {"npx", "pnpm", "npm", "yarn", "bun", "uv", "python", "python3", "go", "cargo", "mvn", "gradle", "make", "docker", "docker-compose"}
    filtered = [p for p in parts if p not in runners]

    if filtered:
        return filtered[0]
    return parts[0]


def parse_bullet_list(raw: str) -> list[str]:
    """Parse a simple bullet list into a list of strings."""
    items: list[str] = []
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif line.startswith("* "):
            items.append(line[2:].strip())
    return items


def find_section(sections: dict[str, str], *candidates: str) -> str | None:
    """Find a section body by trying multiple heading candidates (case-insensitive)."""
    lower_map = {k.lower(): v for k, v in sections.items()}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None
