"""Collapsible section frame widget."""

from __future__ import annotations
import customtkinter as ctk


class SectionFrame(ctk.CTkFrame):
    """A collapsible section with a toggle header."""

    def __init__(
        self,
        master,
        title: str,
        expanded: bool = True,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._expanded = expanded

        # Header button
        self._header = ctk.CTkButton(
            self,
            text=f"{'▼' if expanded else '▶'} {title}",
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            command=self._toggle,
            height=30,
        )
        self._header.pack(fill="x", padx=5, pady=(5, 0))

        self._title = title

        # Content frame
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        if expanded:
            self._content.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    @property
    def content(self) -> ctk.CTkFrame:
        return self._content

    def _toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            self._content.pack(fill="both", expand=True, padx=10, pady=(0, 5))
            self._header.configure(text=f"▼ {self._title}")
        else:
            self._content.pack_forget()
            self._header.configure(text=f"▶ {self._title}")
