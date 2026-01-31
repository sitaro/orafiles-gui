"""Generator for listener.ora from ListenerConfig model."""

from __future__ import annotations
from orafiles.generators.base import BaseGenerator
from orafiles.models.listener import ListenerConfig, SIDEntry
from orafiles.models.protocol_address import (
    TCPAddress, TCPSAddress, IPCAddress, NMPAddress, Address, get_protocol_name
)


class ListenerGenerator(BaseGenerator):

    def generate(self, config: ListenerConfig) -> str:
        sections = []

        # Listener address definition
        addr_section = self._gen_addresses(config)
        if addr_section:
            sections.append(addr_section)

        # SID_LIST
        sid_section = self._gen_sid_list(config)
        if sid_section:
            sections.append(sid_section)

        # Control parameters
        ctrl = self._gen_control(config)
        if ctrl:
            sections.append(ctrl)

        # Rate Limiting
        rate = self._gen_rate_limiting(config)
        if rate:
            sections.append(rate)

        # Security
        sec = self._gen_security(config)
        if sec:
            sections.append(sec)

        # SSL/TLS
        ssl = self._gen_ssl(config)
        if ssl:
            sections.append(ssl)

        # Diagnostics
        diag = self._gen_diagnostics(config)
        if diag:
            sections.append(diag)

        return "\n\n".join(sections) + "\n" if sections else ""

    def _gen_address(self, addr: Address, depth: int) -> str:
        lines = [self._section_open("ADDRESS", depth)]
        d = depth + 1
        if isinstance(addr, TCPAddress):
            lines.append(self._param("PROTOCOL", "TCP", d))
            lines.append(self._param("HOST", addr.host, d))
            lines.append(self._param("PORT", addr.port, d))
            if addr.ip:
                lines.append(self._param("IP", addr.ip, d))
            if addr.queuesize:
                lines.append(self._param("QUEUESIZE", addr.queuesize, d))
            if addr.buf_size:
                lines.append(self._param("BUF_SIZE", addr.buf_size, d))
            if addr.rate_limit:
                lines.append(self._param("RATE_LIMIT", addr.rate_limit, d))
        elif isinstance(addr, TCPSAddress):
            lines.append(self._param("PROTOCOL", "TCPS", d))
            lines.append(self._param("HOST", addr.host, d))
            lines.append(self._param("PORT", addr.port, d))
            if addr.ip:
                lines.append(self._param("IP", addr.ip, d))
            if addr.queuesize:
                lines.append(self._param("QUEUESIZE", addr.queuesize, d))
            if addr.buf_size:
                lines.append(self._param("BUF_SIZE", addr.buf_size, d))
            if addr.rate_limit:
                lines.append(self._param("RATE_LIMIT", addr.rate_limit, d))
        elif isinstance(addr, IPCAddress):
            lines.append(self._param("PROTOCOL", "IPC", d))
            lines.append(self._param("KEY", addr.key, d))
        elif isinstance(addr, NMPAddress):
            lines.append(self._param("PROTOCOL", "NMP", d))
            if addr.server:
                lines.append(self._param("SERVER", addr.server, d))
            lines.append(self._param("PIPE", addr.pipe, d))
        lines.append(self._section_close(depth))
        return "\n".join(lines)

    def _gen_addresses(self, config: ListenerConfig) -> str:
        if not config.addresses:
            return ""
        lines = [self._section_open(config.name, 0)]
        for addr in config.addresses:
            lines.append(self._gen_address(addr, 1))
        lines.append(self._section_close(0))
        return "\n".join(lines)

    def _gen_sid_list(self, config: ListenerConfig) -> str:
        if not config.sid_list:
            return ""
        lines = [self._section_open(f"SID_LIST_{config.name}", 0)]
        for sid in config.sid_list:
            lines.append(self._gen_sid_desc(sid, 1))
        lines.append(self._section_close(0))
        return "\n".join(lines)

    def _gen_sid_desc(self, sid: SIDEntry, depth: int) -> str:
        lines = [self._section_open("SID_DESC", depth)]
        d = depth + 1
        if sid.sid_name:
            lines.append(self._param("SID_NAME", sid.sid_name, d))
        if sid.global_dbname:
            lines.append(self._param("GLOBAL_DBNAME", sid.global_dbname, d))
        if sid.oracle_home:
            lines.append(self._param("ORACLE_HOME", sid.oracle_home, d))
        if sid.program:
            lines.append(self._param("PROGRAM", sid.program, d))
        if sid.envs:
            lines.append(self._param("ENVS", f'"{sid.envs}"', d))
        if sid.sdu:
            lines.append(self._param("SDU", sid.sdu, d))
        lines.append(self._section_close(depth))
        return "\n".join(lines)

    def _gen_control(self, config: ListenerConfig) -> str:
        name = config.name
        lines = [
            self._param_line(f"ADMIN_RESTRICTIONS_{name}", config.admin_restrictions),
            self._param_line(f"DEFAULT_SERVICE_{name}", config.default_service),
            self._param_line(f"DYNAMIC_REGISTRATION_{name}", config.dynamic_registration),
            self._param_line(f"INBOUND_CONNECT_TIMEOUT_{name}", config.inbound_connect_timeout),
            self._param_line(f"MAX_ALL_CONNECTIONS_{name}", config.max_all_connections),
            self._param_line(f"MAX_REG_CONNECTIONS_{name}", config.max_reg_connections),
            self._param_line(f"SAVE_CONFIG_ON_STOP_{name}", config.save_config_on_stop),
            self._param_line(f"USE_SID_AS_SERVICE_{name}", config.use_sid_as_service),
            self._param_line(f"DEDICATED_THROUGH_BROKER_{name}", config.dedicated_through_broker),
            self._param_line(f"ALLOW_MULTIPLE_REDIRECTS_{name}", config.allow_multiple_redirects),
            self._param_line(f"CRS_NOTIFICATION_{name}", config.crs_notification),
            self._param_line(f"ENABLE_EXADIRECT_{name}", config.enable_exadirect),
            self._param_line(f"SUBSCRIBE_FOR_NODE_DOWN_EVENT_{name}", config.subscribe_for_node_down_event),
        ]
        return self._build(lines)

    def _gen_rate_limiting(self, config: ListenerConfig) -> str:
        name = config.name
        lines = [
            self._param_line(f"CONNECTION_RATE_{name}", config.connection_rate),
            self._param_line(f"SERVICE_RATE_{name}", config.service_rate),
        ]
        return self._build(lines)

    def _gen_security(self, config: ListenerConfig) -> str:
        name = config.name
        lines = [
            self._param_line(f"VALID_NODE_CHECKING_REGISTRATION_{name}", config.valid_node_checking_registration),
            self._param_line(f"REGISTRATION_INVITED_NODES_{name}", config.registration_invited_nodes),
            self._param_line(f"REGISTRATION_EXCLUDED_NODES_{name}", config.registration_excluded_nodes),
            self._param_line(f"LOCAL_REGISTRATION_ADDRESS_{name}", config.local_registration_address),
            self._param_line(f"REMOTE_REGISTRATION_ADDRESS_{name}", config.remote_registration_address),
            self._param_line(f"SECURE_REGISTER_{name}", config.secure_register),
            self._param_line(f"SECURE_PROTOCOL_{name}", config.secure_protocol),
            self._param_line(f"SECURE_CONTROL_{name}", config.secure_control),
        ]
        return self._build(lines)

    def _gen_ssl(self, config: ListenerConfig) -> str:
        name = config.name
        lines = [
            self._param_line(f"SSL_VERSION_{name}", config.ssl_version),
            self._param_line(f"SSL_CLIENT_AUTHENTICATION_{name}", config.ssl_client_authentication),
            self._param_line(f"SSL_CIPHER_SUITES_{name}", config.ssl_cipher_suites),
            self._param_line(f"WALLET_LOCATION_{name}", config.wallet_location),
        ]
        return self._build(lines)

    def _gen_diagnostics(self, config: ListenerConfig) -> str:
        name = config.name
        lines = [
            self._param_line(f"DIAG_ADR_ENABLED_{name}", config.diag_adr_enabled),
            self._param_line(f"ADR_BASE_{name}", config.adr_base),
            self._param_line(f"LOGGING_{name}", config.logging),
            self._param_line(f"LOG_FILE_NUM_{name}", config.log_file_num),
            self._param_line(f"LOG_FILE_SIZE_{name}", config.log_file_size),
            self._param_line(f"TRACE_LEVEL_{name}", config.trace_level),
            self._param_line(f"TRACE_TIMESTAMP_{name}", config.trace_timestamp),
            self._param_line(f"TRACE_DIRECTORY_{name}", config.trace_directory),
            self._param_line(f"TRACE_FILE_{name}", config.trace_file),
            self._param_line(f"TRACE_FILEAGE_{name}", config.trace_fileage),
            self._param_line(f"TRACE_FILELEN_{name}", config.trace_filelen),
            self._param_line(f"TRACE_FILENO_{name}", config.trace_fileno),
            self._param_line(f"LOG_DIRECTORY_{name}", config.log_directory),
            self._param_line(f"LOG_FILE_{name}", config.log_file),
        ]
        return self._build(lines)
