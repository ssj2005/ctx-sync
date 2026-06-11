"""Parser base class and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ctx_sync.models import SyncContext, ToolFormat

_PARSERS: dict[ToolFormat, type[BaseParser]] = {}


class BaseParser(ABC):
    """Abstract base for config file parsers."""

    format: ToolFormat

    @abstractmethod
    def parse(self, content: str, path: Path) -> SyncContext:
        """Parse file content into a SyncContext."""
        ...

    @abstractmethod
    def can_parse(self, path: Path) -> bool:
        """Return True if this parser handles the given file."""
        ...


def register_parser(cls: type[BaseParser]) -> type[BaseParser]:
    """Decorator to register a parser class."""
    _PARSERS[cls.format] = cls
    return cls


def get_parser(fmt: ToolFormat) -> BaseParser:
    """Get a parser instance for the given format."""
    if fmt not in _PARSERS:
        raise ValueError(f"No parser registered for format: {fmt.value}")
    return _PARSERS[fmt]()


def get_all_parsers() -> dict[ToolFormat, type[BaseParser]]:
    """Return all registered parser classes."""
    return dict(_PARSERS)


# Import all concrete parsers so their @register_parser decorators fire
from ctx_sync.parsers import (  # noqa: E402, F401
    agents_md,
    claude_md,
    copilot,
    cursor_mdc,
    cursorrules,
)
