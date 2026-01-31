"""Protocol address models shared across listener.ora and tnsnames.ora."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union
from orafiles.models.base import BaseModel, ValidationError
from orafiles.parser.ast_nodes import NVPair, NVList, NVValue


@dataclass
class TCPAddress(BaseModel):
    host: str = "localhost"
    port: str = "1521"
    ip: str = ""  # v4, v6
    queuesize: str = ""
    buf_size: str = ""
    rate_limit: str = ""

    def validate(self) -> list[ValidationError]:
        errors = []
        if not self.host:
            errors.append(ValidationError("host", "Host is required"))
        errors.extend(self._validate_port(self.port, "port"))
        errors.extend(self._validate_positive_int(self.queuesize, "queuesize"))
        errors.extend(self._validate_positive_int(self.buf_size, "buf_size"))
        return errors

    @classmethod
    def from_ast(cls, nvlist: NVList) -> TCPAddress:
        return cls(
            host=nvlist.get_value("HOST") or "localhost",
            port=nvlist.get_value("PORT") or "1521",
            ip=nvlist.get_value("IP") or "",
            queuesize=nvlist.get_value("QUEUESIZE") or "",
            buf_size=nvlist.get_value("BUF_SIZE") or "",
            rate_limit=nvlist.get_value("RATE_LIMIT") or "",
        )


@dataclass
class TCPSAddress(BaseModel):
    host: str = "localhost"
    port: str = "2484"
    ip: str = ""
    queuesize: str = ""
    buf_size: str = ""
    rate_limit: str = ""

    def validate(self) -> list[ValidationError]:
        errors = []
        if not self.host:
            errors.append(ValidationError("host", "Host is required"))
        errors.extend(self._validate_port(self.port, "port"))
        return errors

    @classmethod
    def from_ast(cls, nvlist: NVList) -> TCPSAddress:
        return cls(
            host=nvlist.get_value("HOST") or "localhost",
            port=nvlist.get_value("PORT") or "2484",
            ip=nvlist.get_value("IP") or "",
            queuesize=nvlist.get_value("QUEUESIZE") or "",
            buf_size=nvlist.get_value("BUF_SIZE") or "",
            rate_limit=nvlist.get_value("RATE_LIMIT") or "",
        )


@dataclass
class IPCAddress(BaseModel):
    key: str = "EXTPROC1"

    def validate(self) -> list[ValidationError]:
        errors = []
        if not self.key:
            errors.append(ValidationError("key", "IPC KEY is required"))
        return errors

    @classmethod
    def from_ast(cls, nvlist: NVList) -> IPCAddress:
        return cls(key=nvlist.get_value("KEY") or "EXTPROC1")


@dataclass
class NMPAddress(BaseModel):
    server: str = ""
    pipe: str = ""

    def validate(self) -> list[ValidationError]:
        errors = []
        if not self.pipe:
            errors.append(ValidationError("pipe", "Pipe name is required"))
        return errors

    @classmethod
    def from_ast(cls, nvlist: NVList) -> NMPAddress:
        return cls(
            server=nvlist.get_value("SERVER") or "",
            pipe=nvlist.get_value("PIPE") or "",
        )


Address = Union[TCPAddress, TCPSAddress, IPCAddress, NMPAddress]


def address_from_ast(nvlist: NVList) -> Address:
    """Create an Address from a parsed ADDRESS NVList."""
    protocol = (nvlist.get_value("PROTOCOL") or "TCP").upper()
    if protocol == "TCPS":
        return TCPSAddress.from_ast(nvlist)
    elif protocol == "IPC":
        return IPCAddress.from_ast(nvlist)
    elif protocol == "NMP":
        return NMPAddress.from_ast(nvlist)
    else:
        return TCPAddress.from_ast(nvlist)


def get_protocol_name(addr: Address) -> str:
    if isinstance(addr, TCPSAddress):
        return "TCPS"
    elif isinstance(addr, IPCAddress):
        return "IPC"
    elif isinstance(addr, NMPAddress):
        return "NMP"
    return "TCP"


@dataclass
class AddressList(BaseModel):
    """A list of protocol addresses with optional failover/load_balance."""
    addresses: list[Address] = field(default_factory=list)
    failover: str = ""  # ON/OFF
    load_balance: str = ""  # ON/OFF
    source_route: str = ""  # ON/OFF

    def validate(self) -> list[ValidationError]:
        errors = []
        for i, addr in enumerate(self.addresses):
            for err in addr.validate():
                errors.append(ValidationError(f"address[{i}].{err.field}", err.message))
        return errors

    @classmethod
    def from_ast(cls, nvlist: NVList) -> AddressList:
        addresses = []
        for pair in nvlist.find_all("ADDRESS"):
            if isinstance(pair.value, NVList):
                addresses.append(address_from_ast(pair.value))
        return cls(
            addresses=addresses,
            failover=nvlist.get_value("FAILOVER") or "",
            load_balance=nvlist.get_value("LOAD_BALANCE") or "",
            source_route=nvlist.get_value("SOURCE_ROUTE") or "",
        )
