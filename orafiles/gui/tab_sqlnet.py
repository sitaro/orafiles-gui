"""sqlnet.ora tab implementation."""

from __future__ import annotations
import customtkinter as ctk

from orafiles.models.sqlnet import SQLNetConfig
from orafiles.generators.sqlnet_gen import SQLNetGenerator
from orafiles.parser.parser import parse_ora
from orafiles.gui.preview_panel import PreviewPanel
from orafiles.gui.widgets.labeled_entry import LabeledEntry
from orafiles.gui.widgets.labeled_optionmenu import LabeledOptionMenu
from orafiles.gui.widgets.section_frame import SectionFrame
from orafiles.gui.widgets.toolbar import Toolbar
from orafiles.gui.dialogs.file_dialogs import open_ora_file, save_ora_file
from orafiles.utils.file_io import read_file, write_file
from orafiles.utils.clipboard import copy_to_clipboard


def _entry(parent, label, placeholder="", on_change=None):
    w = LabeledEntry(parent, label, placeholder=placeholder, on_change=on_change)
    w.pack(fill="x", pady=2)
    return w


def _option(parent, label, values, on_change=None):
    w = LabeledOptionMenu(parent, label, values, on_change=on_change)
    w.pack(fill="x", pady=2)
    return w


class SQLNetTab(ctk.CTkFrame):
    """Tab for editing sqlnet.ora configuration."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._generator = SQLNetGenerator()
        self._preview_job = None
        self._build_ui()

    def _build_ui(self):
        toolbar = Toolbar(
            self,
            on_import=self._do_import,
            on_export=self._do_export,
            on_copy=self._do_copy,
            on_clear=self._do_clear,
        )
        toolbar.pack(fill="x", padx=5, pady=5)

        pane = ctk.CTkFrame(self, fg_color="transparent")
        pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=3)
        pane.columnconfigure(1, weight=2)
        pane.rowconfigure(0, weight=1)

        form_scroll = ctk.CTkScrollableFrame(pane)
        form_scroll.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        self._preview = PreviewPanel(pane, title="sqlnet.ora Preview")
        self._preview.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)

        oc = self._schedule_preview

        # --- Naming ---
        sec = SectionFrame(form_scroll, "Naming")
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._names_default_domain = _entry(c, "NAMES.DEFAULT_DOMAIN:", on_change=oc)
        self._names_directory_path = _entry(c, "NAMES.DIRECTORY_PATH:", placeholder="TNSNAMES, LDAP, EZCONNECT", on_change=oc)
        self._names_ldap_attr = _entry(c, "NAMES.LDAP_ATTR:", on_change=oc)
        self._names_ldap_auth_bind = _entry(c, "NAMES.LDAP_AUTHENTICATE_BIND:", on_change=oc)
        self._names_ldap_persistent = _entry(c, "NAMES.LDAP_PERSISTENT_SESSION:", on_change=oc)

        # --- Encryption ---
        sec = SectionFrame(form_scroll, "Encryption", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        enc_levels = ["", "ACCEPTED", "REJECTED", "REQUESTED", "REQUIRED"]
        self._enc_client = _option(c, "ENCRYPTION_CLIENT:", enc_levels, on_change=oc)
        self._enc_types_client = _entry(c, "ENCRYPTION_TYPES_CLIENT:", placeholder="AES256, AES192", on_change=oc)
        self._enc_server = _option(c, "ENCRYPTION_SERVER:", enc_levels, on_change=oc)
        self._enc_types_server = _entry(c, "ENCRYPTION_TYPES_SERVER:", placeholder="AES256, AES192", on_change=oc)
        self._allow_weak = _option(c, "ALLOW_WEAK_CRYPTO:", ["", "TRUE", "FALSE"], on_change=oc)

        # --- Integrity ---
        sec = SectionFrame(form_scroll, "Integrity", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        chk_levels = ["", "ACCEPTED", "REJECTED", "REQUESTED", "REQUIRED"]
        self._chk_client = _option(c, "CRYPTO_CHECKSUM_CLIENT:", chk_levels, on_change=oc)
        self._chk_types_client = _entry(c, "CHECKSUM_TYPES_CLIENT:", placeholder="SHA256, SHA384", on_change=oc)
        self._chk_server = _option(c, "CRYPTO_CHECKSUM_SERVER:", chk_levels, on_change=oc)
        self._chk_types_server = _entry(c, "CHECKSUM_TYPES_SERVER:", placeholder="SHA256, SHA384", on_change=oc)

        # --- SSL/TLS ---
        sec = SectionFrame(form_scroll, "SSL/TLS", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._ssl_version = _entry(c, "SSL_VERSION:", placeholder="1.2", on_change=oc)
        self._ssl_client_auth = _option(c, "SSL_CLIENT_AUTH:", ["", "TRUE", "FALSE"], on_change=oc)
        self._ssl_cipher_suites = _entry(c, "SSL_CIPHER_SUITES:", on_change=oc)
        self._ssl_dn_match = _option(c, "SSL_SERVER_DN_MATCH:", ["", "ON", "OFF"], on_change=oc)
        self._ssl_cert_dn = _entry(c, "SSL_SERVER_CERT_DN:", on_change=oc)
        self._ssl_crl_file = _entry(c, "SSL_CRL_FILE:", on_change=oc)
        self._ssl_crl_path = _entry(c, "SSL_CRL_PATH:", on_change=oc)
        self._ssl_ec_curves = _entry(c, "SSL_EC_CURVES:", on_change=oc)
        self._ssl_md5 = _option(c, "SSL_ALLOW_MD5_CERTS:", ["", "TRUE", "FALSE"], on_change=oc)
        self._ssl_sha1 = _option(c, "SSL_ALLOW_SHA1_CERTS:", ["", "TRUE", "FALSE"], on_change=oc)
        self._ssl_ext_key = _entry(c, "SSL_EXTENDED_KEY_USAGE:", on_change=oc)

        # --- Authentication ---
        sec = SectionFrame(form_scroll, "Authentication", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._auth_services = _entry(c, "AUTHENTICATION_SERVICES:", placeholder="ALL, NTS, KERBEROS5", on_change=oc)
        self._logon_version_client = _option(c, "LOGON_VERSION_CLIENT:", ["", "8", "10", "11", "12", "12a"], on_change=oc)
        self._logon_version_server = _option(c, "LOGON_VERSION_SERVER:", ["", "8", "10", "11", "12", "12a"], on_change=oc)
        self._fallback_auth = _option(c, "FALLBACK_AUTHENTICATION:", ["", "TRUE", "FALSE"], on_change=oc)
        self._password_auth = _entry(c, "PASSWORD_AUTH:", on_change=oc)

        # --- Kerberos ---
        sec = SectionFrame(form_scroll, "Kerberos", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._krb_cc = _entry(c, "KERBEROS5_CC_NAME:", on_change=oc)
        self._krb_conf = _entry(c, "KERBEROS5_CONF:", on_change=oc)
        self._krb_clockskew = _entry(c, "KERBEROS5_CLOCKSKEW:", on_change=oc)
        self._krb_keytab = _entry(c, "KERBEROS5_KEYTAB:", on_change=oc)
        self._krb_realms = _entry(c, "KERBEROS5_REALMS:", on_change=oc)
        self._krb_delegation = _option(c, "KERBEROS5_DELEGATION:", ["", "FULL", "CONSTRAINED"], on_change=oc)
        self._krb_service = _entry(c, "KERBEROS5_SERVICE:", on_change=oc)

        # --- RADIUS ---
        sec = SectionFrame(form_scroll, "RADIUS", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._radius_primary = _entry(c, "RADIUS_AUTHENTICATION:", on_change=oc)
        self._radius_primary_port = _entry(c, "RADIUS_AUTH_PORT:", on_change=oc)
        self._radius_alternate = _entry(c, "RADIUS_AUTH_ALTERNATE:", on_change=oc)
        self._radius_alternate_port = _entry(c, "RADIUS_ALT_PORT:", on_change=oc)
        self._radius_challenge = _option(c, "RADIUS_CHALLENGE:", ["", "TRUE", "FALSE"], on_change=oc)
        self._radius_secret = _entry(c, "RADIUS_SECRET:", on_change=oc)
        self._radius_accounting = _option(c, "RADIUS_SEND_ACCOUNTING:", ["", "ON", "OFF"], on_change=oc)

        # --- OCI/Cloud ---
        sec = SectionFrame(form_scroll, "OCI / Cloud", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._oci_iam = _entry(c, "OCI_IAM_URL:", on_change=oc)
        self._oci_tenancy = _entry(c, "OCI_TENANCY:", on_change=oc)
        self._oci_compartment = _entry(c, "OCI_COMPARTMENT:", on_change=oc)
        self._oci_database = _entry(c, "OCI_DATABASE:", on_change=oc)
        self._token_auth = _entry(c, "TOKEN_AUTH:", on_change=oc)
        self._token_location = _entry(c, "TOKEN_LOCATION:", on_change=oc)
        self._cloud_user = _entry(c, "CLOUD_USER:", on_change=oc)

        # --- Timeouts ---
        sec = SectionFrame(form_scroll, "Timeouts", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._expire_time = _entry(c, "EXPIRE_TIME:", placeholder="0", on_change=oc)
        self._outbound_timeout = _entry(c, "OUTBOUND_CONNECT_TIMEOUT:", on_change=oc)
        self._inbound_timeout = _entry(c, "INBOUND_CONNECT_TIMEOUT:", on_change=oc)
        self._recv_timeout = _entry(c, "RECV_TIMEOUT:", on_change=oc)
        self._send_timeout = _entry(c, "SEND_TIMEOUT:", on_change=oc)
        self._down_hosts_timeout = _entry(c, "DOWN_HOSTS_TIMEOUT:", on_change=oc)
        self._tcp_connect_timeout = _entry(c, "TCP.CONNECT_TIMEOUT:", on_change=oc)

        # --- Performance ---
        sec = SectionFrame(form_scroll, "Performance", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._default_sdu = _entry(c, "DEFAULT_SDU_SIZE:", placeholder="8192", on_change=oc)
        self._recv_buf = _entry(c, "RECV_BUF_SIZE:", on_change=oc)
        self._send_buf = _entry(c, "SEND_BUF_SIZE:", on_change=oc)
        self._max_conduits = _entry(c, "MAX_CONDUITS:", on_change=oc)

        # --- Compression ---
        sec = SectionFrame(form_scroll, "Compression", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._compression = _option(c, "COMPRESSION:", ["", "ON", "OFF"], on_change=oc)
        self._comp_levels = _entry(c, "COMPRESSION_LEVELS:", placeholder="LOW, HIGH", on_change=oc)
        self._comp_threshold = _entry(c, "COMPRESSION_THRESHOLD:", on_change=oc)
        self._comp_accel = _entry(c, "COMPRESSION_ACCELERATION:", on_change=oc)

        # --- TCP Access Control ---
        sec = SectionFrame(form_scroll, "TCP Access Control", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._tcp_validnode = _option(c, "VALIDNODE_CHECKING:", ["", "YES", "NO"], on_change=oc)
        self._tcp_invited = _entry(c, "TCP.INVITED_NODES:", on_change=oc)
        self._tcp_excluded = _entry(c, "TCP.EXCLUDED_NODES:", on_change=oc)
        self._tcp_nodelay = _option(c, "TCP.NODELAY:", ["", "YES", "NO"], on_change=oc)
        self._tcp_queuesize = _entry(c, "TCP.QUEUESIZE:", on_change=oc)

        # --- Advanced (IPC/SDP/Exadirect/OOB) ---
        sec = SectionFrame(form_scroll, "Advanced", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._ipc_keypath = _entry(c, "IPC.KEYPATH:", on_change=oc)
        self._sdp_pf = _entry(c, "SDP.PF_INET_SDP:", on_change=oc)
        self._exa_flow = _entry(c, "EXADIRECT_FLOW_CONTROL:", on_change=oc)
        self._exa_recvpoll = _entry(c, "EXADIRECT_RECVPOLL:", on_change=oc)
        self._disable_oob = _option(c, "DISABLE_OOB:", ["", "ON", "OFF"], on_change=oc)
        self._disable_oob_auto = _option(c, "DISABLE_OOB_AUTO:", ["", "TRUE", "FALSE"], on_change=oc)
        self._disable_interrupt = _option(c, "DISABLE_INTERRUPT:", ["", "TRUE", "FALSE"], on_change=oc)
        self._bequeath_detach = _option(c, "BEQUEATH_DETACH:", ["", "YES", "NO"], on_change=oc)

        # --- Wallet ---
        sec = SectionFrame(form_scroll, "Wallet", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._wallet_location = _entry(c, "WALLET_LOCATION:", on_change=oc)
        self._wallet_override = _option(c, "WALLET_OVERRIDE:", ["", "TRUE", "FALSE"], on_change=oc)
        self._enc_wallet_location = _entry(c, "ENCRYPTION_WALLET_LOCATION:", on_change=oc)

        # --- Security Banners ---
        sec = SectionFrame(form_scroll, "Security Banners", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._audit_banner = _entry(c, "AUDIT_ACTION_BANNER:", on_change=oc)
        self._unauth_banner = _entry(c, "UNAUTHORIZED_ACCESS_BANNER:", on_change=oc)

        # --- Misc ---
        sec = SectionFrame(form_scroll, "Miscellaneous", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._uri = _entry(c, "SQLNET.URI:", on_change=oc)
        self._use_https_proxy = _option(c, "USE_HTTPS_PROXY:", ["", "ON", "OFF"], on_change=oc)
        self._client_reg = _entry(c, "CLIENT_REGISTRATION:", on_change=oc)
        self._use_cman = _option(c, "USE_CMAN:", ["", "TRUE", "FALSE"], on_change=oc)
        self._use_dedicated = _option(c, "USE_DEDICATED_SERVER:", ["", "ON", "OFF"], on_change=oc)
        self._dbfw_key = _entry(c, "DBFW_PUBLIC_KEY:", on_change=oc)

        # --- Logging ---
        sec = SectionFrame(form_scroll, "Logging", expanded=False)
        sec.pack(fill="x", pady=3)
        c = sec.content
        self._tnsping_trace_level = _option(c, "TNSPING.TRACE_LEVEL:", ["", "OFF", "USER", "ADMIN", "SUPPORT"], on_change=oc)
        self._tnsping_trace_dir = _entry(c, "TNSPING.TRACE_DIRECTORY:", on_change=oc)

    def _build_model(self) -> SQLNetConfig:
        return SQLNetConfig(
            names_default_domain=self._names_default_domain.get(),
            names_directory_path=self._names_directory_path.get(),
            names_ldap_attr=self._names_ldap_attr.get(),
            names_ldap_authenticate_bind=self._names_ldap_auth_bind.get(),
            names_ldap_persistent_session=self._names_ldap_persistent.get(),
            sqlnet_encryption_client=self._enc_client.get(),
            sqlnet_encryption_types_client=self._enc_types_client.get(),
            sqlnet_encryption_server=self._enc_server.get(),
            sqlnet_encryption_types_server=self._enc_types_server.get(),
            sqlnet_allow_weak_crypto=self._allow_weak.get(),
            sqlnet_crypto_checksum_client=self._chk_client.get(),
            sqlnet_crypto_checksum_types_client=self._chk_types_client.get(),
            sqlnet_crypto_checksum_server=self._chk_server.get(),
            sqlnet_crypto_checksum_types_server=self._chk_types_server.get(),
            ssl_version=self._ssl_version.get(),
            ssl_client_authentication=self._ssl_client_auth.get(),
            ssl_cipher_suites=self._ssl_cipher_suites.get(),
            ssl_server_dn_match=self._ssl_dn_match.get(),
            ssl_server_cert_dn=self._ssl_cert_dn.get(),
            ssl_crl_file=self._ssl_crl_file.get(),
            ssl_crl_path=self._ssl_crl_path.get(),
            ssl_ec_curves=self._ssl_ec_curves.get(),
            ssl_allow_md5_certs=self._ssl_md5.get(),
            ssl_allow_sha1_certs=self._ssl_sha1.get(),
            ssl_extended_key_usage=self._ssl_ext_key.get(),
            sqlnet_authentication_services=self._auth_services.get(),
            sqlnet_allowed_logon_version_client=self._logon_version_client.get(),
            sqlnet_allowed_logon_version_server=self._logon_version_server.get(),
            sqlnet_fallback_authentication=self._fallback_auth.get(),
            sqlnet_password_auth=self._password_auth.get(),
            sqlnet_kerberos5_cc_name=self._krb_cc.get(),
            sqlnet_kerberos5_conf=self._krb_conf.get(),
            sqlnet_kerberos5_clockskew=self._krb_clockskew.get(),
            sqlnet_kerberos5_keytab=self._krb_keytab.get(),
            sqlnet_kerberos5_realms=self._krb_realms.get(),
            sqlnet_kerberos5_delegation_mode=self._krb_delegation.get(),
            sqlnet_kerberos5_service=self._krb_service.get(),
            sqlnet_radius_primary=self._radius_primary.get(),
            sqlnet_radius_primary_port=self._radius_primary_port.get(),
            sqlnet_radius_alternate=self._radius_alternate.get(),
            sqlnet_radius_alternate_port=self._radius_alternate_port.get(),
            sqlnet_radius_challenge=self._radius_challenge.get(),
            sqlnet_radius_secret=self._radius_secret.get(),
            sqlnet_radius_send_accounting=self._radius_accounting.get(),
            oci_iam_url=self._oci_iam.get(),
            oci_tenancy=self._oci_tenancy.get(),
            oci_compartment=self._oci_compartment.get(),
            oci_database=self._oci_database.get(),
            token_auth=self._token_auth.get(),
            token_location=self._token_location.get(),
            cloud_user=self._cloud_user.get(),
            sqlnet_expire_time=self._expire_time.get(),
            sqlnet_outbound_connect_timeout=self._outbound_timeout.get(),
            sqlnet_inbound_connect_timeout=self._inbound_timeout.get(),
            sqlnet_recv_timeout=self._recv_timeout.get(),
            sqlnet_send_timeout=self._send_timeout.get(),
            sqlnet_down_hosts_timeout=self._down_hosts_timeout.get(),
            tcp_connect_timeout=self._tcp_connect_timeout.get(),
            default_sdu_size=self._default_sdu.get(),
            recv_buf_size=self._recv_buf.get(),
            send_buf_size=self._send_buf.get(),
            max_conduits=self._max_conduits.get(),
            sqlnet_compression=self._compression.get(),
            sqlnet_compression_levels=self._comp_levels.get(),
            sqlnet_compression_threshold=self._comp_threshold.get(),
            sqlnet_compression_acceleration=self._comp_accel.get(),
            tcp_validnode_checking=self._tcp_validnode.get(),
            tcp_invited_nodes=self._tcp_invited.get(),
            tcp_excluded_nodes=self._tcp_excluded.get(),
            tcp_nodelay=self._tcp_nodelay.get(),
            tcp_queuesize=self._tcp_queuesize.get(),
            ipc_keypath=self._ipc_keypath.get(),
            sdp_pf_inet_sdp=self._sdp_pf.get(),
            exadirect_flow_control=self._exa_flow.get(),
            exadirect_recvpoll=self._exa_recvpoll.get(),
            disable_oob=self._disable_oob.get(),
            disable_oob_auto=self._disable_oob_auto.get(),
            disable_interrupt=self._disable_interrupt.get(),
            bequeath_detach=self._bequeath_detach.get(),
            wallet_location=self._wallet_location.get(),
            wallet_override=self._wallet_override.get(),
            encryption_wallet_location=self._enc_wallet_location.get(),
            sec_user_audit_action_banner=self._audit_banner.get(),
            sec_user_unauthorized_access_banner=self._unauth_banner.get(),
            sqlnet_uri=self._uri.get(),
            use_https_proxy=self._use_https_proxy.get(),
            sqlnet_client_registration=self._client_reg.get(),
            use_cman=self._use_cman.get(),
            use_dedicated_server=self._use_dedicated.get(),
            dbfw_public_key=self._dbfw_key.get(),
            tnsping_trace_level=self._tnsping_trace_level.get(),
            tnsping_trace_directory=self._tnsping_trace_dir.get(),
        )

    def _populate_from_model(self, config: SQLNetConfig):
        self._names_default_domain.set(config.names_default_domain)
        self._names_directory_path.set(config.names_directory_path)
        self._names_ldap_attr.set(config.names_ldap_attr)
        self._names_ldap_auth_bind.set(config.names_ldap_authenticate_bind)
        self._names_ldap_persistent.set(config.names_ldap_persistent_session)

        self._enc_client.set(config.sqlnet_encryption_client)
        self._enc_types_client.set(config.sqlnet_encryption_types_client)
        self._enc_server.set(config.sqlnet_encryption_server)
        self._enc_types_server.set(config.sqlnet_encryption_types_server)
        self._allow_weak.set(config.sqlnet_allow_weak_crypto)

        self._chk_client.set(config.sqlnet_crypto_checksum_client)
        self._chk_types_client.set(config.sqlnet_crypto_checksum_types_client)
        self._chk_server.set(config.sqlnet_crypto_checksum_server)
        self._chk_types_server.set(config.sqlnet_crypto_checksum_types_server)

        self._ssl_version.set(config.ssl_version)
        self._ssl_client_auth.set(config.ssl_client_authentication)
        self._ssl_cipher_suites.set(config.ssl_cipher_suites)
        self._ssl_dn_match.set(config.ssl_server_dn_match)
        self._ssl_cert_dn.set(config.ssl_server_cert_dn)
        self._ssl_crl_file.set(config.ssl_crl_file)
        self._ssl_crl_path.set(config.ssl_crl_path)
        self._ssl_ec_curves.set(config.ssl_ec_curves)
        self._ssl_md5.set(config.ssl_allow_md5_certs)
        self._ssl_sha1.set(config.ssl_allow_sha1_certs)
        self._ssl_ext_key.set(config.ssl_extended_key_usage)

        self._auth_services.set(config.sqlnet_authentication_services)
        self._logon_version_client.set(config.sqlnet_allowed_logon_version_client)
        self._logon_version_server.set(config.sqlnet_allowed_logon_version_server)
        self._fallback_auth.set(config.sqlnet_fallback_authentication)
        self._password_auth.set(config.sqlnet_password_auth)

        self._krb_cc.set(config.sqlnet_kerberos5_cc_name)
        self._krb_conf.set(config.sqlnet_kerberos5_conf)
        self._krb_clockskew.set(config.sqlnet_kerberos5_clockskew)
        self._krb_keytab.set(config.sqlnet_kerberos5_keytab)
        self._krb_realms.set(config.sqlnet_kerberos5_realms)
        self._krb_delegation.set(config.sqlnet_kerberos5_delegation_mode)
        self._krb_service.set(config.sqlnet_kerberos5_service)

        self._radius_primary.set(config.sqlnet_radius_primary)
        self._radius_primary_port.set(config.sqlnet_radius_primary_port)
        self._radius_alternate.set(config.sqlnet_radius_alternate)
        self._radius_alternate_port.set(config.sqlnet_radius_alternate_port)
        self._radius_challenge.set(config.sqlnet_radius_challenge)
        self._radius_secret.set(config.sqlnet_radius_secret)
        self._radius_accounting.set(config.sqlnet_radius_send_accounting)

        self._oci_iam.set(config.oci_iam_url)
        self._oci_tenancy.set(config.oci_tenancy)
        self._oci_compartment.set(config.oci_compartment)
        self._oci_database.set(config.oci_database)
        self._token_auth.set(config.token_auth)
        self._token_location.set(config.token_location)
        self._cloud_user.set(config.cloud_user)

        self._expire_time.set(config.sqlnet_expire_time)
        self._outbound_timeout.set(config.sqlnet_outbound_connect_timeout)
        self._inbound_timeout.set(config.sqlnet_inbound_connect_timeout)
        self._recv_timeout.set(config.sqlnet_recv_timeout)
        self._send_timeout.set(config.sqlnet_send_timeout)
        self._down_hosts_timeout.set(config.sqlnet_down_hosts_timeout)
        self._tcp_connect_timeout.set(config.tcp_connect_timeout)

        self._default_sdu.set(config.default_sdu_size)
        self._recv_buf.set(config.recv_buf_size)
        self._send_buf.set(config.send_buf_size)
        self._max_conduits.set(config.max_conduits)

        self._compression.set(config.sqlnet_compression)
        self._comp_levels.set(config.sqlnet_compression_levels)
        self._comp_threshold.set(config.sqlnet_compression_threshold)
        self._comp_accel.set(config.sqlnet_compression_acceleration)

        self._tcp_validnode.set(config.tcp_validnode_checking)
        self._tcp_invited.set(config.tcp_invited_nodes)
        self._tcp_excluded.set(config.tcp_excluded_nodes)
        self._tcp_nodelay.set(config.tcp_nodelay)
        self._tcp_queuesize.set(config.tcp_queuesize)

        self._ipc_keypath.set(config.ipc_keypath)
        self._sdp_pf.set(config.sdp_pf_inet_sdp)
        self._exa_flow.set(config.exadirect_flow_control)
        self._exa_recvpoll.set(config.exadirect_recvpoll)
        self._disable_oob.set(config.disable_oob)
        self._disable_oob_auto.set(config.disable_oob_auto)
        self._disable_interrupt.set(config.disable_interrupt)
        self._bequeath_detach.set(config.bequeath_detach)

        self._wallet_location.set(config.wallet_location)
        self._wallet_override.set(config.wallet_override)
        self._enc_wallet_location.set(config.encryption_wallet_location)

        self._audit_banner.set(config.sec_user_audit_action_banner)
        self._unauth_banner.set(config.sec_user_unauthorized_access_banner)

        self._uri.set(config.sqlnet_uri)
        self._use_https_proxy.set(config.use_https_proxy)
        self._client_reg.set(config.sqlnet_client_registration)
        self._use_cman.set(config.use_cman)
        self._use_dedicated.set(config.use_dedicated_server)
        self._dbfw_key.set(config.dbfw_public_key)

        self._tnsping_trace_level.set(config.tnsping_trace_level)
        self._tnsping_trace_dir.set(config.tnsping_trace_directory)

        self._update_preview()

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

    def _do_import(self):
        path = open_ora_file("Import sqlnet.ora")
        if path:
            try:
                text = read_file(path)
                ast = parse_ora(text)
                config = SQLNetConfig.from_ast(ast)
                self._populate_from_model(config)
            except Exception as e:
                ctk.CTkInputDialog(text=f"Error importing: {e}", title="Import Error")

    def _do_export(self):
        path = save_ora_file("Export sqlnet.ora", "sqlnet.ora")
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
        self._populate_from_model(SQLNetConfig())
