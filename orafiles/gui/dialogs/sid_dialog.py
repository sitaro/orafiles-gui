"""Dialog for editing a SID_DESC entry."""

from __future__ import annotations
import customtkinter as ctk
from orafiles.models.listener import SIDEntry
from orafiles.gui.widgets.labeled_entry import LabeledEntry


class SIDDialog(ctk.CTkToplevel):
    """Dialog to create or edit a SID_DESC entry."""

    def __init__(self, master, sid: SIDEntry | None = None):
        super().__init__(master)
        self.title("Edit SID Entry")
        self.geometry("450x350")
        self.resizable(False, False)
        self.grab_set()

        self.result: SIDEntry | None = None

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._sid_name = LabeledEntry(frame, "SID_NAME:")
        self._sid_name.pack(fill="x", pady=3)

        self._global_dbname = LabeledEntry(frame, "GLOBAL_DBNAME:")
        self._global_dbname.pack(fill="x", pady=3)

        self._oracle_home = LabeledEntry(frame, "ORACLE_HOME:")
        self._oracle_home.pack(fill="x", pady=3)

        self._program = LabeledEntry(frame, "PROGRAM:")
        self._program.pack(fill="x", pady=3)

        self._envs = LabeledEntry(frame, "ENVS:")
        self._envs.pack(fill="x", pady=3)

        self._sdu = LabeledEntry(frame, "SDU:", placeholder="8192")
        self._sdu.pack(fill="x", pady=3)

        if sid:
            self._sid_name.set(sid.sid_name)
            self._global_dbname.set(sid.global_dbname)
            self._oracle_home.set(sid.oracle_home)
            self._program.set(sid.program)
            self._envs.set(sid.envs)
            self._sdu.set(sid.sdu)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="OK", width=80, command=self._ok).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", width=80, command=self._cancel).pack(side="right", padx=5)

    def _ok(self):
        self.result = SIDEntry(
            sid_name=self._sid_name.get(),
            global_dbname=self._global_dbname.get(),
            oracle_home=self._oracle_home.get(),
            program=self._program.get(),
            envs=self._envs.get(),
            sdu=self._sdu.get(),
        )
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
