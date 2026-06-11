"""Renderer base class and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ctx_sync.models import SyncContext, ToolFormat

_RENDERERS: dict[ToolFormat, type[BaseRenderer]] = {}


class BaseRenderer(ABC):
    """Abstract base for config file renderers."""

    format: ToolFormat

    @abstractmethod
    def render(self, ctx: SyncContext) -> str:
        """Render a SyncContext into the target format string."""
        ...


def register_renderer(cls: type[BaseRenderer]) -> type[BaseRenderer]:
    """Decorator to register a renderer class."""
    _RENDERERS[cls.format] = cls
    return cls


def get_renderer(fmt: ToolFormat) -> BaseRenderer:
    """Get a renderer instance for the given format."""
    if fmt not in _RENDERERS:
        raise ValueError(f"No renderer registered for format: {fmt.value}")
    return _RENDERERS[fmt]()


def get_all_renderers() -> dict[ToolFormat, type[BaseRenderer]]:
    """Return all registered renderer classes."""
    return dict(_RENDERERS)


# Import all concrete renderers so their @register_renderer decorators fire
from ctx_sync.renderers import (  # noqa: E402, F401
    agents_md,
    claude_md,
    copilot,
    cursorrules,
)
