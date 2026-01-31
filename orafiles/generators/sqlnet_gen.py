"""Generator for sqlnet.ora from SQLNetConfig model."""

from __future__ import annotations
from orafiles.generators.base import BaseGenerator
from orafiles.models.sqlnet import SQLNetConfig


class SQLNetGenerator(BaseGenerator):

    def generate(self, config: SQLNetConfig) -> str:
        sections = []

        s = self._gen_naming(config)
        if s:
            sections.append(s)
        s = self._gen_encryption(config)
        if s:
            sections.append(s)
        s = self._gen_integrity(config)
        if s:
            sections.append(s)
        s = self._gen_ssl(config)
        if s:
            sections.append(s)
        s = self._gen_auth(config)
        if s:
            sections.append(s)
        s = self._gen_kerberos(config)
        if s:
            sections.append(s)
        s = self._gen_radius(config)
        if s:
            sections.append(s)
        s = self._gen_oci_cloud(config)
        if s:
            sections.append(s)
        s = self._gen_timeouts(config)
        if s:
            sections.append(s)
        s = self._gen_performance(config)
        if s:
            sections.append(s)
        s = self._gen_compression(config)
        if s:
            sections.append(s)
        s = self._gen_tcp_access(config)
        if s:
            sections.append(s)
        s = self._gen_advanced(config)
        if s:
            sections.append(s)
        s = self._gen_wallet(config)
        if s:
            sections.append(s)
        s = self._gen_banners(config)
        if s:
            sections.append(s)
        s = self._gen_misc(config)
        if s:
            sections.append(s)
        s = self._gen_logging(config)
        if s:
            sections.append(s)

        return "\n\n".join(sections) + "\n" if sections else ""

    def _gen_naming(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("NAMES.DEFAULT_DOMAIN", c.names_default_domain),
            self._list_param("NAMES.DIRECTORY_PATH", c.names_directory_path),
            self._param_line("NAMES.LDAP_ATTR", c.names_ldap_attr),
            self._param_line("NAMES.LDAP_AUTHENTICATE_BIND", c.names_ldap_authenticate_bind),
            self._param_line("NAMES.LDAP_PERSISTENT_SESSION", c.names_ldap_persistent_session),
        ])

    def _gen_encryption(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SQLNET.ENCRYPTION_CLIENT", c.sqlnet_encryption_client),
            self._list_param("SQLNET.ENCRYPTION_TYPES_CLIENT", c.sqlnet_encryption_types_client),
            self._param_line("SQLNET.ENCRYPTION_SERVER", c.sqlnet_encryption_server),
            self._list_param("SQLNET.ENCRYPTION_TYPES_SERVER", c.sqlnet_encryption_types_server),
            self._param_line("SQLNET.ALLOW_WEAK_CRYPTO", c.sqlnet_allow_weak_crypto),
        ])

    def _gen_integrity(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SQLNET.CRYPTO_CHECKSUM_CLIENT", c.sqlnet_crypto_checksum_client),
            self._list_param("SQLNET.CRYPTO_CHECKSUM_TYPES_CLIENT", c.sqlnet_crypto_checksum_types_client),
            self._param_line("SQLNET.CRYPTO_CHECKSUM_SERVER", c.sqlnet_crypto_checksum_server),
            self._list_param("SQLNET.CRYPTO_CHECKSUM_TYPES_SERVER", c.sqlnet_crypto_checksum_types_server),
        ])

    def _gen_ssl(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SSL_VERSION", c.ssl_version),
            self._param_line("SSL_CLIENT_AUTHENTICATION", c.ssl_client_authentication),
            self._list_param("SSL_CIPHER_SUITES", c.ssl_cipher_suites),
            self._param_line("SSL_SERVER_DN_MATCH", c.ssl_server_dn_match),
            self._param_line("SSL_SERVER_CERT_DN", c.ssl_server_cert_dn),
            self._param_line("SSL_CRL_FILE", c.ssl_crl_file),
            self._param_line("SSL_CRL_PATH", c.ssl_crl_path),
            self._param_line("SSL_EC_CURVES", c.ssl_ec_curves),
            self._param_line("SSL_ALLOW_MD5_CERTS", c.ssl_allow_md5_certs),
            self._param_line("SSL_ALLOW_SHA1_CERTS", c.ssl_allow_sha1_certs),
            self._param_line("SSL_EXTENDED_KEY_USAGE", c.ssl_extended_key_usage),
        ])

    def _gen_auth(self, c: SQLNetConfig) -> str:
        return self._build([
            self._list_param("SQLNET.AUTHENTICATION_SERVICES", c.sqlnet_authentication_services),
            self._param_line("SQLNET.ALLOWED_LOGON_VERSION_CLIENT", c.sqlnet_allowed_logon_version_client),
            self._param_line("SQLNET.ALLOWED_LOGON_VERSION_SERVER", c.sqlnet_allowed_logon_version_server),
            self._param_line("SQLNET.FALLBACK_AUTHENTICATION", c.sqlnet_fallback_authentication),
            self._param_line("SQLNET.PASSWORD_AUTH", c.sqlnet_password_auth),
        ])

    def _gen_kerberos(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SQLNET.KERBEROS5_CC_NAME", c.sqlnet_kerberos5_cc_name),
            self._param_line("SQLNET.KERBEROS5_CONF", c.sqlnet_kerberos5_conf),
            self._param_line("SQLNET.KERBEROS5_CLOCKSKEW", c.sqlnet_kerberos5_clockskew),
            self._param_line("SQLNET.KERBEROS5_KEYTAB", c.sqlnet_kerberos5_keytab),
            self._param_line("SQLNET.KERBEROS5_REALMS", c.sqlnet_kerberos5_realms),
            self._param_line("SQLNET.KERBEROS5_DELEGATION_MODE", c.sqlnet_kerberos5_delegation_mode),
            self._param_line("SQLNET.KERBEROS5_SERVICE", c.sqlnet_kerberos5_service),
        ])

    def _gen_radius(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SQLNET.RADIUS_AUTHENTICATION", c.sqlnet_radius_primary),
            self._param_line("SQLNET.RADIUS_AUTHENTICATION_PORT", c.sqlnet_radius_primary_port),
            self._param_line("SQLNET.RADIUS_AUTHENTICATION_ALTERNATE", c.sqlnet_radius_alternate),
            self._param_line("SQLNET.RADIUS_AUTHENTICATION_ALTERNATE_PORT", c.sqlnet_radius_alternate_port),
            self._param_line("SQLNET.RADIUS_CHALLENGE_RESPONSE", c.sqlnet_radius_challenge),
            self._param_line("SQLNET.RADIUS_SECRET", c.sqlnet_radius_secret),
            self._param_line("SQLNET.RADIUS_SEND_ACCOUNTING", c.sqlnet_radius_send_accounting),
        ])

    def _gen_oci_cloud(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("OCI_IAM_URL", c.oci_iam_url),
            self._param_line("OCI_TENANCY", c.oci_tenancy),
            self._param_line("OCI_COMPARTMENT", c.oci_compartment),
            self._param_line("OCI_DATABASE", c.oci_database),
            self._param_line("TOKEN_AUTH", c.token_auth),
            self._param_line("TOKEN_LOCATION", c.token_location),
            self._param_line("CLOUD_USER", c.cloud_user),
        ])

    def _gen_timeouts(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SQLNET.EXPIRE_TIME", c.sqlnet_expire_time),
            self._param_line("SQLNET.OUTBOUND_CONNECT_TIMEOUT", c.sqlnet_outbound_connect_timeout),
            self._param_line("SQLNET.INBOUND_CONNECT_TIMEOUT", c.sqlnet_inbound_connect_timeout),
            self._param_line("SQLNET.RECV_TIMEOUT", c.sqlnet_recv_timeout),
            self._param_line("SQLNET.SEND_TIMEOUT", c.sqlnet_send_timeout),
            self._param_line("SQLNET.DOWN_HOSTS_TIMEOUT", c.sqlnet_down_hosts_timeout),
            self._param_line("TCP.CONNECT_TIMEOUT", c.tcp_connect_timeout),
        ])

    def _gen_performance(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("DEFAULT_SDU_SIZE", c.default_sdu_size),
            self._param_line("RECV_BUF_SIZE", c.recv_buf_size),
            self._param_line("SEND_BUF_SIZE", c.send_buf_size),
            self._param_line("MAX_CONDUITS", c.max_conduits),
        ])

    def _gen_compression(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SQLNET.COMPRESSION", c.sqlnet_compression),
            self._list_param("SQLNET.COMPRESSION_LEVELS", c.sqlnet_compression_levels),
            self._param_line("SQLNET.COMPRESSION_THRESHOLD", c.sqlnet_compression_threshold),
            self._param_line("SQLNET.COMPRESSION_ACCELERATION", c.sqlnet_compression_acceleration),
        ])

    def _gen_tcp_access(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("TCP.VALIDNODE_CHECKING", c.tcp_validnode_checking),
            self._list_param("TCP.INVITED_NODES", c.tcp_invited_nodes),
            self._list_param("TCP.EXCLUDED_NODES", c.tcp_excluded_nodes),
            self._param_line("TCP.NODELAY", c.tcp_nodelay),
            self._param_line("TCP.QUEUESIZE", c.tcp_queuesize),
        ])

    def _gen_advanced(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("IPC.KEYPATH", c.ipc_keypath),
            self._param_line("SDP.PF_INET_SDP", c.sdp_pf_inet_sdp),
            self._param_line("EXADIRECT_FLOW_CONTROL", c.exadirect_flow_control),
            self._param_line("EXADIRECT_RECVPOLL", c.exadirect_recvpoll),
            self._param_line("DISABLE_OOB", c.disable_oob),
            self._param_line("DISABLE_OOB_AUTO", c.disable_oob_auto),
            self._param_line("DISABLE_INTERRUPT", c.disable_interrupt),
            self._param_line("BEQUEATH_DETACH", c.bequeath_detach),
        ])

    def _gen_wallet(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("WALLET_LOCATION", c.wallet_location),
            self._param_line("WALLET_OVERRIDE", c.wallet_override),
            self._param_line("ENCRYPTION_WALLET_LOCATION", c.encryption_wallet_location),
        ])

    def _gen_banners(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SEC_USER_AUDIT_ACTION_BANNER", c.sec_user_audit_action_banner),
            self._param_line("SEC_USER_UNAUTHORIZED_ACCESS_BANNER", c.sec_user_unauthorized_access_banner),
        ])

    def _gen_misc(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("SQLNET.URI", c.sqlnet_uri),
            self._param_line("USE_HTTPS_PROXY", c.use_https_proxy),
            self._param_line("SQLNET.CLIENT_REGISTRATION", c.sqlnet_client_registration),
            self._param_line("USE_CMAN", c.use_cman),
            self._param_line("USE_DEDICATED_SERVER", c.use_dedicated_server),
            self._param_line("DBFW_PUBLIC_KEY", c.dbfw_public_key),
        ])

    def _gen_logging(self, c: SQLNetConfig) -> str:
        return self._build([
            self._param_line("TNSPING.TRACE_LEVEL", c.tnsping_trace_level),
            self._param_line("TNSPING.TRACE_DIRECTORY", c.tnsping_trace_directory),
        ])
