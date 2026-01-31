"""Application initialization and entry point."""

import customtkinter as ctk
from orafiles.gui.main_window import MainWindow


def main():
    """Launch the OraFiles GUI application."""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
