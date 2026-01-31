"""tnsnames.ora tab implementation."""

from __future__ import annotations
import copy
import customtkinter as ctk

from orafiles.models.tnsnames import TNSNamesConfig, ServiceEntry, ConnectData, FailoverMode, DescriptionSecurity
from orafiles.models.protocol_address import TCPAddress
from orafiles.generators.tnsnames_gen import TNSNamesGenerator
from orafiles.parser.parser import parse_ora
from orafiles.gui.preview_panel import PreviewPanel
from orafiles.gui.widgets.list_manager import ListManager
from orafiles.gui.widgets.toolbar import Toolbar
from orafiles.gui.dialogs.service_dialog import ServiceDialog
from orafiles.gui.dialogs.file_dialogs import open_ora_file, save_ora_file
from orafiles.utils.file_io import read_file, write_file
from orafiles.utils.clipboard import copy_to_clipboard


class TNSNamesTab(ctk.CTkFrame):
    """Tab for editing tnsnames.ora configuration."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._config = TNSNamesConfig()
        self._generator = TNSNamesGenerator()

        self._build_ui()

    def _build_ui(self):
        # Toolbar
        toolbar = Toolbar(
            self,
            on_import=self._do_import,
            on_export=self._do_export,
            on_copy=self._do_copy,
            on_clear=self._do_clear,
        )
        toolbar.pack(fill="x", padx=5, pady=5)

        # 3-panel layout
        pane = ctk.CTkFrame(self, fg_color="transparent")
        pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=1)
        pane.columnconfigure(1, weight=2)
        pane.columnconfigure(2, weight=2)
        pane.rowconfigure(0, weight=1)

        # Left: service list
        self._list_manager = ListManager(
            pane,
            title="Net Services",
            on_select=self._on_select,
            on_add=self._on_add,
            on_edit=self._on_edit,
            on_delete=self._on_delete,
            on_duplicate=self._on_duplicate,
        )
        self._list_manager.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        # Middle: detail view (read-only summary)
        self._detail_frame = ctk.CTkScrollableFrame(pane)
        self._detail_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)

        self._detail_label = ctk.CTkLabel(
            self._detail_frame,
            text="Select or add a service to view details.",
            anchor="nw",
            justify="left",
            wraplength=300,
        )
        self._detail_label.pack(fill="both", expand=True, padx=5, pady=5)

        # Right: preview
        self._preview = PreviewPanel(pane, title="tnsnames.ora Preview")
        self._preview.grid(row=0, column=2, sticky="nsew", padx=(2, 5), pady=5)

    def _refresh_list(self):
        names = [svc.name for svc in self._config.services]
        self._list_manager.set_items(names)
        self._update_preview()

    def _on_select(self, index: int):
        if 0 <= index < len(self._config.services):
            svc = self._config.services[index]
            self._show_detail(svc)

    def _show_detail(self, svc: ServiceEntry):
        lines = []
        lines.append(f"Name: {svc.name}")
        lines.append(f"Addresses: {len(svc.addresses)}")
        for i, addr in enumerate(svc.addresses):
            from orafiles.models.protocol_address import get_protocol_name, TCPAddress, TCPSAddress, IPCAddress, NMPAddress
            proto = get_protocol_name(addr)
            if isinstance(addr, (TCPAddress, TCPSAddress)):
                lines.append(f"  [{i}] {proto} {addr.host}:{addr.port}")
            elif isinstance(addr, IPCAddress):
                lines.append(f"  [{i}] IPC KEY={addr.key}")
            elif isinstance(addr, NMPAddress):
                lines.append(f"  [{i}] NMP PIPE={addr.pipe}")

        cd = svc.connect_data
        if cd.service_name:
            lines.append(f"SERVICE_NAME: {cd.service_name}")
        if cd.sid:
            lines.append(f"SID: {cd.sid}")
        if cd.server:
            lines.append(f"SERVER: {cd.server}")
        if cd.instance_name:
            lines.append(f"INSTANCE_NAME: {cd.instance_name}")

        self._detail_label.configure(text="\n".join(lines))

    def _on_add(self):
        dialog = ServiceDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self._config.services.append(dialog.result)
            self._refresh_list()
            self._list_manager.select_index(len(self._config.services) - 1)

    def _on_edit(self, index: int):
        if 0 <= index < len(self._config.services):
            svc = self._config.services[index]
            dialog = ServiceDialog(self, svc)
            self.wait_window(dialog)
            if dialog.result:
                self._config.services[index] = dialog.result
                self._refresh_list()
                self._list_manager.select_index(index)

    def _on_delete(self, index: int):
        if 0 <= index < len(self._config.services):
            self._config.services.pop(index)
            self._refresh_list()
            self._detail_label.configure(text="Select or add a service to view details.")

    def _on_duplicate(self, index: int):
        if 0 <= index < len(self._config.services):
            original = self._config.services[index]
            dup = copy.deepcopy(original)
            dup.name = f"{dup.name}_COPY"
            self._config.services.append(dup)
            self._refresh_list()
            self._list_manager.select_index(len(self._config.services) - 1)

    def _update_preview(self):
        try:
            text = self._generator.generate(self._config)
            self._preview.set_text(text)
        except Exception:
            pass

    def get_preview_text(self) -> str:
        return self._preview.get_text()

    def _do_import(self):
        path = open_ora_file("Import tnsnames.ora")
        if path:
            try:
                text = read_file(path)
                ast = parse_ora(text)
                self._config = TNSNamesConfig.from_ast(ast)
                self._refresh_list()
                if self._config.services:
                    self._list_manager.select_index(0)
            except Exception as e:
                ctk.CTkInputDialog(text=f"Error importing: {e}", title="Import Error")

    def _do_export(self):
        path = save_ora_file("Export tnsnames.ora", "tnsnames.ora")
        if path:
            try:
                text = self._generator.generate(self._config)
                write_file(path, text)
            except Exception as e:
                ctk.CTkInputDialog(text=f"Error exporting: {e}", title="Export Error")

    def _do_copy(self):
        text = self.get_preview_text()
        if text:
            copy_to_clipboard(self, text)

    def _do_clear(self):
        self._config = TNSNamesConfig()
        self._refresh_list()
        self._detail_label.configure(text="Select or add a service to view details.")
