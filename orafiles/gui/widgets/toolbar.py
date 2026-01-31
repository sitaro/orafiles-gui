"""Toolbar widget with Import/Export/Preview/Copy/Clear buttons."""

from __future__ import annotations
import customtkinter as ctk
from typing import Callable


class Toolbar(ctk.CTkFrame):
    """Horizontal toolbar with action buttons."""

    def __init__(
        self,
        master,
        on_import: Callable[[], None] | None = None,
        on_export: Callable[[], None] | None = None,
        on_copy: Callable[[], None] | None = None,
        on_clear: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        if on_import:
            ctk.CTkButton(self, text="Import", width=80, command=on_import).pack(side="left", padx=3)
        if on_export:
            ctk.CTkButton(self, text="Export", width=80, command=on_export).pack(side="left", padx=3)
        if on_copy:
            ctk.CTkButton(self, text="Copy", width=80, command=on_copy).pack(side="left", padx=3)
        if on_clear:
            ctk.CTkButton(self, text="Clear", width=80, command=on_clear).pack(side="left", padx=3)
