"""Live preview panel for generated .ora content."""

from __future__ import annotations
import customtkinter as ctk


class PreviewPanel(ctk.CTkFrame):
    """Read-only text area for displaying generated .ora file content."""

    def __init__(self, master, title: str = "Preview", **kwargs):
        super().__init__(master, **kwargs)

        header = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(weight="bold"))
        header.pack(fill="x", padx=5, pady=(5, 2))

        self._textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier", size=12),
            wrap="none",
            state="disabled",
        )
        self._textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def set_text(self, text: str) -> None:
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("1.0", text)
        self._textbox.configure(state="disabled")

    def get_text(self) -> str:
        return self._textbox.get("1.0", "end").rstrip()
