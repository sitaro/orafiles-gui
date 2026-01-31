"""Generator for tnsnames.ora from TNSNamesConfig model."""

from __future__ import annotations
from orafiles.generators.base import BaseGenerator
from orafiles.models.tnsnames import TNSNamesConfig, ServiceEntry, ConnectData, FailoverMode, DescriptionSecurity
from orafiles.models.protocol_address import (
    TCPAddress, TCPSAddress, IPCAddress, NMPAddress, Address
)


class TNSNamesGenerator(BaseGenerator):

    def generate(self, config: TNSNamesConfig) -> str:
        sections = []
        if config.ifile:
            sections.append(f"IFILE = {config.ifile}")
        for svc in config.services:
            sections.append(self._gen_service(svc))
        return "\n\n".join(sections) + "\n" if sections else ""

    def _gen_service(self, svc: ServiceEntry) -> str:
        lines = [f"{svc.name} =", "("]
        # DESCRIPTION
        lines.append(self._ind(1) + "DESCRIPTION =")
        lines.append(self._ind(1) + "(")

        # Addresses
        if svc.addresses:
            if len(svc.addresses) > 1 or svc.address_list_failover or svc.address_list_load_balance:
                lines.append(self._section_open("ADDRESS_LIST", 2))
                if svc.address_list_failover:
                    lines.append(self._param("FAILOVER", svc.address_list_failover, 3))
                if svc.address_list_load_balance:
                    lines.append(self._param("LOAD_BALANCE", svc.address_list_load_balance, 3))
                if svc.address_list_source_route:
                    lines.append(self._param("SOURCE_ROUTE", svc.address_list_source_route, 3))
                for addr in svc.addresses:
                    lines.append(self._gen_address(addr, 3))
                lines.append(self._section_close(2))
            else:
                for addr in svc.addresses:
                    lines.append(self._gen_address(addr, 2))

        # Description options
        for key, val in [
            ("FAILOVER", svc.failover),
            ("LOAD_BALANCE", svc.load_balance),
            ("SOURCE_ROUTE", svc.source_route),
            ("SDU", svc.sdu),
            ("ENABLE", svc.enable),
            ("EXPIRE_TIME", svc.expire_time),
            ("RECV_BUF_SIZE", svc.recv_buf_size),
            ("SEND_BUF_SIZE", svc.send_buf_size),
            ("TYPE_OF_SERVICE", svc.type_of_service),
            ("HTTPS_PROXY", svc.https_proxy),
            ("HTTPS_PROXY_PORT", svc.https_proxy_port),
            ("CONNECT_TIMEOUT", svc.connect_timeout),
            ("RETRY_COUNT", svc.retry_count),
            ("RETRY_DELAY", svc.retry_delay),
            ("TRANSPORT_CONNECT_TIMEOUT", svc.transport_connect_timeout),
            ("RECV_TIMEOUT", svc.recv_timeout),
            ("COMPRESSION", svc.compression),
            ("COMPRESSION_LEVELS", svc.compression_levels),
        ]:
            if val:
                lines.append(self._param(key, val, 2))

        # Connect Data
        cd_section = self._gen_connect_data(svc.connect_data)
        if cd_section:
            lines.append(cd_section)

        # Security
        sec_section = self._gen_security(svc.security)
        if sec_section:
            lines.append(sec_section)

        lines.append(self._ind(1) + ")")  # close DESCRIPTION
        lines.append(")")  # close service
        return "\n".join(lines)

    def _gen_address(self, addr: Address, depth: int) -> str:
        lines = [self._section_open("ADDRESS", depth)]
        d = depth + 1
        if isinstance(addr, TCPAddress):
            lines.append(self._param("PROTOCOL", "TCP", d))
            lines.append(self._param("HOST", addr.host, d))
            lines.append(self._param("PORT", addr.port, d))
            if addr.ip:
                lines.append(self._param("IP", addr.ip, d))
        elif isinstance(addr, TCPSAddress):
            lines.append(self._param("PROTOCOL", "TCPS", d))
            lines.append(self._param("HOST", addr.host, d))
            lines.append(self._param("PORT", addr.port, d))
            if addr.ip:
                lines.append(self._param("IP", addr.ip, d))
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

    def _gen_connect_data(self, cd: ConnectData) -> str:
        items = []
        for key, val in [
            ("SERVICE_NAME", cd.service_name),
            ("SID", cd.sid),
            ("INSTANCE_NAME", cd.instance_name),
            ("SERVER", cd.server),
            ("HS", cd.hs),
            ("GLOBAL_NAME", cd.global_name),
            ("RDB_DATABASE", cd.rdb_database),
            ("COLOCATION_TAG", cd.colocation_tag),
            ("CONNECTION_ID_PREFIX", cd.connection_id_prefix),
            ("POOL_CONNECTION_CLASS", cd.pool_connection_class),
            ("POOL_PURITY", cd.pool_purity),
            ("SERVER_WAIT_TIMEOUT", cd.server_wait_timeout),
            ("SHARDING_KEY", cd.sharding_key),
            ("SUPER_SHARDING_KEY", cd.super_sharding_key),
            ("TUNNEL_SERVICE_NAME", cd.tunnel_service_name),
        ]:
            if val:
                items.append(self._param(key, val, 3))

        # Failover mode
        fo = self._gen_failover_mode(cd.failover_mode)
        if fo:
            items.append(fo)

        if not items:
            return ""

        lines = [self._section_open("CONNECT_DATA", 2)]
        lines.extend(items)
        lines.append(self._section_close(2))
        return "\n".join(lines)

    def _gen_failover_mode(self, fm: FailoverMode) -> str:
        items = []
        for key, val in [
            ("TYPE", fm.type),
            ("METHOD", fm.method),
            ("BACKUP", fm.backup),
            ("RETRIES", fm.retries),
            ("DELAY", fm.delay),
            ("TRANSACTION", fm.transaction),
        ]:
            if val:
                items.append(self._param(key, val, 4))

        if not items:
            return ""

        lines = [self._section_open("FAILOVER_MODE", 3)]
        lines.extend(items)
        lines.append(self._section_close(3))
        return "\n".join(lines)

    def _gen_security(self, sec: DescriptionSecurity) -> str:
        items = []
        for key, val in [
            ("AUTHENTICATION_SERVICE", sec.authentication_service),
            ("SSL_SERVER_CERT_DN", sec.ssl_server_cert_dn),
            ("SSL_SERVER_DN_MATCH", sec.ssl_server_dn_match),
            ("SSL_VERSION", sec.ssl_version),
            ("WALLET_LOCATION", sec.wallet_location),
            ("KERBEROS5_CC_NAME", sec.kerberos5_cc_name),
            ("KERBEROS5_PRINCIPAL", sec.kerberos5_principal),
            ("IGNORE_ANO_ENCRYPTION_FOR_TCPS", sec.ignore_ano_encryption_for_tcps),
        ]:
            if val:
                items.append(self._param(key, val, 3))

        if not items:
            return ""

        lines = [self._section_open("SECURITY", 2)]
        lines.extend(items)
        lines.append(self._section_close(2))
        return "\n".join(lines)
