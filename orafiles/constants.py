"""Oracle parameter constants, enums, and defaults."""

from enum import Enum

# --- Protocol Types ---

class Protocol(str, Enum):
    TCP = "TCP"
    TCPS = "TCPS"
    IPC = "IPC"
    NMP = "NMP"


class IPVersion(str, Enum):
    V4 = "v4"
    V6 = "v6"


# --- Listener Parameters ---

class OnOffEnum(str, Enum):
    ON = "ON"
    OFF = "OFF"


class TraceLevel(str, Enum):
    OFF = "OFF"
    USER = "USER"
    ADMIN = "ADMIN"
    SUPPORT = "SUPPORT"


class SecureRegister(str, Enum):
    TCP = "TCP"
    TCPS = "TCPS"
    IPC = "IPC"


# --- TNS Connect Data ---

class ServerType(str, Enum):
    DEDICATED = "DEDICATED"
    SHARED = "SHARED"
    POOLED = "POOLED"


class HSOption(str, Enum):
    NONE = ""
    OK = "OK"


class FailoverType(str, Enum):
    NONE = "NONE"
    SESSION = "SESSION"
    SELECT = "SELECT"
    TRANSACTION = "TRANSACTION"


class FailoverMethod(str, Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    PRECONNECT = "PRECONNECT"


class PoolPurity(str, Enum):
    NEW = "NEW"
    SELF = "SELF"


# --- SQLNet Parameters ---

class NamingMethod(str, Enum):
    TNSNAMES = "TNSNAMES"
    LDAP = "LDAP"
    EZCONNECT = "EZCONNECT"
    HOSTNAME = "HOSTNAME"
    NIS = "NIS"


class EncryptionLevel(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REQUESTED = "REQUESTED"
    REQUIRED = "REQUIRED"


class EncryptionAlgorithm(str, Enum):
    AES256 = "AES256"
    AES192 = "AES192"
    AES128 = "AES128"
    DES3 = "3DES168"
    DES = "DES"
    DES56 = "DES56C"
    RC4_256 = "RC4_256"
    RC4_128 = "RC4_128"
    RC4_56 = "RC4_56"
    RC4_40 = "RC4_40"


class ChecksumLevel(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REQUESTED = "REQUESTED"
    REQUIRED = "REQUIRED"


class ChecksumAlgorithm(str, Enum):
    SHA256 = "SHA256"
    SHA384 = "SHA384"
    SHA512 = "SHA512"
    SHA1 = "SHA1"
    MD5 = "MD5"


class SSLVersion(str, Enum):
    TLS1_0 = "1.0"
    TLS1_1 = "1.1"
    TLS1_2 = "1.2"
    TLS1_3 = "1.3"
    UNDETERMINED = "UNDETERMINED"


class AuthService(str, Enum):
    ALL = "ALL"
    NONE = "NONE"
    NTS = "NTS"
    KERBEROS5 = "KERBEROS5"
    RADIUS = "RADIUS"
    TCPS = "TCPS"


class CompressionLevel(str, Enum):
    LOW = "LOW"
    HIGH = "HIGH"


class LogonVersion(str, Enum):
    V8 = "8"
    V10 = "10"
    V11 = "11"
    V12 = "12"
    V12A = "12a"


class KerberosDelegation(str, Enum):
    FULL = "FULL"
    CONSTRAINED = "CONSTRAINED"


# --- SSL Cipher Suites ---

SSL_CIPHER_SUITES = [
    "SSL_RSA_WITH_AES_256_CBC_SHA",
    "SSL_RSA_WITH_AES_256_CBC_SHA256",
    "SSL_RSA_WITH_AES_256_GCM_SHA384",
    "SSL_RSA_WITH_AES_128_CBC_SHA",
    "SSL_RSA_WITH_AES_128_CBC_SHA256",
    "SSL_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "SSL_RSA_WITH_3DES_EDE_CBC_SHA",
    "SSL_RSA_WITH_RC4_128_SHA",
    "SSL_RSA_WITH_RC4_128_MD5",
]

# --- Default Values ---

DEFAULTS = {
    "listener_name": "LISTENER",
    "tcp_host": "localhost",
    "tcp_port": "1521",
    "ipc_key": "EXTPROC1",
    "sdu": "8192",
    "inbound_connect_timeout": "60",
    "default_sdu_size": "8192",
    "expire_time": "0",
    "outbound_connect_timeout": "0",
    "recv_timeout": "0",
    "send_timeout": "0",
}
