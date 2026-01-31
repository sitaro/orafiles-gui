"""Label + Entry widget."""

from __future__ import annotations
import customtkinter as ctk
from typing import Callable


class LabeledEntry(ctk.CTkFrame):
    """A frame containing a label and an entry field."""

    def __init__(
        self,
        master,
        label: str,
        placeholder: str = "",
        width: int = 200,
        on_change: Callable[[str], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_change = on_change
        self._suppress = False

        self._label = ctk.CTkLabel(self, text=label, width=220, anchor="w")
        self._label.pack(side="left", padx=(0, 5))

        self._var = ctk.StringVar()
        self._entry = ctk.CTkEntry(
            self, textvariable=self._var, placeholder_text=placeholder, width=width
        )
        self._entry.pack(side="left", fill="x", expand=True)

        if on_change:
            self._var.trace_add("write", self._on_var_change)

    def _on_var_change(self, *_args):
        if not self._suppress and self._on_change:
            self._on_change(self._var.get())

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str) -> None:
        self._suppress = True
        self._var.set(value)
        self._suppress = False

    def configure_state(self, state: str) -> None:
        self._entry.configure(state=state)
