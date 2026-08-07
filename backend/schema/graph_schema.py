from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class NodeType(Enum):
    CODE_FILE = "CODE_FILE"
    CRYPTO_USAGE = "CRYPTO_USAGE"
    CERTIFICATE = "CERTIFICATE"
    NETWORK_ENDPOINT = "NETWORK_ENDPOINT"
    LIBRARY = "LIBRARY"
    SENSITIVE_DATA = "SENSITIVE_DATA"


class EdgeType(Enum):
    USES_CRYPTO = "USES_CRYPTO"
    SECURES_ENDPOINT = "SECURES_ENDPOINT"
    PROTECTS_DATA = "PROTECTS_DATA"
    DEPENDS_ON = "DEPENDS_ON"
    CONTAINS_CRYPTO = "CONTAINS_CRYPTO"
    HOSTS_CERTIFICATE = "HOSTS_CERTIFICATE"
    HAS_VULNERABILITY = "HAS_VULNERABILITY"


@dataclass
class Node:
    id: str
    type: NodeType
    properties: Dict[str, Any]


@dataclass
class Edge:
    source_id: str
    target_id: str
    type: EdgeType
    properties: Dict[str, Any]
