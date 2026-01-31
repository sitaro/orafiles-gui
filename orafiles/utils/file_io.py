"""File read/write utilities."""

from __future__ import annotations
from pathlib import Path


def read_file(path: str | Path) -> str:
    """Read a text file and return its contents."""
    return Path(path).read_text(encoding="utf-8")


def write_file(path: str | Path, content: str) -> None:
    """Write text content to a file."""
    Path(path).write_text(content, encoding="utf-8")
