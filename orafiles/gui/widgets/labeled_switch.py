"""Label + Switch widget."""

from __future__ import annotations
import customtkinter as ctk
from typing import Callable


class LabeledSwitch(ctk.CTkFrame):
    """A frame containing a label and a switch (on/off toggle)."""

    def __init__(
        self,
        master,
        label: str,
        on_value: str = "ON",
        off_value: str = "",
        on_change: Callable[[str], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_value = on_value
        self._off_value = off_value
        self._on_change = on_change

        self._label = ctk.CTkLabel(self, text=label, width=220, anchor="w")
        self._label.pack(side="left", padx=(0, 5))

        self._var = ctk.StringVar(value=off_value)
        self._switch = ctk.CTkSwitch(
            self,
            text="",
            variable=self._var,
            onvalue=on_value,
            offvalue=off_value,
            command=self._changed,
        )
        self._switch.pack(side="left")

    def _changed(self):
        if self._on_change:
            self._on_change(self._var.get())

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str) -> None:
        self._var.set(value)
        if value == self._on_value:
            self._switch.select()
        else:
            self._switch.deselect()
