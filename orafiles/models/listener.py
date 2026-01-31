"""Listener configuration data model (listener.ora)."""

from __future__ import annotations
from dataclasses import dataclass, field
from orafiles.models.base import BaseModel, ValidationError
from orafiles.models.protocol_address import Address, AddressList, address_from_ast
from orafiles.parser.ast_nodes import ConfigFile, NVList, NVPair, NVValue


@dataclass
class SIDEntry(BaseModel):
    sid_name: str = ""
    global_dbname: str = ""
    oracle_home: str = ""
    program: str = ""
    envs: str = ""
    sdu: str = ""

    def validate(self) -> list[ValidationError]:
        errors = []
        errors.extend(self._validate_positive_int(self.sdu, "sdu"))
        return errors

    @classmethod
    def from_ast(cls, nvlist: NVList) -> SIDEntry:
        return cls(
            sid_name=nvlist.get_value("SID_NAME") or "",
            global_dbname=nvlist.get_value("GLOBAL_DBNAME") or "",
            oracle_home=nvlist.get_value("ORACLE_HOME") or "",
            program=nvlist.get_value("PROGRAM") or "",
            envs=nvlist.get_value("ENVS") or "",
            sdu=nvlist.get_value("SDU") or "",
        )

    def display_name(self) -> str:
        return self.sid_name or self.global_dbname or "(unnamed)"


