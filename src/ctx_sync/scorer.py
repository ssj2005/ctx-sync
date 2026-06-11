"""Quality scoring engine for AI config files.

Based on research (arXiv 2602.11988): exact build/test/lint commands
are the most valuable context. Verbose files can REDUCE task success.
Optimal length is 50-200 lines.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScoreReport:
    """Quality report for a config file."""

    total: int  # 0-100
    grade: str  # A / B / C / D
    breakdown: dict[str, int] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


def score(content: str, file_path: Path | None = None) -> ScoreReport:
    """Score a config file's quality.

    Scoring dimensions (total 100 points):
      1. Commands (30 pts) — build/test/lint/dev commands present
      2. Architecture (20 pts) — directory structure or architecture description
      3. Conventions (15 pts) — coding style / naming / error handling rules
      4. Conciseness (15 pts) — optimal 50-200 lines
      5. Freshness (10 pts) — referenced files still exist
      6. Security (10 pts) — no leaked secrets
    """
    breakdown: dict[str, int] = {}
    issues: list[str] = []
    suggestions: list[str] = []
    lines = content.strip().split("\n")
    line_count = len(lines)
    content_lower = content.lower()

    # ── 1. Commands (30 pts) ──────────────────────────────────────────
    has_build = any(kw in content_lower for kw in ["build", "compile"])
    has_test = "test" in content_lower
    has_lint = any(kw in content_lower for kw in ["lint", "format", "eslint", "ruff", "prettier", "black"])
    has_dev = any(kw in content_lower for kw in ["dev", "start", "run", "serve"])

    cmd_pts = has_build * 8 + has_test * 8 + has_lint * 7 + has_dev * 7
    breakdown["commands"] = cmd_pts

    if not has_build:
        issues.append("Missing build command")
        suggestions.append("Add a build command (e.g. `pnpm build` or `mvn compile`)")
    if not has_test:
        suggestions.append("Add a test command (research shows this is the most valuable context)")
    if not has_lint:
        suggestions.append("Add a lint/format command")
    if not has_dev:
        suggestions.append("Add a dev/start command")

    # ── 2. Architecture (20 pts) ──────────────────────────────────────
    has_arch_keyword = any(
        kw in content_lower
        for kw in ["architecture", "structure", "directory", "目录"]
    )
    has_dir_entries = any(
        line.strip().startswith("-") or line.strip().startswith("├") or line.strip().startswith("└")
        for line in lines
    ) and any("`" in line and ("/" in line or "\\" in line or "." in line) for line in lines)

    arch_pts = min(20, (10 if has_arch_keyword else 0) + (10 if has_dir_entries else 5))
    breakdown["architecture"] = arch_pts

    if not has_arch_keyword:
        suggestions.append("Add an Architecture section describing project structure")

    # ── 3. Conventions (15 pts) ───────────────────────────────────────
    has_conv = any(
        kw in content_lower
        for kw in ["convention", "style", "pattern", "约定", "naming", "error-handling"]
    )
    conv_pts = 15 if has_conv else 5
    breakdown["conventions"] = conv_pts

    if not has_conv:
        suggestions.append("Add a Conventions section with coding style rules")

    # ── 4. Conciseness (15 pts) ───────────────────────────────────────
    # Research: >200 lines reduces AI performance
    if line_count < 30:
        length_pts = 4
        issues.append(f"Only {line_count} lines — likely missing important info")
        suggestions.append("Expand to 80-150 lines covering commands, architecture, conventions")
    elif line_count <= 200:
        length_pts = 15
    elif line_count <= 400:
        length_pts = 8
        suggestions.append(
            f"File is {line_count} lines — consider trimming to <200 lines "
            "(verbose context degrades AI performance by ~20%)"
        )
    else:
        length_pts = 2
        issues.append(f"File is {line_count} lines — severely overweight")
        suggestions.append("Strongly recommend trimming to <200 lines or splitting into sub-files")
    breakdown["conciseness"] = length_pts

    # ── 5. Freshness (10 pts) ─────────────────────────────────────────
    # Check if referenced file paths still exist
    file_refs = re.findall(r"`([a-zA-Z0-9_./\\-]+\.[a-z]{1,10})`", content)
    dead_refs: list[str] = []

    if file_refs and file_path and file_path.parent.exists():
        for ref in set(file_refs):
            # Normalize path separators
            normalized = ref.replace("/", "\\") if "\\" in str(file_path) else ref
            if not (file_path.parent / normalized).exists():
                dead_refs.append(ref)

    if not file_refs:
        freshness_pts = 7  # No refs = no dead refs, but no extra points either
    elif not dead_refs:
        freshness_pts = 10
    else:
        freshness_pts = max(0, 10 - len(dead_refs) * 3)
        for ref in dead_refs:
            issues.append(f"Referenced file does not exist: `{ref}`")
        suggestions.append("Remove or update references to files that no longer exist")
    breakdown["freshness"] = freshness_pts

    # ── 6. Security (10 pts) ──────────────────────────────────────────
    has_secret = any(
        kw in content_lower
        for kw in [
            "api_key", "secret_key", "password =", "passwd",
            "sk-", "xai-", "ghp_", "AKIA", "-----BEGIN",
        ]
    )
    # Also check for common secret patterns
    has_secret_pattern = bool(re.search(r"(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}", content, re.IGNORECASE))

    sec_pts = 0 if (has_secret or has_secret_pattern) else 10
    if has_secret or has_secret_pattern:
        issues.append("CRITICAL: Detected possible secrets/credentials — remove immediately!")
    breakdown["security"] = sec_pts

    # ── Total ──────────────────────────────────────────────────────────
    total = sum(breakdown.values())

    if total >= 80:
        grade = "A"
    elif total >= 60:
        grade = "B"
    elif total >= 40:
        grade = "C"
    else:
        grade = "D"

    return ScoreReport(
        total=total,
        grade=grade,
        breakdown=breakdown,
        issues=issues,
        suggestions=suggestions,
    )
