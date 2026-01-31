"""SQLNet configuration data model (sqlnet.ora)."""

from __future__ import annotations
from dataclasses import dataclass
from orafiles.models.base import BaseModel, ValidationError
from orafiles.parser.ast_nodes import ConfigFile, NVList


def _get_csv(config: ConfigFile, key: str) -> str:
    """Get a parameter that may be a list as comma-separated string."""
    pair = config.find(key)
    if not pair:
        return ""
    if pair.get_value():
        return pair.get_value()
    lst = pair.get_list()
    if lst:
        from orafiles.parser.ast_nodes import NVValue
        vals = [item.value for item in lst.items if isinstance(item, NVValue)]
        return ", ".join(vals)
    return ""


@dataclass
class SQLNetConfig(BaseModel):
    """Complete sqlnet.ora configuration."""

    # Naming
    names_default_domain: str = ""
    names_directory_path: str = ""  # comma-separated: TNSNAMES, LDAP, EZCONNECT
    names_ldap_attr: str = ""
    names_ldap_authenticate_bind: str = ""
    names_ldap_persistent_session: str = ""

    # Encryption - Client
    sqlnet_encryption_client: str = ""  # ACCEPTED, REJECTED, REQUESTED, REQUIRED
    sqlnet_encryption_types_client: str = ""
    # Encryption - Server
    sqlnet_encryption_server: str = ""
    sqlnet_encryption_types_server: str = ""
    sqlnet_allow_weak_crypto: str = ""  # TRUE/FALSE

    # Integrity - Client
    sqlnet_crypto_checksum_client: str = ""
    sqlnet_crypto_checksum_types_client: str = ""
    # Integrity - Server
    sqlnet_crypto_checksum_server: str = ""
    sqlnet_crypto_checksum_types_server: str = ""

    # SSL/TLS
    ssl_version: str = ""
    ssl_client_authentication: str = ""  # TRUE/FALSE
    ssl_cipher_suites: str = ""
    ssl_server_dn_match: str = ""  # ON/OFF
    ssl_server_cert_dn: str = ""
    ssl_crl_file: str = ""
    ssl_crl_path: str = ""
    ssl_ec_curves: str = ""
    ssl_allow_md5_certs: str = ""  # TRUE/FALSE
    ssl_allow_sha1_certs: str = ""  # TRUE/FALSE
    ssl_extended_key_usage: str = ""

    # Authentication
    sqlnet_authentication_services: str = ""
    sqlnet_allowed_logon_version_client: str = ""
    sqlnet_allowed_logon_version_server: str = ""
    sqlnet_fallback_authentication: str = ""  # TRUE/FALSE
    sqlnet_password_auth: str = ""

    # Kerberos
    sqlnet_kerberos5_cc_name: str = ""
    sqlnet_kerberos5_conf: str = ""
    sqlnet_kerberos5_clockskew: str = ""
    sqlnet_kerberos5_keytab: str = ""
    sqlnet_kerberos5_realms: str = ""
    sqlnet_kerberos5_delegation_mode: str = ""
    sqlnet_kerberos5_service: str = ""

    # RADIUS
    sqlnet_radius_primary: str = ""
    sqlnet_radius_primary_port: str = ""
    sqlnet_radius_alternate: str = ""
    sqlnet_radius_alternate_port: str = ""
    sqlnet_radius_challenge: str = ""  # TRUE/FALSE
    sqlnet_radius_secret: str = ""
    sqlnet_radius_send_accounting: str = ""  # ON/OFF

    # OCI/Cloud
    oci_iam_url: str = ""
    oci_tenancy: str = ""
    oci_compartment: str = ""
    oci_database: str = ""
    token_auth: str = ""
    token_location: str = ""
    cloud_user: str = ""

    # Timeouts
    sqlnet_expire_time: str = ""
    sqlnet_outbound_connect_timeout: str = ""
    sqlnet_inbound_connect_timeout: str = ""
    sqlnet_recv_timeout: str = ""
    sqlnet_send_timeout: str = ""
    sqlnet_down_hosts_timeout: str = ""
    tcp_connect_timeout: str = ""

    # Performance
    default_sdu_size: str = ""
    recv_buf_size: str = ""
    send_buf_size: str = ""
    max_conduits: str = ""

    # Compression
    sqlnet_compression: str = ""  # ON/OFF
    sqlnet_compression_levels: str = ""
    sqlnet_compression_threshold: str = ""
    sqlnet_compression_acceleration: str = ""

    # TCP Access Control
    tcp_validnode_checking: str = ""  # YES/NO
    tcp_invited_nodes: str = ""
    tcp_excluded_nodes: str = ""
    tcp_nodelay: str = ""  # YES/NO
    tcp_queuesize: str = ""

    # IPC / SDP / Exadirect
    ipc_keypath: str = ""
    sdp_pf_inet_sdp: str = ""
    exadirect_flow_control: str = ""
    exadirect_recvpoll: str = ""

    # OOB / Interrupts
    disable_oob: str = ""  # ON/OFF
    disable_oob_auto: str = ""  # TRUE/FALSE
    disable_interrupt: str = ""  # TRUE/FALSE
    bequeath_detach: str = ""  # YES/NO

    # Wallet
    wallet_location: str = ""
    wallet_override: str = ""  # TRUE/FALSE
    encryption_wallet_location: str = ""

    # Security Banners
    sec_user_audit_action_banner: str = ""
    sec_user_unauthorized_access_banner: str = ""

    # Misc
    sqlnet_uri: str = ""
    use_https_proxy: str = ""  # ON/OFF
    sqlnet_client_registration: str = ""
    use_cman: str = ""  # TRUE/FALSE
    use_dedicated_server: str = ""  # ON/OFF
    dbfw_public_key: str = ""

    # Logging
    tnsping_trace_level: str = ""
    tnsping_trace_directory: str = ""

    def validate(self) -> list[ValidationError]:
        errors = []
        errors.extend(self._validate_positive_int(self.default_sdu_size, "default_sdu_size"))
        errors.extend(self._validate_positive_int(self.sqlnet_expire_time, "expire_time"))
        errors.extend(self._validate_positive_int(self.sqlnet_outbound_connect_timeout, "outbound_connect_timeout"))
        errors.extend(self._validate_positive_int(self.sqlnet_recv_timeout, "recv_timeout"))
        errors.extend(self._validate_positive_int(self.sqlnet_send_timeout, "send_timeout"))
        return errors

    @classmethod
    def from_ast(cls, config: ConfigFile) -> SQLNetConfig:
        g = config.get_value
        gc = lambda key: _get_csv(config, key)

        return cls(
            # Naming
            names_default_domain=g("NAMES.DEFAULT_DOMAIN") or "",
            names_directory_path=gc("NAMES.DIRECTORY_PATH"),
            names_ldap_attr=g("NAMES.LDAP_ATTR") or "",
            names_ldap_authenticate_bind=g("NAMES.LDAP_AUTHENTICATE_BIND") or "",
            names_ldap_persistent_session=g("NAMES.LDAP_PERSISTENT_SESSION") or "",

            # Encryption - Client
            sqlnet_encryption_client=g("SQLNET.ENCRYPTION_CLIENT") or "",
            sqlnet_encryption_types_client=gc("SQLNET.ENCRYPTION_TYPES_CLIENT"),
            sqlnet_encryption_server=g("SQLNET.ENCRYPTION_SERVER") or "",
            sqlnet_encryption_types_server=gc("SQLNET.ENCRYPTION_TYPES_SERVER"),
            sqlnet_allow_weak_crypto=g("SQLNET.ALLOW_WEAK_CRYPTO") or "",

            # Integrity
            sqlnet_crypto_checksum_client=g("SQLNET.CRYPTO_CHECKSUM_CLIENT") or "",
            sqlnet_crypto_checksum_types_client=gc("SQLNET.CRYPTO_CHECKSUM_TYPES_CLIENT"),
            sqlnet_crypto_checksum_server=g("SQLNET.CRYPTO_CHECKSUM_SERVER") or "",
            sqlnet_crypto_checksum_types_server=gc("SQLNET.CRYPTO_CHECKSUM_TYPES_SERVER"),

            # SSL/TLS
            ssl_version=g("SSL_VERSION") or "",
            ssl_client_authentication=g("SSL_CLIENT_AUTHENTICATION") or "",
            ssl_cipher_suites=gc("SSL_CIPHER_SUITES"),
            ssl_server_dn_match=g("SSL_SERVER_DN_MATCH") or "",
            ssl_server_cert_dn=g("SSL_SERVER_CERT_DN") or "",
            ssl_crl_file=g("SSL_CRL_FILE") or "",
            ssl_crl_path=g("SSL_CRL_PATH") or "",
            ssl_ec_curves=g("SSL_EC_CURVES") or "",
            ssl_allow_md5_certs=g("SSL_ALLOW_MD5_CERTS") or "",
            ssl_allow_sha1_certs=g("SSL_ALLOW_SHA1_CERTS") or "",
            ssl_extended_key_usage=g("SSL_EXTENDED_KEY_USAGE") or "",

            # Authentication
            sqlnet_authentication_services=gc("SQLNET.AUTHENTICATION_SERVICES"),
            sqlnet_allowed_logon_version_client=g("SQLNET.ALLOWED_LOGON_VERSION_CLIENT") or "",
            sqlnet_allowed_logon_version_server=g("SQLNET.ALLOWED_LOGON_VERSION_SERVER") or "",
            sqlnet_fallback_authentication=g("SQLNET.FALLBACK_AUTHENTICATION") or "",
            sqlnet_password_auth=g("SQLNET.PASSWORD_AUTH") or "",

            # Kerberos
            sqlnet_kerberos5_cc_name=g("SQLNET.KERBEROS5_CC_NAME") or "",
            sqlnet_kerberos5_conf=g("SQLNET.KERBEROS5_CONF") or "",
            sqlnet_kerberos5_clockskew=g("SQLNET.KERBEROS5_CLOCKSKEW") or "",
            sqlnet_kerberos5_keytab=g("SQLNET.KERBEROS5_KEYTAB") or "",
            sqlnet_kerberos5_realms=g("SQLNET.KERBEROS5_REALMS") or "",
            sqlnet_kerberos5_delegation_mode=g("SQLNET.KERBEROS5_DELEGATION_MODE") or "",
            sqlnet_kerberos5_service=g("SQLNET.KERBEROS5_SERVICE") or "",

            # RADIUS
            sqlnet_radius_primary=g("SQLNET.RADIUS_AUTHENTICATION") or "",
            sqlnet_radius_primary_port=g("SQLNET.RADIUS_AUTHENTICATION_PORT") or "",
            sqlnet_radius_alternate=g("SQLNET.RADIUS_AUTHENTICATION_ALTERNATE") or "",
            sqlnet_radius_alternate_port=g("SQLNET.RADIUS_AUTHENTICATION_ALTERNATE_PORT") or "",
            sqlnet_radius_challenge=g("SQLNET.RADIUS_CHALLENGE_RESPONSE") or "",
            sqlnet_radius_secret=g("SQLNET.RADIUS_SECRET") or "",
            sqlnet_radius_send_accounting=g("SQLNET.RADIUS_SEND_ACCOUNTING") or "",

            # OCI/Cloud
            oci_iam_url=g("OCI_IAM_URL") or "",
            oci_tenancy=g("OCI_TENANCY") or "",
            oci_compartment=g("OCI_COMPARTMENT") or "",
            oci_database=g("OCI_DATABASE") or "",
            token_auth=g("TOKEN_AUTH") or "",
            token_location=g("TOKEN_LOCATION") or "",
            cloud_user=g("CLOUD_USER") or "",

            # Timeouts
            sqlnet_expire_time=g("SQLNET.EXPIRE_TIME") or "",
            sqlnet_outbound_connect_timeout=g("SQLNET.OUTBOUND_CONNECT_TIMEOUT") or "",
            sqlnet_inbound_connect_timeout=g("SQLNET.INBOUND_CONNECT_TIMEOUT") or "",
            sqlnet_recv_timeout=g("SQLNET.RECV_TIMEOUT") or "",
            sqlnet_send_timeout=g("SQLNET.SEND_TIMEOUT") or "",
            sqlnet_down_hosts_timeout=g("SQLNET.DOWN_HOSTS_TIMEOUT") or "",
            tcp_connect_timeout=g("TCP.CONNECT_TIMEOUT") or "",

            # Performance
            default_sdu_size=g("DEFAULT_SDU_SIZE") or "",
            recv_buf_size=g("RECV_BUF_SIZE") or "",
            send_buf_size=g("SEND_BUF_SIZE") or "",
            max_conduits=g("MAX_CONDUITS") or "",

            # Compression
            sqlnet_compression=g("SQLNET.COMPRESSION") or "",
            sqlnet_compression_levels=gc("SQLNET.COMPRESSION_LEVELS"),
            sqlnet_compression_threshold=g("SQLNET.COMPRESSION_THRESHOLD") or "",
            sqlnet_compression_acceleration=g("SQLNET.COMPRESSION_ACCELERATION") or "",

            # TCP Access
            tcp_validnode_checking=g("TCP.VALIDNODE_CHECKING") or "",
            tcp_invited_nodes=gc("TCP.INVITED_NODES"),
            tcp_excluded_nodes=gc("TCP.EXCLUDED_NODES"),
            tcp_nodelay=g("TCP.NODELAY") or "",
            tcp_queuesize=g("TCP.QUEUESIZE") or "",

            # IPC/SDP/Exadirect
            ipc_keypath=g("IPC.KEYPATH") or "",
            sdp_pf_inet_sdp=g("SDP.PF_INET_SDP") or "",
            exadirect_flow_control=g("EXADIRECT_FLOW_CONTROL") or "",
            exadirect_recvpoll=g("EXADIRECT_RECVPOLL") or "",

            # OOB/Interrupts
            disable_oob=g("DISABLE_OOB") or "",
            disable_oob_auto=g("DISABLE_OOB_AUTO") or "",
            disable_interrupt=g("DISABLE_INTERRUPT") or "",
            bequeath_detach=g("BEQUEATH_DETACH") or "",

            # Wallet
            wallet_location=g("WALLET_LOCATION") or "",
            wallet_override=g("WALLET_OVERRIDE") or "",
            encryption_wallet_location=g("ENCRYPTION_WALLET_LOCATION") or "",

            # Banners
            sec_user_audit_action_banner=g("SEC_USER_AUDIT_ACTION_BANNER") or "",
            sec_user_unauthorized_access_banner=g("SEC_USER_UNAUTHORIZED_ACCESS_BANNER") or "",

            # Misc
            sqlnet_uri=g("SQLNET.URI") or "",
            use_https_proxy=g("USE_HTTPS_PROXY") or "",
            sqlnet_client_registration=g("SQLNET.CLIENT_REGISTRATION") or "",
            use_cman=g("USE_CMAN") or "",
            use_dedicated_server=g("USE_DEDICATED_SERVER") or "",
            dbfw_public_key=g("DBFW_PUBLIC_KEY") or "",

            # Logging
            tnsping_trace_level=g("TNSPING.TRACE_LEVEL") or "",
            tnsping_trace_directory=g("TNSPING.TRACE_DIRECTORY") or "",
        )