@dataclass
class ListenerConfig(BaseModel):
    # Identity
    name: str = "LISTENER"
    addresses: list[Address] = field(default_factory=list)

    # SID List
    sid_list: list[SIDEntry] = field(default_factory=list)

    # Control parameters
    admin_restrictions: str = ""  # ON/OFF
    default_service: str = ""
    dynamic_registration: str = ""  # ON/OFF
    inbound_connect_timeout: str = ""
    max_all_connections: str = ""
    max_reg_connections: str = ""
    save_config_on_stop: str = ""  # ON/OFF
    use_sid_as_service: str = ""  # ON/OFF
    dedicated_through_broker: str = ""  # ON/OFF
    allow_multiple_redirects: str = ""  # ON/OFF
    crs_notification: str = ""  # ON/OFF
    enable_exadirect: str = ""  # ON/OFF
    subscribe_for_node_down_event: str = ""  # ON/OFF

    # Rate Limiting
    connection_rate: str = ""
    service_rate: str = ""

    # Security
    valid_node_checking_registration: str = ""  # ON/OFF
    registration_invited_nodes: str = ""
    registration_excluded_nodes: str = ""
    local_registration_address: str = ""
    remote_registration_address: str = ""
    secure_register: str = ""
    secure_protocol: str = ""
    secure_control: str = ""

    # SSL/TLS
    ssl_version: str = ""
    ssl_client_authentication: str = ""  # TRUE/FALSE
    ssl_cipher_suites: str = ""
    wallet_location: str = ""

    # Diagnostics
    diag_adr_enabled: str = ""  # ON/OFF
    adr_base: str = ""
    logging: str = ""  # ON/OFF
    log_file_num: str = ""
    log_file_size: str = ""
    trace_level: str = ""
    trace_timestamp: str = ""  # ON/OFF
    trace_directory: str = ""
    trace_file: str = ""
    trace_fileage: str = ""
    trace_filelen: str = ""
    trace_fileno: str = ""
    log_directory: str = ""
    log_file: str = ""

    def validate(self) -> list[ValidationError]:
        errors = []
        if not self.name:
            errors.append(ValidationError("name", "Listener name is required"))
        for i, addr in enumerate(self.addresses):
            for err in addr.validate():
                errors.append(ValidationError(f"address[{i}].{err.field}", err.message))
        for i, sid in enumerate(self.sid_list):
            for err in sid.validate():
                errors.append(ValidationError(f"sid[{i}].{err.field}", err.message))
        errors.extend(self._validate_positive_int(self.inbound_connect_timeout, "inbound_connect_timeout"))
        errors.extend(self._validate_positive_int(self.max_all_connections, "max_all_connections"))
        errors.extend(self._validate_positive_int(self.max_reg_connections, "max_reg_connections"))
        errors.extend(self._validate_positive_int(self.connection_rate, "connection_rate"))
        errors.extend(self._validate_positive_int(self.service_rate, "service_rate"))
        return errors

    @classmethod
    def from_ast(cls, config: ConfigFile) -> ListenerConfig:
        lc = cls()

        # Determine listener name from first *_LISTENER or LISTENER entry
        for entry in config.entries:
            key = entry.key.upper()
            if key.endswith("_LISTENER") or key == "LISTENER":
                # This is likely the listener name part of a parameter
                pass

        # Try to find listener name
        # listener.ora uses <LISTENER_NAME> = ... pattern
        # Find the address list entry: <NAME> = (ADDRESS_LIST = ...) or (ADDRESS = ...)
        for entry in config.entries:
            key = entry.key.upper()
            if isinstance(entry.value, NVList):
                # Check if this looks like a listener address definition
                addr_list = entry.value.find("ADDRESS_LIST")
                addr = entry.value.find("ADDRESS")
                if addr_list or addr:
                    lc.name = entry.key
                    if addr_list and isinstance(addr_list.value, NVList):
                        for ap in addr_list.value.find_all("ADDRESS"):
                            if isinstance(ap.value, NVList):
                                lc.addresses.append(address_from_ast(ap.value))
                    elif addr and isinstance(addr.value, NVList):
                        lc.addresses.append(address_from_ast(addr.value))
                    # Also check for direct ADDRESS entries in the top list
                    for ap in entry.value.find_all("ADDRESS"):
                        if isinstance(ap.value, NVList) and ap != addr:
                            lc.addresses.append(address_from_ast(ap.value))
                    break

        # SID_LIST_<NAME>
        for entry in config.entries:
            key = entry.key.upper()
            if key.startswith("SID_LIST"):
                if isinstance(entry.value, NVList):
                    for sid_desc in entry.value.find_all("SID_DESC"):
                        if isinstance(sid_desc.value, NVList):
                            lc.sid_list.append(SIDEntry.from_ast(sid_desc.value))

        # Helper to get prefixed param
        def _get(base_key: str) -> str:
            # Try <NAME>_<KEY> first, then <KEY>_<NAME>, then just <KEY>
            for prefix_fmt in [f"{lc.name}_{base_key}", f"{base_key}_{lc.name}", base_key]:
                val = config.get_value(prefix_fmt)
                if val:
                    return val
            return ""

        # Control parameters
        lc.admin_restrictions = _get("ADMIN_RESTRICTIONS")
        lc.default_service = _get("DEFAULT_SERVICE")
        lc.dynamic_registration = _get("DYNAMIC_REGISTRATION")
        lc.inbound_connect_timeout = _get("INBOUND_CONNECT_TIMEOUT")
        lc.max_all_connections = _get("MAX_ALL_CONNECTIONS")
        lc.max_reg_connections = _get("MAX_REG_CONNECTIONS")
        lc.save_config_on_stop = _get("SAVE_CONFIG_ON_STOP")
        lc.use_sid_as_service = _get("USE_SID_AS_SERVICE")
        lc.dedicated_through_broker = _get("DEDICATED_THROUGH_BROKER")
        lc.allow_multiple_redirects = _get("ALLOW_MULTIPLE_REDIRECTS")
        lc.crs_notification = _get("CRS_NOTIFICATION")
        lc.enable_exadirect = _get("ENABLE_EXADIRECT")
        lc.subscribe_for_node_down_event = _get("SUBSCRIBE_FOR_NODE_DOWN_EVENT")

        # Rate Limiting
        lc.connection_rate = _get("CONNECTION_RATE")
        lc.service_rate = _get("SERVICE_RATE")

        # Security
        lc.valid_node_checking_registration = _get("VALID_NODE_CHECKING_REGISTRATION")
        lc.registration_invited_nodes = _get("REGISTRATION_INVITED_NODES")
        lc.registration_excluded_nodes = _get("REGISTRATION_EXCLUDED_NODES")
        lc.local_registration_address = _get("LOCAL_REGISTRATION_ADDRESS")
        lc.remote_registration_address = _get("REMOTE_REGISTRATION_ADDRESS")
        lc.secure_register = _get("SECURE_REGISTER")
        lc.secure_protocol = _get("SECURE_PROTOCOL")
        lc.secure_control = _get("SECURE_CONTROL")

        # SSL/TLS
        lc.ssl_version = _get("SSL_VERSION")
        lc.ssl_client_authentication = _get("SSL_CLIENT_AUTHENTICATION")
        lc.ssl_cipher_suites = _get("SSL_CIPHER_SUITES")
        lc.wallet_location = _get("WALLET_LOCATION")

        # Diagnostics
        lc.diag_adr_enabled = _get("DIAG_ADR_ENABLED")
        lc.adr_base = _get("ADR_BASE")
        lc.logging = _get("LOGGING")
        lc.log_file_num = _get("LOG_FILE_NUM")
        lc.log_file_size = _get("LOG_FILE_SIZE")
        lc.trace_level = _get("TRACE_LEVEL")
        lc.trace_timestamp = _get("TRACE_TIMESTAMP")
        lc.trace_directory = _get("TRACE_DIRECTORY")
        lc.trace_file = _get("TRACE_FILE")
        lc.trace_fileage = _get("TRACE_FILEAGE")
        lc.trace_filelen = _get("TRACE_FILELEN")
        lc.trace_fileno = _get("TRACE_FILENO")
        lc.log_directory = _get("LOG_DIRECTORY")
        lc.log_file = _get("LOG_FILE")

        return lc
