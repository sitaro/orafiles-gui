"""Clipboard utilities."""

from __future__ import annotations
import tkinter as tk


def copy_to_clipboard(root: tk.Misc, text: str) -> None:
    """Copy text to the system clipboard."""
    root.clipboard_clear()
    root.clipboard_append(text)
