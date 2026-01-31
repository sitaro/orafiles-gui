"""Main window with tabview and menubar."""

from __future__ import annotations
import customtkinter as ctk
from orafiles.gui.tab_listener import ListenerTab
from orafiles.gui.tab_tnsnames import TNSNamesTab
from orafiles.gui.tab_sqlnet import SQLNetTab
from orafiles.gui.dialogs.file_dialogs import open_ora_file, save_ora_file
from orafiles.utils.file_io import read_file, write_file


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("OraFiles GUI - Oracle Configuration Editor")
        self.geometry("1200x800")
        self.minsize(900, 600)

        self._build_menu()
        self._build_ui()
        self._build_statusbar()

    def _build_menu(self):
        menubar = ctk.CTkFrame(self, height=30, fg_color=("gray85", "gray20"))
        menubar.pack(fill="x")
        menubar.pack_propagate(False)

        # File menu buttons
        ctk.CTkButton(
            menubar, text="Import", width=70, height=24,
            fg_color="transparent", hover_color=("gray75", "gray30"),
            command=self._menu_import
        ).pack(side="left", padx=2, pady=3)

        ctk.CTkButton(
            menubar, text="Export", width=70, height=24,
            fg_color="transparent", hover_color=("gray75", "gray30"),
            command=self._menu_export
        ).pack(side="left", padx=2, pady=3)

        # Separator
        ctk.CTkLabel(menubar, text="|", text_color="gray50").pack(side="left", padx=5)

        # Appearance toggle
        ctk.CTkButton(
            menubar, text="Dark/Light", width=80, height=24,
            fg_color="transparent", hover_color=("gray75", "gray30"),
            command=self._toggle_appearance
        ).pack(side="left", padx=2, pady=3)

        # About
        ctk.CTkButton(
            menubar, text="About", width=60, height=24,
            fg_color="transparent", hover_color=("gray75", "gray30"),
            command=self._show_about
        ).pack(side="right", padx=2, pady=3)

    def _build_ui(self):
        self._tabview = ctk.CTkTabview(self, command=self._on_tab_changed)
        self._tabview.pack(fill="both", expand=True, padx=5, pady=5)

        self._tabview.add("listener.ora")
        self._tabview.add("tnsnames.ora")
        self._tabview.add("sqlnet.ora")

        self._listener_tab: ListenerTab | None = None
        self._tnsnames_tab: TNSNamesTab | None = None
        self._sqlnet_tab: SQLNetTab | None = None

        # Build only the first tab immediately
        self.after(50, self._ensure_current_tab)

    def _on_tab_changed(self):
        self._ensure_current_tab()

    def _ensure_current_tab(self):
        current = self._tabview.get()
        if current == "listener.ora" and self._listener_tab is None:
            self._listener_tab = ListenerTab(self._tabview.tab("listener.ora"))
            self._listener_tab.pack(fill="both", expand=True)
        elif current == "tnsnames.ora" and self._tnsnames_tab is None:
            self._tnsnames_tab = TNSNamesTab(self._tabview.tab("tnsnames.ora"))
            self._tnsnames_tab.pack(fill="both", expand=True)
        elif current == "sqlnet.ora" and self._sqlnet_tab is None:
            self._sqlnet_tab = SQLNetTab(self._tabview.tab("sqlnet.ora"))
            self._sqlnet_tab.pack(fill="both", expand=True)

    def _build_statusbar(self):
        self._statusbar = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            height=20,
            font=ctk.CTkFont(size=11),
            text_color="gray50",
        )
        self._statusbar.pack(fill="x", padx=10, pady=(0, 3))

    def _set_status(self, text: str):
        self._statusbar.configure(text=text)

    def _menu_import(self):
        """Import dispatches to the currently active tab."""
        self._ensure_current_tab()
        current = self._tabview.get()
        if current == "listener.ora" and self._listener_tab:
            self._listener_tab._do_import()
        elif current == "tnsnames.ora" and self._tnsnames_tab:
            self._tnsnames_tab._do_import()
        elif current == "sqlnet.ora" and self._sqlnet_tab:
            self._sqlnet_tab._do_import()

    def _menu_export(self):
        """Export dispatches to the currently active tab."""
        self._ensure_current_tab()
        current = self._tabview.get()
        if current == "listener.ora" and self._listener_tab:
            self._listener_tab._do_export()
        elif current == "tnsnames.ora" and self._tnsnames_tab:
            self._tnsnames_tab._do_export()
        elif current == "sqlnet.ora" and self._sqlnet_tab:
            self._sqlnet_tab._do_export()

    def _toggle_appearance(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def _show_about(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("About OraFiles GUI")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="OraFiles GUI",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            dialog,
            text="Oracle Configuration File Editor\nv1.0.0",
            justify="center",
        ).pack(pady=5)

        ctk.CTkLabel(
            dialog,
            text="listener.ora | tnsnames.ora | sqlnet.ora",
            text_color="gray50",
        ).pack(pady=5)

        ctk.CTkButton(
            dialog, text="Close", width=80,
            command=dialog.destroy,
        ).pack(pady=10)
