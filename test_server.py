import socket
import time
import base64
from shared.protocol import *

def start_fake_server():
    host = "0.0.0.0"
    port = 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    print(f"[*] Faux serveur à l'écoute sur le port {port}...")
    
    conn, addr = server.accept()
    print(f"[+] Agent connecté depuis {addr[0]}:{addr[1]}")
    
    # 1. Lire le HELLO
    data = conn.recv(MAX_MESSAGE_SIZE).decode('utf-8')
    msg = decode_message(data)
    print(f"[+] Message reçu : {msg['type']} de {msg['data'].get('name')}")
    
    # 2. Envoyer HELLO_ACK
    conn.sendall(encode_message(hello_ack("test-agent-123")))
    time.sleep(0.5)
    
    # 3. Test Registre
    print("\n[*] Test 1 : Envoi de la commande REGISTRY...")
    conn.sendall(encode_message(make_message(MessageType.REGISTRY)))
    time.sleep(0.5)
    res_data = conn.recv(MAX_MESSAGE_SIZE).decode('utf-8')
    res_msg = decode_message(res_data)
    print(f"[+] Résultat REGISTRY : {res_msg['data'].get('payload', {}).get('output')}")
    
    # 4. Test SAM
    print("\n[*] Test 2 : Envoi de la commande SAM_AUDIT...")
    conn.sendall(encode_message(make_message(MessageType.SAM_AUDIT)))
    time.sleep(0.5)
    res_data = conn.recv(MAX_MESSAGE_SIZE).decode('utf-8')
    res_msg = decode_message(res_data)
    print(f"[+] Résultat SAM : {res_msg['data'].get('payload', {}).get('output')}")
    
    # 5. Test Screenshot
    print("\n[*] Test 3 : Envoi de la commande SCREENSHOT...")
    conn.sendall(encode_message(make_message(MessageType.SCREENSHOT)))
    
    # Pour le screenshot, le message est très gros, on doit lire plusieurs fois
    full_data = b""
    while True:
        chunk = conn.recv(MAX_MESSAGE_SIZE)
        if not chunk:
            break
        full_data += chunk
        if b"\n" in full_data: # Fin du message
            break
    
    res_msg = decode_message(full_data)
    b64_img = res_msg['data'].get('payload', {}).get('image_base64')
    
    if b64_img:
        print(f"[+] Résultat SCREENSHOT : Image reçue (Taille: {len(b64_img)} caractères)")
        # On sauvegarde l'image pour que tu puisses la voir !
        with open("capture_test.png", "wb") as f:
            f.write(base64.b64decode(b64_img))
        print("[*] L'image a été sauvegardée sous le nom 'capture_test.png' dans ton dossier !")
    else:
        print(f"[-] Erreur screenshot: {res_msg}")
        
    conn.close()
    print("\n[*] Test terminé avec succès.")

if __name__ == "__main__":
    start_fake_server()
