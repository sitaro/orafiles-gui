"""TNS Names configuration data model (tnsnames.ora)."""

from __future__ import annotations
from dataclasses import dataclass, field
from orafiles.models.base import BaseModel, ValidationError
from orafiles.models.protocol_address import Address, AddressList, address_from_ast
from orafiles.parser.ast_nodes import ConfigFile, NVList, NVPair, NVValue


@dataclass
class FailoverMode(BaseModel):
    type: str = ""       # NONE, SESSION, SELECT, TRANSACTION
    method: str = ""     # NONE, BASIC, PRECONNECT
    backup: str = ""
    retries: str = ""
    delay: str = ""
    transaction: str = ""  # ON/OFF

    @classmethod
    def from_ast(cls, nvlist: NVList) -> FailoverMode:
        return cls(
            type=nvlist.get_value("TYPE") or "",
            method=nvlist.get_value("METHOD") or "",
            backup=nvlist.get_value("BACKUP") or "",
            retries=nvlist.get_value("RETRIES") or "",
            delay=nvlist.get_value("DELAY") or "",
            transaction=nvlist.get_value("TRANSACTION") or "",
        )


@dataclass
class ConnectData(BaseModel):
    service_name: str = ""
    sid: str = ""
    instance_name: str = ""
    server: str = ""         # DEDICATED, SHARED, POOLED
    hs: str = ""             # OK or empty
    global_name: str = ""
    rdb_database: str = ""
    colocation_tag: str = ""
    connection_id_prefix: str = ""
    pool_connection_class: str = ""
    pool_purity: str = ""    # NEW, SELF
    server_wait_timeout: str = ""
    sharding_key: str = ""
    super_sharding_key: str = ""
    tunnel_service_name: str = ""
    failover_mode: FailoverMode = field(default_factory=FailoverMode)

    @classmethod
    def from_ast(cls, nvlist: NVList) -> ConnectData:
        cd = cls(
            service_name=nvlist.get_value("SERVICE_NAME") or "",
            sid=nvlist.get_value("SID") or "",
            instance_name=nvlist.get_value("INSTANCE_NAME") or "",
            server=nvlist.get_value("SERVER") or "",
            hs=nvlist.get_value("HS") or "",
            global_name=nvlist.get_value("GLOBAL_NAME") or "",
            rdb_database=nvlist.get_value("RDB_DATABASE") or "",
            colocation_tag=nvlist.get_value("COLOCATION_TAG") or "",
            connection_id_prefix=nvlist.get_value("CONNECTION_ID_PREFIX") or "",
            pool_connection_class=nvlist.get_value("POOL_CONNECTION_CLASS") or "",
            pool_purity=nvlist.get_value("POOL_PURITY") or "",
            server_wait_timeout=nvlist.get_value("SERVER_WAIT_TIMEOUT") or "",
            sharding_key=nvlist.get_value("SHARDING_KEY") or "",
            super_sharding_key=nvlist.get_value("SUPER_SHARDING_KEY") or "",
            tunnel_service_name=nvlist.get_value("TUNNEL_SERVICE_NAME") or "",
        )
        fo = nvlist.find("FAILOVER_MODE")
        if fo and isinstance(fo.value, NVList):
            cd.failover_mode = FailoverMode.from_ast(fo.value)
        return cd


@dataclass
class DescriptionSecurity(BaseModel):
    authentication_service: str = ""
    ssl_server_cert_dn: str = ""
    ssl_server_dn_match: str = ""  # ON/OFF
    ssl_version: str = ""
    wallet_location: str = ""
    kerberos5_cc_name: str = ""
    kerberos5_principal: str = ""
    ignore_ano_encryption_for_tcps: str = ""  # ON/OFF

    @classmethod
    def from_ast(cls, nvlist: NVList) -> DescriptionSecurity:
        sec = nvlist.find("SECURITY")
        if sec and isinstance(sec.value, NVList):
            sl = sec.value
            return cls(
                authentication_service=sl.get_value("AUTHENTICATION_SERVICE") or "",
                ssl_server_cert_dn=sl.get_value("SSL_SERVER_CERT_DN") or "",
                ssl_server_dn_match=sl.get_value("SSL_SERVER_DN_MATCH") or "",
                ssl_version=sl.get_value("SSL_VERSION") or "",
                wallet_location=sl.get_value("WALLET_LOCATION") or "",
                kerberos5_cc_name=sl.get_value("KERBEROS5_CC_NAME") or "",
                kerberos5_principal=sl.get_value("KERBEROS5_PRINCIPAL") or "",
                ignore_ano_encryption_for_tcps=sl.get_value("IGNORE_ANO_ENCRYPTION_FOR_TCPS") or "",
            )
        return cls()


