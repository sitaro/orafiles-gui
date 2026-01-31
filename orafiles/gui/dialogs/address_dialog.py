"""Dialog for editing a protocol address."""

from __future__ import annotations
import customtkinter as ctk
from orafiles.models.protocol_address import (
    TCPAddress, TCPSAddress, IPCAddress, NMPAddress, Address, get_protocol_name
)
from orafiles.gui.widgets.labeled_entry import LabeledEntry
from orafiles.gui.widgets.labeled_optionmenu import LabeledOptionMenu


class AddressDialog(ctk.CTkToplevel):
    """Dialog to create or edit a protocol address."""

    def __init__(self, master, address: Address | None = None):
        super().__init__(master)
        self.title("Edit Address")
        self.geometry("450x400")
        self.resizable(False, False)
        self.grab_set()

        self.result: Address | None = None
        self._address = address

        # Protocol selector
        initial_protocol = get_protocol_name(address) if address else "TCP"
        self._protocol = LabeledOptionMenu(
            self, "Protocol:", ["TCP", "TCPS", "IPC", "NMP"],
            default=initial_protocol,
            on_change=self._on_protocol_change,
        )
        self._protocol.pack(fill="x", padx=10, pady=5)

        # Dynamic fields frame
        self._fields_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._fields_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._field_widgets: dict[str, LabeledEntry] = {}
        self._build_fields(initial_protocol)
        self._populate(address)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="OK", width=80, command=self._ok).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", width=80, command=self._cancel).pack(side="right", padx=5)

    def _build_fields(self, protocol: str):
        for w in self._fields_frame.winfo_children():
            w.destroy()
        self._field_widgets.clear()

        if protocol in ("TCP", "TCPS"):
            port_default = "1521" if protocol == "TCP" else "2484"
            fields = [
                ("host", "Host:", "localhost"),
                ("port", "Port:", port_default),
                ("ip", "IP Version (v4/v6):", ""),
                ("queuesize", "Queue Size:", ""),
                ("buf_size", "Buffer Size:", ""),
                ("rate_limit", "Rate Limit:", ""),
            ]
        elif protocol == "IPC":
            fields = [
                ("key", "KEY:", "EXTPROC1"),
            ]
        elif protocol == "NMP":
            fields = [
                ("server", "Server:", ""),
                ("pipe", "Pipe:", ""),
            ]
        else:
            fields = []

        for name, label, placeholder in fields:
            w = LabeledEntry(self._fields_frame, label, placeholder=placeholder)
            w.pack(fill="x", pady=3)
            self._field_widgets[name] = w

    def _populate(self, address: Address | None):
        if not address:
            return
        if isinstance(address, (TCPAddress, TCPSAddress)):
            self._set_field("host", address.host)
            self._set_field("port", address.port)
            self._set_field("ip", address.ip)
            self._set_field("queuesize", address.queuesize)
            self._set_field("buf_size", address.buf_size)
            self._set_field("rate_limit", address.rate_limit)
        elif isinstance(address, IPCAddress):
            self._set_field("key", address.key)
        elif isinstance(address, NMPAddress):
            self._set_field("server", address.server)
            self._set_field("pipe", address.pipe)

    def _set_field(self, name: str, value: str):
        if name in self._field_widgets and value:
            self._field_widgets[name].set(value)

    def _get_field(self, name: str) -> str:
        if name in self._field_widgets:
            return self._field_widgets[name].get()
        return ""

    def _on_protocol_change(self, protocol: str):
        self._build_fields(protocol)

    def _ok(self):
        protocol = self._protocol.get()
        if protocol == "TCP":
            self.result = TCPAddress(
                host=self._get_field("host") or "localhost",
                port=self._get_field("port") or "1521",
                ip=self._get_field("ip"),
                queuesize=self._get_field("queuesize"),
                buf_size=self._get_field("buf_size"),
                rate_limit=self._get_field("rate_limit"),
            )
        elif protocol == "TCPS":
            self.result = TCPSAddress(
                host=self._get_field("host") or "localhost",
                port=self._get_field("port") or "2484",
                ip=self._get_field("ip"),
                queuesize=self._get_field("queuesize"),
                buf_size=self._get_field("buf_size"),
                rate_limit=self._get_field("rate_limit"),
            )
        elif protocol == "IPC":
            self.result = IPCAddress(key=self._get_field("key") or "EXTPROC1")
        elif protocol == "NMP":
            self.result = NMPAddress(
                server=self._get_field("server"),
                pipe=self._get_field("pipe"),
            )
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
