"""Import/Export file dialogs."""

from __future__ import annotations
from tkinter import filedialog


ORA_FILETYPES = [
    ("Oracle Config Files", "*.ora"),
    ("All Files", "*.*"),
]


def open_ora_file(title: str = "Import .ora File") -> str | None:
    """Show file open dialog for .ora files. Returns path or None."""
    path = filedialog.askopenfilename(
        title=title,
        filetypes=ORA_FILETYPES,
    )
    return path if path else None


def save_ora_file(title: str = "Export .ora File", default_name: str = "") -> str | None:
    """Show file save dialog for .ora files. Returns path or None."""
    path = filedialog.asksaveasfilename(
        title=title,
        filetypes=ORA_FILETYPES,
        defaultextension=".ora",
        initialfile=default_name,
    )
    return path if path else None
