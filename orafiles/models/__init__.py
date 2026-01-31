"""Oracle configuration data models."""

from orafiles.models.protocol_address import TCPAddress, TCPSAddress, IPCAddress, NMPAddress, AddressList
from orafiles.models.listener import ListenerConfig, SIDEntry
from orafiles.models.tnsnames import TNSNamesConfig, ServiceEntry, ConnectData, FailoverMode
from orafiles.models.sqlnet import SQLNetConfig

__all__ = [
    "TCPAddress", "TCPSAddress", "IPCAddress", "NMPAddress", "AddressList",
    "ListenerConfig", "SIDEntry",
    "TNSNamesConfig", "ServiceEntry", "ConnectData", "FailoverMode",
    "SQLNetConfig",
]