@dataclass
class ServiceEntry(BaseModel):
    """A single TNS service entry (net service name)."""
    name: str = ""
    addresses: list[Address] = field(default_factory=list)
    address_list_failover: str = ""  # ON/OFF
    address_list_load_balance: str = ""  # ON/OFF
    address_list_source_route: str = ""  # ON/OFF
    connect_data: ConnectData = field(default_factory=ConnectData)
    security: DescriptionSecurity = field(default_factory=DescriptionSecurity)

    # Description options
    failover: str = ""  # ON/OFF
    load_balance: str = ""  # ON/OFF
    source_route: str = ""  # ON/OFF
    sdu: str = ""
    enable: str = ""  # BROKEN
    expire_time: str = ""
    recv_buf_size: str = ""
    send_buf_size: str = ""
    type_of_service: str = ""
    https_proxy: str = ""
    https_proxy_port: str = ""

    # Timeouts
    connect_timeout: str = ""
    retry_count: str = ""
    retry_delay: str = ""
    transport_connect_timeout: str = ""
    recv_timeout: str = ""

    # Compression
    compression: str = ""  # ON/OFF
    compression_levels: str = ""  # LOW, HIGH

    def validate(self) -> list[ValidationError]:
        errors = []
        if not self.name:
            errors.append(ValidationError("name", "Service name is required"))
        for i, addr in enumerate(self.addresses):
            for err in addr.validate():
                errors.append(ValidationError(f"address[{i}].{err.field}", err.message))
        return errors

    @classmethod
    def from_ast(cls, name: str, nvlist: NVList) -> ServiceEntry:
        """Parse a service entry from the top-level NVPair value."""
        se = cls(name=name)

        # Navigate into DESCRIPTION or DESCRIPTION_LIST
        desc = nvlist.find("DESCRIPTION")
        desc_list = nvlist.find("DESCRIPTION_LIST")

        if desc_list and isinstance(desc_list.value, NVList):
            # Use first DESCRIPTION in list
            first_desc = desc_list.value.find("DESCRIPTION")
            if first_desc and isinstance(first_desc.value, NVList):
                desc = first_desc

        if desc and isinstance(desc.value, NVList):
            target = desc.value
        else:
            # The list itself might be the description content
            target = nvlist

        # Parse addresses
        addr_list = target.find("ADDRESS_LIST")
        if addr_list and isinstance(addr_list.value, NVList):
            al = addr_list.value
            se.address_list_failover = al.get_value("FAILOVER") or ""
            se.address_list_load_balance = al.get_value("LOAD_BALANCE") or ""
            se.address_list_source_route = al.get_value("SOURCE_ROUTE") or ""
            for ap in al.find_all("ADDRESS"):
                if isinstance(ap.value, NVList):
                    se.addresses.append(address_from_ast(ap.value))
        else:
            # Direct ADDRESS entries
            for ap in target.find_all("ADDRESS"):
                if isinstance(ap.value, NVList):
                    se.addresses.append(address_from_ast(ap.value))

        # Connect Data
        cd = target.find("CONNECT_DATA")
        if cd and isinstance(cd.value, NVList):
            se.connect_data = ConnectData.from_ast(cd.value)

        # Security
        se.security = DescriptionSecurity.from_ast(target)

        # Description options
        se.failover = target.get_value("FAILOVER") or ""
        se.load_balance = target.get_value("LOAD_BALANCE") or ""
        se.source_route = target.get_value("SOURCE_ROUTE") or ""
        se.sdu = target.get_value("SDU") or ""
        se.enable = target.get_value("ENABLE") or ""
        se.expire_time = target.get_value("EXPIRE_TIME") or ""
        se.recv_buf_size = target.get_value("RECV_BUF_SIZE") or ""
        se.send_buf_size = target.get_value("SEND_BUF_SIZE") or ""
        se.type_of_service = target.get_value("TYPE_OF_SERVICE") or ""
        se.https_proxy = target.get_value("HTTPS_PROXY") or ""
        se.https_proxy_port = target.get_value("HTTPS_PROXY_PORT") or ""

        # Timeouts
        se.connect_timeout = target.get_value("CONNECT_TIMEOUT") or ""
        se.retry_count = target.get_value("RETRY_COUNT") or ""
        se.retry_delay = target.get_value("RETRY_DELAY") or ""
        se.transport_connect_timeout = target.get_value("TRANSPORT_CONNECT_TIMEOUT") or ""
        se.recv_timeout = target.get_value("RECV_TIMEOUT") or ""

        # Compression
        se.compression = target.get_value("COMPRESSION") or ""
        se.compression_levels = target.get_value("COMPRESSION_LEVELS") or ""

        return se


@dataclass
class TNSNamesConfig(BaseModel):
    """Complete tnsnames.ora configuration."""
    services: list[ServiceEntry] = field(default_factory=list)
    ifile: str = ""

    def validate(self) -> list[ValidationError]:
        errors = []
        for i, svc in enumerate(self.services):
            for err in svc.validate():
                errors.append(ValidationError(f"service[{i}].{err.field}", err.message))
        return errors

    @classmethod
    def from_ast(cls, config: ConfigFile) -> TNSNamesConfig:
        tc = cls()
        for entry in config.entries:
            key = entry.key.upper()
            if key == "IFILE":
                tc.ifile = entry.get_value() or ""
            elif isinstance(entry.value, NVList):
                tc.services.append(ServiceEntry.from_ast(entry.key, entry.value))
        return tc
