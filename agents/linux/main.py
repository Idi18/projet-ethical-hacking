import argparse
import json
import platform
import socket
import uuid


def envoyer(sock, type_message, data=None, identifiant=None):
    message = {
        "type": type_message,
        "id": identifiant or str(uuid.uuid4()),
        "data": data if data is not None else {},
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

                if type_message == "ping":
                    envoyer(client, "pong", {}, identifiant)
                    print("[DEBIAN] PONG envoyé")

                elif type_message == "sysinfo":
                    infos = {
                        "hostname": nom,
                        "os": platform.system(),
                        "release": platform.release(),
                        "architecture": platform.machine(),
                        "python": platform.python_version()
                    }

                    envoyer(client, "result", {
                        "ok": True,
                        "payload": {"info": infos}
                    }, identifiant)

                    print("[DEBIAN] SYSINFO envoyé")

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