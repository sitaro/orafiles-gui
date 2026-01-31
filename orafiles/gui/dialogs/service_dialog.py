"""Dialog for editing a TNS net service entry."""

from __future__ import annotations
import copy
import customtkinter as ctk
from orafiles.models.tnsnames import ServiceEntry, ConnectData, FailoverMode, DescriptionSecurity
from orafiles.models.protocol_address import (
    TCPAddress, TCPSAddress, IPCAddress, NMPAddress, Address, get_protocol_name
)
from orafiles.gui.widgets.labeled_entry import LabeledEntry
from orafiles.gui.widgets.labeled_optionmenu import LabeledOptionMenu
from orafiles.gui.widgets.section_frame import SectionFrame
from orafiles.gui.dialogs.address_dialog import AddressDialog


class ServiceDialog(ctk.CTkToplevel):
    """Dialog to create or edit a TNS service entry."""

    def __init__(self, master, service: ServiceEntry | None = None):
        super().__init__(master)
        self.title("Edit Net Service")
        self.geometry("600x700")
        self.resizable(True, True)
        self.grab_set()

        self.result: ServiceEntry | None = None
        self._addresses: list[Address] = list(service.addresses) if service else []

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # Service Name
        self._name = LabeledEntry(scroll, "Service Name:")
        self._name.pack(fill="x", pady=3)

        # --- Addresses Section ---
        addr_sec = SectionFrame(scroll, "Addresses")
        addr_sec.pack(fill="x", pady=5)

        self._addr_list_frame = ctk.CTkFrame(addr_sec.content, fg_color="transparent")
        self._addr_list_frame.pack(fill="x")

        addr_btn_frame = ctk.CTkFrame(addr_sec.content, fg_color="transparent")
        addr_btn_frame.pack(fill="x", pady=3)
        ctk.CTkButton(addr_btn_frame, text="Add Address", width=100, command=self._add_address).pack(side="left", padx=3)
        ctk.CTkButton(addr_btn_frame, text="Remove Last", width=100, command=self._remove_address).pack(side="left", padx=3)

        self._addr_list_fo = LabeledOptionMenu(addr_sec.content, "Address List Failover:", ["", "ON", "OFF"])
        self._addr_list_fo.pack(fill="x", pady=2)
        self._addr_list_lb = LabeledOptionMenu(addr_sec.content, "Address List Load Balance:", ["", "ON", "OFF"])
        self._addr_list_lb.pack(fill="x", pady=2)

        # --- Connect Data Section ---
        cd_sec = SectionFrame(scroll, "Connect Data")
        cd_sec.pack(fill="x", pady=5)
        c = cd_sec.content

        self._service_name = LabeledEntry(c, "SERVICE_NAME:")
        self._service_name.pack(fill="x", pady=2)
        self._sid = LabeledEntry(c, "SID:")
        self._sid.pack(fill="x", pady=2)
        self._instance_name = LabeledEntry(c, "INSTANCE_NAME:")
        self._instance_name.pack(fill="x", pady=2)
        self._server = LabeledOptionMenu(c, "SERVER:", ["", "DEDICATED", "SHARED", "POOLED"])
        self._server.pack(fill="x", pady=2)
        self._hs = LabeledOptionMenu(c, "HS:", ["", "OK"])
        self._hs.pack(fill="x", pady=2)
        self._global_name = LabeledEntry(c, "GLOBAL_NAME:")
        self._global_name.pack(fill="x", pady=2)
        self._rdb_database = LabeledEntry(c, "RDB_DATABASE:")
        self._rdb_database.pack(fill="x", pady=2)
        self._colocation_tag = LabeledEntry(c, "COLOCATION_TAG:")
        self._colocation_tag.pack(fill="x", pady=2)
        self._conn_id_prefix = LabeledEntry(c, "CONNECTION_ID_PREFIX:")
        self._conn_id_prefix.pack(fill="x", pady=2)
        self._pool_class = LabeledEntry(c, "POOL_CONNECTION_CLASS:")
        self._pool_class.pack(fill="x", pady=2)
        self._pool_purity = LabeledOptionMenu(c, "POOL_PURITY:", ["", "NEW", "SELF"])
        self._pool_purity.pack(fill="x", pady=2)
        self._server_wait = LabeledEntry(c, "SERVER_WAIT_TIMEOUT:")
        self._server_wait.pack(fill="x", pady=2)
        self._sharding = LabeledEntry(c, "SHARDING_KEY:")
        self._sharding.pack(fill="x", pady=2)
        self._super_sharding = LabeledEntry(c, "SUPER_SHARDING_KEY:")
        self._super_sharding.pack(fill="x", pady=2)
        self._tunnel_svc = LabeledEntry(c, "TUNNEL_SERVICE_NAME:")
        self._tunnel_svc.pack(fill="x", pady=2)

        # --- Failover Mode ---
        fo_sec = SectionFrame(scroll, "Failover Mode", expanded=False)
        fo_sec.pack(fill="x", pady=5)
        f = fo_sec.content

        self._fo_type = LabeledOptionMenu(f, "TYPE:", ["", "NONE", "SESSION", "SELECT", "TRANSACTION"])
        self._fo_type.pack(fill="x", pady=2)
        self._fo_method = LabeledOptionMenu(f, "METHOD:", ["", "NONE", "BASIC", "PRECONNECT"])
        self._fo_method.pack(fill="x", pady=2)
        self._fo_backup = LabeledEntry(f, "BACKUP:")
        self._fo_backup.pack(fill="x", pady=2)
        self._fo_retries = LabeledEntry(f, "RETRIES:")
        self._fo_retries.pack(fill="x", pady=2)
        self._fo_delay = LabeledEntry(f, "DELAY:")
        self._fo_delay.pack(fill="x", pady=2)

        # --- Description Options ---
        desc_sec = SectionFrame(scroll, "Description Options", expanded=False)
        desc_sec.pack(fill="x", pady=5)
        d = desc_sec.content

        self._desc_failover = LabeledOptionMenu(d, "FAILOVER:", ["", "ON", "OFF"])
        self._desc_failover.pack(fill="x", pady=2)
        self._desc_lb = LabeledOptionMenu(d, "LOAD_BALANCE:", ["", "ON", "OFF"])
        self._desc_lb.pack(fill="x", pady=2)
        self._sdu = LabeledEntry(d, "SDU:")
        self._sdu.pack(fill="x", pady=2)
        self._enable = LabeledEntry(d, "ENABLE:")
        self._enable.pack(fill="x", pady=2)
        self._expire_time = LabeledEntry(d, "EXPIRE_TIME:")
        self._expire_time.pack(fill="x", pady=2)
        self._recv_buf = LabeledEntry(d, "RECV_BUF_SIZE:")
        self._recv_buf.pack(fill="x", pady=2)
        self._send_buf = LabeledEntry(d, "SEND_BUF_SIZE:")
        self._send_buf.pack(fill="x", pady=2)
        self._type_of_service = LabeledEntry(d, "TYPE_OF_SERVICE:")
        self._type_of_service.pack(fill="x", pady=2)
        self._https_proxy = LabeledEntry(d, "HTTPS_PROXY:")
        self._https_proxy.pack(fill="x", pady=2)
        self._https_proxy_port = LabeledEntry(d, "HTTPS_PROXY_PORT:")
        self._https_proxy_port.pack(fill="x", pady=2)

        # --- Timeouts ---
        to_sec = SectionFrame(scroll, "Timeouts", expanded=False)
        to_sec.pack(fill="x", pady=5)
        t = to_sec.content

        self._connect_timeout = LabeledEntry(t, "CONNECT_TIMEOUT:")
        self._connect_timeout.pack(fill="x", pady=2)
        self._retry_count = LabeledEntry(t, "RETRY_COUNT:")
        self._retry_count.pack(fill="x", pady=2)
        self._retry_delay = LabeledEntry(t, "RETRY_DELAY:")
        self._retry_delay.pack(fill="x", pady=2)
        self._transport_timeout = LabeledEntry(t, "TRANSPORT_CONNECT_TIMEOUT:")
        self._transport_timeout.pack(fill="x", pady=2)
        self._recv_timeout = LabeledEntry(t, "RECV_TIMEOUT:")
        self._recv_timeout.pack(fill="x", pady=2)

        # --- Security ---
        sec_sec = SectionFrame(scroll, "Security", expanded=False)
        sec_sec.pack(fill="x", pady=5)
        sc = sec_sec.content

        self._auth_svc = LabeledEntry(sc, "AUTHENTICATION_SERVICE:")
        self._auth_svc.pack(fill="x", pady=2)
        self._ssl_cert_dn = LabeledEntry(sc, "SSL_SERVER_CERT_DN:")
        self._ssl_cert_dn.pack(fill="x", pady=2)
        self._ssl_dn_match = LabeledOptionMenu(sc, "SSL_SERVER_DN_MATCH:", ["", "ON", "OFF"])
        self._ssl_dn_match.pack(fill="x", pady=2)
        self._sec_ssl_version = LabeledEntry(sc, "SSL_VERSION:")
        self._sec_ssl_version.pack(fill="x", pady=2)
        self._sec_wallet = LabeledEntry(sc, "WALLET_LOCATION:")
        self._sec_wallet.pack(fill="x", pady=2)
        self._krb_cc = LabeledEntry(sc, "KERBEROS5_CC_NAME:")
        self._krb_cc.pack(fill="x", pady=2)
        self._krb_principal = LabeledEntry(sc, "KERBEROS5_PRINCIPAL:")
        self._krb_principal.pack(fill="x", pady=2)
        self._ignore_ano = LabeledOptionMenu(sc, "IGNORE_ANO_ENCRYPTION:", ["", "ON", "OFF"])
        self._ignore_ano.pack(fill="x", pady=2)

        # --- Compression ---
        comp_sec = SectionFrame(scroll, "Compression", expanded=False)
        comp_sec.pack(fill="x", pady=5)
        cp = comp_sec.content

        self._compression = LabeledOptionMenu(cp, "COMPRESSION:", ["", "ON", "OFF"])
        self._compression.pack(fill="x", pady=2)
        self._comp_levels = LabeledOptionMenu(cp, "COMPRESSION_LEVELS:", ["", "LOW", "HIGH"])
        self._comp_levels.pack(fill="x", pady=2)

        # Populate if editing
        if service:
            self._populate(service)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="OK", width=80, command=self._ok).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", width=80, command=self._cancel).pack(side="right", padx=5)

        self._refresh_addr_list()

    def _refresh_addr_list(self):
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
            ctk.CTkButton(
                row, text="Edit", width=50,
                command=lambda idx=i: self._edit_address(idx)
            ).pack(side="right", padx=2)

    def _add_address(self):
        dialog = AddressDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self._addresses.append(dialog.result)
            self._refresh_addr_list()

    def _edit_address(self, index: int):
        dialog = AddressDialog(self, self._addresses[index])
        self.wait_window(dialog)
        if dialog.result:
            self._addresses[index] = dialog.result
            self._refresh_addr_list()

    def _remove_address(self):
        if self._addresses:
            self._addresses.pop()
            self._refresh_addr_list()

    def _populate(self, svc: ServiceEntry):
        self._name.set(svc.name)
        self._addr_list_fo.set(svc.address_list_failover)
        self._addr_list_lb.set(svc.address_list_load_balance)

        cd = svc.connect_data
        self._service_name.set(cd.service_name)
        self._sid.set(cd.sid)
        self._instance_name.set(cd.instance_name)
        self._server.set(cd.server)
        self._hs.set(cd.hs)
        self._global_name.set(cd.global_name)
        self._rdb_database.set(cd.rdb_database)
        self._colocation_tag.set(cd.colocation_tag)
        self._conn_id_prefix.set(cd.connection_id_prefix)
        self._pool_class.set(cd.pool_connection_class)
        self._pool_purity.set(cd.pool_purity)
        self._server_wait.set(cd.server_wait_timeout)
        self._sharding.set(cd.sharding_key)
        self._super_sharding.set(cd.super_sharding_key)
        self._tunnel_svc.set(cd.tunnel_service_name)

        fm = cd.failover_mode
        self._fo_type.set(fm.type)
        self._fo_method.set(fm.method)
        self._fo_backup.set(fm.backup)
        self._fo_retries.set(fm.retries)
        self._fo_delay.set(fm.delay)

        self._desc_failover.set(svc.failover)
        self._desc_lb.set(svc.load_balance)
        self._sdu.set(svc.sdu)
        self._enable.set(svc.enable)
        self._expire_time.set(svc.expire_time)
        self._recv_buf.set(svc.recv_buf_size)
        self._send_buf.set(svc.send_buf_size)
        self._type_of_service.set(svc.type_of_service)
        self._https_proxy.set(svc.https_proxy)
        self._https_proxy_port.set(svc.https_proxy_port)

        self._connect_timeout.set(svc.connect_timeout)
        self._retry_count.set(svc.retry_count)
        self._retry_delay.set(svc.retry_delay)
        self._transport_timeout.set(svc.transport_connect_timeout)
        self._recv_timeout.set(svc.recv_timeout)

        sec = svc.security
        self._auth_svc.set(sec.authentication_service)
        self._ssl_cert_dn.set(sec.ssl_server_cert_dn)
        self._ssl_dn_match.set(sec.ssl_server_dn_match)
        self._sec_ssl_version.set(sec.ssl_version)
        self._sec_wallet.set(sec.wallet_location)
        self._krb_cc.set(sec.kerberos5_cc_name)
        self._krb_principal.set(sec.kerberos5_principal)
        self._ignore_ano.set(sec.ignore_ano_encryption_for_tcps)

        self._compression.set(svc.compression)
        self._comp_levels.set(svc.compression_levels)

    def _ok(self):
        self.result = ServiceEntry(
            name=self._name.get(),
            addresses=list(self._addresses),
            address_list_failover=self._addr_list_fo.get(),
            address_list_load_balance=self._addr_list_lb.get(),
            connect_data=ConnectData(
                service_name=self._service_name.get(),
                sid=self._sid.get(),
                instance_name=self._instance_name.get(),
                server=self._server.get(),
                hs=self._hs.get(),
                global_name=self._global_name.get(),
                rdb_database=self._rdb_database.get(),
                colocation_tag=self._colocation_tag.get(),
                connection_id_prefix=self._conn_id_prefix.get(),
                pool_connection_class=self._pool_class.get(),
                pool_purity=self._pool_purity.get(),
                server_wait_timeout=self._server_wait.get(),
                sharding_key=self._sharding.get(),
                super_sharding_key=self._super_sharding.get(),
                tunnel_service_name=self._tunnel_svc.get(),
                failover_mode=FailoverMode(
                    type=self._fo_type.get(),
                    method=self._fo_method.get(),
                    backup=self._fo_backup.get(),
                    retries=self._fo_retries.get(),
                    delay=self._fo_delay.get(),
                ),
            ),
            security=DescriptionSecurity(
                authentication_service=self._auth_svc.get(),
                ssl_server_cert_dn=self._ssl_cert_dn.get(),
                ssl_server_dn_match=self._ssl_dn_match.get(),
                ssl_version=self._sec_ssl_version.get(),
                wallet_location=self._sec_wallet.get(),
                kerberos5_cc_name=self._krb_cc.get(),
                kerberos5_principal=self._krb_principal.get(),
                ignore_ano_encryption_for_tcps=self._ignore_ano.get(),
            ),
            failover=self._desc_failover.get(),
            load_balance=self._desc_lb.get(),
            sdu=self._sdu.get(),
            enable=self._enable.get(),
            expire_time=self._expire_time.get(),
            recv_buf_size=self._recv_buf.get(),
            send_buf_size=self._send_buf.get(),
            type_of_service=self._type_of_service.get(),
            https_proxy=self._https_proxy.get(),
            https_proxy_port=self._https_proxy_port.get(),
            connect_timeout=self._connect_timeout.get(),
            retry_count=self._retry_count.get(),
            retry_delay=self._retry_delay.get(),
            transport_connect_timeout=self._transport_timeout.get(),
            recv_timeout=self._recv_timeout.get(),
            compression=self._compression.get(),
            compression_levels=self._comp_levels.get(),
        )
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
