"""Renderer for AGENTS.md (OpenCode / Codex) format."""

from __future__ import annotations

from ctx_sync.models import SyncContext, ToolFormat
from ctx_sync.renderers import BaseRenderer, register_renderer
from ctx_sync.renderers.claude_md import ClaudeMdRenderer


@register_renderer
class AgentsMdRenderer(BaseRenderer):
    """AGENTS.md is structurally identical to CLAUDE.md.

    We reuse ClaudeMdRenderer and just change the format tag.
    """

    format = ToolFormat.AGENTS_MD

    def render(self, ctx: SyncContext) -> str:
        claude_renderer = ClaudeMdRenderer()
        return claude_renderer.render(ctx)
