"""Label + OptionMenu widget."""

from __future__ import annotations
import customtkinter as ctk
from typing import Callable


class LabeledOptionMenu(ctk.CTkFrame):
    """A frame containing a label and an option menu (dropdown)."""

    def __init__(
        self,
        master,
        label: str,
        values: list[str],
        default: str = "",
        width: int = 200,
        on_change: Callable[[str], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_change = on_change
        self._suppress = False

        self._label = ctk.CTkLabel(self, text=label, width=220, anchor="w")
        self._label.pack(side="left", padx=(0, 5))

        # Prepend empty option for "not set"
        if "" not in values:
            values = [""] + values

        self._var = ctk.StringVar(value=default)
        self._menu = ctk.CTkOptionMenu(
            self,
            variable=self._var,
            values=values,
            width=width,
            command=self._on_menu_change,
        )
        self._menu.pack(side="left", fill="x", expand=True)

    def _on_menu_change(self, val):
        if not self._suppress and self._on_change:
            self._on_change(val)

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str) -> None:
        self._suppress = True
        self._var.set(value)
        self._suppress = False
