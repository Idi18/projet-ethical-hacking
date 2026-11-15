"""
shared/protocol.py
Protocole de communication JSON entre le serveur et les agents.
Format d'un message : {"type": "...", "id": "...", "data": {...}}
"""

import json
import uuid
from enum import Enum
from typing import Any, Dict, Optional

class MessageType(str, Enum):
    # Handshake / cycle de vie
    HELLO       = "hello"        
    HELLO_ACK   = "hello_ack"    
    PING        = "ping"         
    PONG        = "pong"         
    BYE         = "bye"          

    # Commandes serveur -> agent
    CMD         = "cmd"          
    SYSINFO     = "sysinfo"      
    SCREENSHOT  = "screenshot"   
    SAM_AUDIT   = "sam_audit"    
    REGISTRY    = "registry"     
    PASSWD      = "passwd"       
    LIST_DIR    = "list_dir"     

    # Réponses agent -> serveur
    RESULT      = "result"       
    ERROR       = "error"        

def make_message(msg_type: MessageType, data: Optional[Dict[str, Any]] = None,
                 msg_id: Optional[str] = None) -> Dict[str, Any]:
    return {
        "type": msg_type.value if isinstance(msg_type, MessageType) else msg_type,
        "id": msg_id or str(uuid.uuid4()),
        "data": data or {},
    }

def encode_message(msg: Dict[str, Any]) -> bytes:
    return (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")

def decode_message(raw: bytes) -> Dict[str, Any]:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    raw = raw.strip()
    if not raw:
        raise ValueError("Message vide")
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalide: {e}")
    if "type" not in msg:
        raise ValueError("Message sans champ 'type'")
    return msg

def hello(agent_name: str, os_name: str, ips: list, version: str = "1.0") -> Dict[str, Any]:
    return make_message(MessageType.HELLO, {
        "name": agent_name, "os": os_name, "ips": ips, "version": version,
    })

def hello_ack(agent_id: str, server_name: str = "kali-server") -> Dict[str, Any]:
    return make_message(MessageType.HELLO_ACK, {"agent_id": agent_id, "server": server_name})

def cmd(command: str, args: Optional[list] = None) -> Dict[str, Any]:
    return make_message(MessageType.CMD, {"command": command, "args": args or []})

def result(payload: Any, ok: bool = True) -> Dict[str, Any]:
    return make_message(MessageType.RESULT, {"ok": ok, "payload": payload})

def error(message: str, code: str = "GENERIC") -> Dict[str, Any]:
    return make_message(MessageType.ERROR, {"code": code, "message": message})

# Constantes partagées
DEFAULT_PORT = 5000
DEFAULT_HOST = "0.0.0.0"
DEFAULT_AGENT_IP = "127.0.0.1"
ENCODING = "utf-8"
MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10 Mo max par message (screenshots)