"""listener.ora tab implementation."""

from __future__ import annotations
import copy
import customtkinter as ctk

from orafiles.models.listener import ListenerConfig, SIDEntry
from orafiles.models.protocol_address import (
    TCPAddress, TCPSAddress, IPCAddress, NMPAddress, Address, get_protocol_name
)
from orafiles.generators.listener_gen import ListenerGenerator
from orafiles.parser.parser import parse_ora
from orafiles.gui.preview_panel import PreviewPanel
from orafiles.gui.widgets.labeled_entry import LabeledEntry
from orafiles.gui.widgets.labeled_optionmenu import LabeledOptionMenu
from orafiles.gui.widgets.labeled_switch import LabeledSwitch
from orafiles.gui.widgets.section_frame import SectionFrame
from orafiles.gui.widgets.toolbar import Toolbar
from orafiles.gui.dialogs.address_dialog import AddressDialog
from orafiles.gui.dialogs.sid_dialog import SIDDialog
from orafiles.gui.dialogs.file_dialogs import open_ora_file, save_ora_file
from orafiles.utils.file_io import read_file, write_file
from orafiles.utils.clipboard import copy_to_clipboard


class ListenerTab(ctk.CTkFrame):
    """Tab for editing listener.ora configuration."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._config = ListenerConfig()
        self._generator = ListenerGenerator()
        self._addresses: list[Address] = []
        self._sid_list: list[SIDEntry] = []
        self._preview_job = None

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

        # Main paned layout
        pane = ctk.CTkFrame(self, fg_color="transparent")
        pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=3)
        pane.columnconfigure(1, weight=2)
        pane.rowconfigure(0, weight=1)

        # Left: scrollable form
        form_scroll = ctk.CTkScrollableFrame(pane)
        form_scroll.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        # Right: preview
        self._preview = PreviewPanel(pane, title="listener.ora Preview")
        self._preview.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)

        self._build_form(form_scroll)

    def _build_form(self, parent):
        # --- Identity ---
        sec = SectionFrame(parent, "Listener Identity")
        sec.pack(fill="x", pady=3)
        c = sec.content

        self._name = LabeledEntry(c, "Listener Name:", placeholder="LISTENER", on_change=self._schedule_preview)
        self._name.pack(fill="x", pady=2)

        # Addresses sub-section
        addr_frame = ctk.CTkFrame(c, fg_color="transparent")
        addr_frame.pack(fill="x", pady=3)
        ctk.CTkLabel(addr_frame, text="Protocol Addresses:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        self._addr_list_frame = ctk.CTkFrame(c, fg_color="transparent")
        self._addr_list_frame.pack(fill="x")

        addr_btns = ctk.CTkFrame(c, fg_color="transparent")
        addr_btns.pack(fill="x", pady=2)
        ctk.CTkButton(addr_btns, text="Add Address", width=100, command=self._add_address).pack(side="left", padx=3)
        ctk.CTkButton(addr_btns, text="Remove Last", width=100, command=self._remove_address).pack(side="left", padx=3)

        # --- SID List ---
        sec = SectionFrame(parent, "SID List")
        sec.pack(fill="x", pady=3)
        c = sec.content

        self._sid_list_frame = ctk.CTkFrame(c, fg_color="transparent")
        self._sid_list_frame.pack(fill="x")

        sid_btns = ctk.CTkFrame(c, fg_color="transparent")
        sid_btns.pack(fill="x", pady=2)
        ctk.CTkButton(sid_btns, text="Add SID", width=100, command=self._add_sid).pack(side="left", padx=3)
        ctk.CTkButton(sid_btns, text="Remove Last", width=100, command=self._remove_sid).pack(side="left", padx=3)

        # --- Control ---
        sec = SectionFrame(parent, "Control Parameters", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content

        self._admin_restrictions = LabeledOptionMenu(c, "ADMIN_RESTRICTIONS:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._admin_restrictions.pack(fill="x", pady=2)
        self._default_service = LabeledEntry(c, "DEFAULT_SERVICE:", on_change=self._schedule_preview)
        self._default_service.pack(fill="x", pady=2)
        self._dynamic_registration = LabeledOptionMenu(c, "DYNAMIC_REGISTRATION:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._dynamic_registration.pack(fill="x", pady=2)
        self._inbound_connect_timeout = LabeledEntry(c, "INBOUND_CONNECT_TIMEOUT:", placeholder="60", on_change=self._schedule_preview)
        self._inbound_connect_timeout.pack(fill="x", pady=2)
        self._max_all_connections = LabeledEntry(c, "MAX_ALL_CONNECTIONS:", on_change=self._schedule_preview)
        self._max_all_connections.pack(fill="x", pady=2)
        self._max_reg_connections = LabeledEntry(c, "MAX_REG_CONNECTIONS:", on_change=self._schedule_preview)
        self._max_reg_connections.pack(fill="x", pady=2)
        self._save_config_on_stop = LabeledOptionMenu(c, "SAVE_CONFIG_ON_STOP:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._save_config_on_stop.pack(fill="x", pady=2)
        self._use_sid_as_service = LabeledOptionMenu(c, "USE_SID_AS_SERVICE:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._use_sid_as_service.pack(fill="x", pady=2)
        self._dedicated_through_broker = LabeledOptionMenu(c, "DEDICATED_THROUGH_BROKER:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._dedicated_through_broker.pack(fill="x", pady=2)
        self._allow_multiple_redirects = LabeledOptionMenu(c, "ALLOW_MULTIPLE_REDIRECTS:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._allow_multiple_redirects.pack(fill="x", pady=2)
        self._crs_notification = LabeledOptionMenu(c, "CRS_NOTIFICATION:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._crs_notification.pack(fill="x", pady=2)
        self._enable_exadirect = LabeledOptionMenu(c, "ENABLE_EXADIRECT:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._enable_exadirect.pack(fill="x", pady=2)
        self._subscribe_node_down = LabeledOptionMenu(c, "SUBSCRIBE_FOR_NODE_DOWN:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._subscribe_node_down.pack(fill="x", pady=2)

        # --- Rate Limiting ---
        sec = SectionFrame(parent, "Rate Limiting", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content

        self._connection_rate = LabeledEntry(c, "CONNECTION_RATE:", on_change=self._schedule_preview)
        self._connection_rate.pack(fill="x", pady=2)
        self._service_rate = LabeledEntry(c, "SERVICE_RATE:", on_change=self._schedule_preview)
        self._service_rate.pack(fill="x", pady=2)

        # --- Security ---
        sec = SectionFrame(parent, "Security", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content

        self._valid_node_checking = LabeledOptionMenu(c, "VALID_NODE_CHECKING_REG:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._valid_node_checking.pack(fill="x", pady=2)
        self._reg_invited_nodes = LabeledEntry(c, "REGISTRATION_INVITED_NODES:", on_change=self._schedule_preview)
        self._reg_invited_nodes.pack(fill="x", pady=2)
        self._reg_excluded_nodes = LabeledEntry(c, "REGISTRATION_EXCLUDED_NODES:", on_change=self._schedule_preview)
        self._reg_excluded_nodes.pack(fill="x", pady=2)
        self._local_reg_addr = LabeledEntry(c, "LOCAL_REGISTRATION_ADDR:", on_change=self._schedule_preview)
        self._local_reg_addr.pack(fill="x", pady=2)
        self._remote_reg_addr = LabeledEntry(c, "REMOTE_REGISTRATION_ADDR:", on_change=self._schedule_preview)
        self._remote_reg_addr.pack(fill="x", pady=2)
        self._secure_register = LabeledEntry(c, "SECURE_REGISTER:", on_change=self._schedule_preview)
        self._secure_register.pack(fill="x", pady=2)
        self._secure_protocol = LabeledEntry(c, "SECURE_PROTOCOL:", on_change=self._schedule_preview)
        self._secure_protocol.pack(fill="x", pady=2)
        self._secure_control = LabeledEntry(c, "SECURE_CONTROL:", on_change=self._schedule_preview)
        self._secure_control.pack(fill="x", pady=2)

        # --- SSL/TLS ---
        sec = SectionFrame(parent, "SSL/TLS", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content

        self._ssl_version = LabeledEntry(c, "SSL_VERSION:", on_change=self._schedule_preview)
        self._ssl_version.pack(fill="x", pady=2)
        self._ssl_client_auth = LabeledOptionMenu(c, "SSL_CLIENT_AUTH:", ["", "TRUE", "FALSE"], on_change=self._schedule_preview)
        self._ssl_client_auth.pack(fill="x", pady=2)
        self._ssl_cipher_suites = LabeledEntry(c, "SSL_CIPHER_SUITES:", on_change=self._schedule_preview)
        self._ssl_cipher_suites.pack(fill="x", pady=2)
        self._wallet_location = LabeledEntry(c, "WALLET_LOCATION:", on_change=self._schedule_preview)
        self._wallet_location.pack(fill="x", pady=2)

        # --- Diagnostics ---
        sec = SectionFrame(parent, "Diagnostics & Tracing", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content

        self._diag_adr_enabled = LabeledOptionMenu(c, "DIAG_ADR_ENABLED:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._diag_adr_enabled.pack(fill="x", pady=2)
        self._adr_base = LabeledEntry(c, "ADR_BASE:", on_change=self._schedule_preview)
        self._adr_base.pack(fill="x", pady=2)
        self._logging = LabeledOptionMenu(c, "LOGGING:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._logging.pack(fill="x", pady=2)
        self._log_file_num = LabeledEntry(c, "LOG_FILE_NUM:", on_change=self._schedule_preview)
        self._log_file_num.pack(fill="x", pady=2)
        self._log_file_size = LabeledEntry(c, "LOG_FILE_SIZE:", on_change=self._schedule_preview)
        self._log_file_size.pack(fill="x", pady=2)
        self._trace_level = LabeledOptionMenu(c, "TRACE_LEVEL:", ["", "OFF", "USER", "ADMIN", "SUPPORT"], on_change=self._schedule_preview)
        self._trace_level.pack(fill="x", pady=2)
        self._trace_timestamp = LabeledOptionMenu(c, "TRACE_TIMESTAMP:", ["", "ON", "OFF"], on_change=self._schedule_preview)
        self._trace_timestamp.pack(fill="x", pady=2)
        self._trace_directory = LabeledEntry(c, "TRACE_DIRECTORY:", on_change=self._schedule_preview)
        self._trace_directory.pack(fill="x", pady=2)
        self._trace_file = LabeledEntry(c, "TRACE_FILE:", on_change=self._schedule_preview)
        self._trace_file.pack(fill="x", pady=2)
        self._trace_fileage = LabeledEntry(c, "TRACE_FILEAGE:", on_change=self._schedule_preview)
        self._trace_fileage.pack(fill="x", pady=2)
        self._trace_filelen = LabeledEntry(c, "TRACE_FILELEN:", on_change=self._schedule_preview)
        self._trace_filelen.pack(fill="x", pady=2)
        self._trace_fileno = LabeledEntry(c, "TRACE_FILENO:", on_change=self._schedule_preview)
        self._trace_fileno.pack(fill="x", pady=2)
        self._log_directory = LabeledEntry(c, "LOG_DIRECTORY:", on_change=self._schedule_preview)
        self._log_directory.pack(fill="x", pady=2)
        self._log_file = LabeledEntry(c, "LOG_FILE:", on_change=self._schedule_preview)
        self._log_file.pack(fill="x", pady=2)

    # --- Address management ---
    def _refresh_addr_display(self):
        for w in self._addr_list_frame.winfo_children():
            w.destroy()
        for i, addr in enumerate(self._addresses):
            proto = get_protocol_name(addr)
            if isinstance(addr, (TCPAddress, TCPSAddress)):
                text = f"{proto} - {addr.host}:{addr.port}"
            elif isinstance(addr, IPCAddress):
                text = f"IPC - KEY={addr.key}"
            elif isinstance(addr, NMPAddress):
                text = f"NMP - PIPE={addr.pipe}"
            else:
                text = str(addr)
            row = ctk.CTkFrame(self._addr_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=text, anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="Edit", width=50, command=lambda idx=i: self._edit_address(idx)).pack(side="right", padx=2)
        self._update_preview()

    def _add_address(self):
        dialog = AddressDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self._addresses.append(dialog.result)
            self._refresh_addr_display()

    def _edit_address(self, index: int):
        dialog = AddressDialog(self, self._addresses[index])
        self.wait_window(dialog)
        if dialog.result:
            self._addresses[index] = dialog.result
            self._refresh_addr_display()

    def _remove_address(self):
        if self._addresses:
            self._addresses.pop()
            self._refresh_addr_display()

    # --- SID management ---
    def _refresh_sid_display(self):
        for w in self._sid_list_frame.winfo_children():
            w.destroy()
        for i, sid in enumerate(self._sid_list):
            row = ctk.CTkFrame(self._sid_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=sid.display_name(), anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="Edit", width=50, command=lambda idx=i: self._edit_sid(idx)).pack(side="right", padx=2)
        self._update_preview()

    def _add_sid(self):
        dialog = SIDDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self._sid_list.append(dialog.result)
            self._refresh_sid_display()

    def _edit_sid(self, index: int):
        dialog = SIDDialog(self, self._sid_list[index])
        self.wait_window(dialog)
        if dialog.result:
            self._sid_list[index] = dialog.result
            self._refresh_sid_display()

    def _remove_sid(self):
        if self._sid_list:
            self._sid_list.pop()
            self._refresh_sid_display()

    # --- Model building ---
    def _build_model(self) -> ListenerConfig:
        return ListenerConfig(
            name=self._name.get() or "LISTENER",
            addresses=list(self._addresses),
            sid_list=list(self._sid_list),
            admin_restrictions=self._admin_restrictions.get(),
            default_service=self._default_service.get(),
            dynamic_registration=self._dynamic_registration.get(),
            inbound_connect_timeout=self._inbound_connect_timeout.get(),
            max_all_connections=self._max_all_connections.get(),
            max_reg_connections=self._max_reg_connections.get(),
            save_config_on_stop=self._save_config_on_stop.get(),
            use_sid_as_service=self._use_sid_as_service.get(),
            dedicated_through_broker=self._dedicated_through_broker.get(),
            allow_multiple_redirects=self._allow_multiple_redirects.get(),
            crs_notification=self._crs_notification.get(),
            enable_exadirect=self._enable_exadirect.get(),
            subscribe_for_node_down_event=self._subscribe_node_down.get(),
            connection_rate=self._connection_rate.get(),
            service_rate=self._service_rate.get(),
            valid_node_checking_registration=self._valid_node_checking.get(),
            registration_invited_nodes=self._reg_invited_nodes.get(),
            registration_excluded_nodes=self._reg_excluded_nodes.get(),
            local_registration_address=self._local_reg_addr.get(),
            remote_registration_address=self._remote_reg_addr.get(),
            secure_register=self._secure_register.get(),
            secure_protocol=self._secure_protocol.get(),
            secure_control=self._secure_control.get(),
            ssl_version=self._ssl_version.get(),
            ssl_client_authentication=self._ssl_client_auth.get(),
            ssl_cipher_suites=self._ssl_cipher_suites.get(),
            wallet_location=self._wallet_location.get(),
            diag_adr_enabled=self._diag_adr_enabled.get(),
            adr_base=self._adr_base.get(),
            logging=self._logging.get(),
            log_file_num=self._log_file_num.get(),
            log_file_size=self._log_file_size.get(),
            trace_level=self._trace_level.get(),
            trace_timestamp=self._trace_timestamp.get(),
            trace_directory=self._trace_directory.get(),
            trace_file=self._trace_file.get(),
            trace_fileage=self._trace_fileage.get(),
            trace_filelen=self._trace_filelen.get(),
            trace_fileno=self._trace_fileno.get(),
            log_directory=self._log_directory.get(),
            log_file=self._log_file.get(),
        )

    def _populate_from_model(self, config: ListenerConfig):
        self._name.set(config.name)
        self._addresses = list(config.addresses)
        self._sid_list = list(config.sid_list)
        self._refresh_addr_display()
        self._refresh_sid_display()

        self._admin_restrictions.set(config.admin_restrictions)
        self._default_service.set(config.default_service)
        self._dynamic_registration.set(config.dynamic_registration)
        self._inbound_connect_timeout.set(config.inbound_connect_timeout)
        self._max_all_connections.set(config.max_all_connections)
        self._max_reg_connections.set(config.max_reg_connections)
        self._save_config_on_stop.set(config.save_config_on_stop)
        self._use_sid_as_service.set(config.use_sid_as_service)
        self._dedicated_through_broker.set(config.dedicated_through_broker)
        self._allow_multiple_redirects.set(config.allow_multiple_redirects)
        self._crs_notification.set(config.crs_notification)
        self._enable_exadirect.set(config.enable_exadirect)
        self._subscribe_node_down.set(config.subscribe_for_node_down_event)

        self._connection_rate.set(config.connection_rate)
        self._service_rate.set(config.service_rate)

        self._valid_node_checking.set(config.valid_node_checking_registration)
        self._reg_invited_nodes.set(config.registration_invited_nodes)
        self._reg_excluded_nodes.set(config.registration_excluded_nodes)
        self._local_reg_addr.set(config.local_registration_address)
        self._remote_reg_addr.set(config.remote_registration_address)
        self._secure_register.set(config.secure_register)
        self._secure_protocol.set(config.secure_protocol)
        self._secure_control.set(config.secure_control)

        self._ssl_version.set(config.ssl_version)
        self._ssl_client_auth.set(config.ssl_client_authentication)
        self._ssl_cipher_suites.set(config.ssl_cipher_suites)
        self._wallet_location.set(config.wallet_location)

        self._diag_adr_enabled.set(config.diag_adr_enabled)
        self._adr_base.set(config.adr_base)
        self._logging.set(config.logging)
        self._log_file_num.set(config.log_file_num)
        self._log_file_size.set(config.log_file_size)
        self._trace_level.set(config.trace_level)
        self._trace_timestamp.set(config.trace_timestamp)
        self._trace_directory.set(config.trace_directory)
        self._trace_file.set(config.trace_file)
        self._trace_fileage.set(config.trace_fileage)
        self._trace_filelen.set(config.trace_filelen)
        self._trace_fileno.set(config.trace_fileno)
        self._log_directory.set(config.log_directory)
        self._log_file.set(config.log_file)

        self._update_preview()

    # --- Preview ---
    def _schedule_preview(self, *_args):
        """Debounced preview update - waits 300ms after last change."""
        if self._preview_job is not None:
            self.after_cancel(self._preview_job)
        self._preview_job = self.after(300, self._update_preview)

    def _update_preview(self):
        self._preview_job = None
        try:
            model = self._build_model()
            text = self._generator.generate(model)
            self._preview.set_text(text)
        except Exception:
            pass

    def get_preview_text(self) -> str:
        return self._preview.get_text()

    # --- Actions ---
    def _do_import(self):
        path = open_ora_file("Import listener.ora")
        if path:
            try:
                text = read_file(path)
                ast = parse_ora(text)
                config = ListenerConfig.from_ast(ast)
                self._populate_from_model(config)
            except Exception as e:
                ctk.CTkInputDialog(text=f"Error importing: {e}", title="Import Error")

    def _do_export(self):
        path = save_ora_file("Export listener.ora", "listener.ora")
        if path:
            try:
                model = self._build_model()
                text = self._generator.generate(model)
                write_file(path, text)
            except Exception as e:
                ctk.CTkInputDialog(text=f"Error exporting: {e}", title="Export Error")

    def _do_copy(self):
        text = self.get_preview_text()
        if text:
            copy_to_clipboard(self, text)

    def _do_clear(self):
        self._populate_from_model(ListenerConfig())
