"""Base formatting utilities for Oracle .ora file generation."""

from __future__ import annotations


class BaseGenerator:
    """Base class for .ora file generators."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def _ind(self, depth: int) -> str:
        return " " * (self.indent * depth)

    def _param(self, key: str, value: str, depth: int = 0) -> str:
        """Format a simple key = value line."""
        return f"{self._ind(depth)}{key} = {value}"

    def _param_line(self, key: str, value: str, depth: int = 0) -> str | None:
        """Format a key = value line only if value is non-empty."""
        if value:
            return self._param(key, value, depth)
        return None

    def _list_param(self, key: str, values: str, depth: int = 0) -> str | None:
        """Format a key = (val1, val2, ...) line from comma-separated string."""
        if not values:
            return None
        items = [v.strip() for v in values.split(",") if v.strip()]
        if not items:
            return None
        if len(items) == 1:
            return self._param(key, items[0], depth)
        vals = ", ".join(items)
        return f"{self._ind(depth)}{key} = ({vals})"

    def _build(self, lines: list[str | None]) -> str:
        """Join non-None lines with newlines."""
        return "\n".join(line for line in lines if line is not None)

    def _section_open(self, key: str, depth: int = 0) -> str:
        return f"{self._ind(depth)}{key} =\n{self._ind(depth)}("

    def _section_close(self, depth: int = 0) -> str:
        return f"{self._ind(depth)})"
