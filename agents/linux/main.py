import socket
import json
import platform
import socket as sock_module
import argparse
import subprocess  # <-- NOUVEAU : Pour exécuter des commandes

parser = argparse.ArgumentParser(description="Agent Linux")
parser.add_argument("--ip", type=str, default="127.0.0.1", help="Adresse IP du serveur")
parser.add_argument("--port", type=int, default=5000, help="Port du serveur")
args = parser.parse_args()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print(f"Connexion au serveur {args.ip}:{args.port}...")
    client.connect((args.ip, args.port))
    
    # 1. Identification
    infos_machine = {
        "type": "hello",
        "os": platform.system().lower(),
        "hostname": sock_module.gethostname()
    }
    client.send(json.dumps(infos_machine).encode("utf-8"))
    reponse = client.recv(1024).decode("utf-8")
    print(f"Serveur : {json.loads(reponse).get('message')}")
    
    print("\nEn attente des commandes du serveur...")
    
    # 2. Boucle d'écoute des commandes
    while True:
        # Le client attend passivement les ordres du serveur
        data = client.recv(4096) 
        if not data:
            break
            
        try:
            message = json.loads(data.decode("utf-8"))
            
            if message.get("type") == "command":
                commande_a_executer = message.get("cmd")
                print(f"\n[>] Commande reçue : {commande_a_executer}")
                
                # On exécute la commande via le shell (Linux)
                # capture_output=True permet de récupérer la sortie
                resultat = subprocess.run(
                    commande_a_executer, 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                
                # On prépare la réponse (stdout = succès, stderr = erreur)
                sortie = resultat.stdout if resultat.stdout else resultat.stderr
                if not sortie:
                    sortie = "Commande exécutée (aucune sortie)."
                
                # On renvoie le résultat au serveur
                reponse_cmd = {
                    "type": "result",
                    "output": sortie
                }
                client.send(json.dumps(reponse_cmd).encode("utf-8"))
                
        except json.JSONDecodeError:
            pass
            
except ConnectionRefusedError:
    print("Erreur : Le serveur est éteint.")
except KeyboardInterrupt:
    print("\nDéconnexion demandée.")
finally:
    client.close()
    print("Déconnecté.")
