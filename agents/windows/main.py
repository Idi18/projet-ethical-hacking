
import argparse
import json
import os
import platform
import socket
import sys

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.insert(0, BASE_DIR)

from shared.protocol import (
    DEFAULT_PORT,
    MessageType,
    decode_message,
    encode_message,
    error,
    hello,
    make_message,
    result,
)

from agents.windows.commandes_locales import executer_diagnostic


def parse_args():
    parser = argparse.ArgumentParser(
        description="Agent Windows - Projet Ethical Hacking"
    )
    parser.add_argument("--ip", required=True, help="IP du serveur")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--name", default="windows-agent")
    return parser.parse_args()


def get_real_ips():
    ips = []

    try:
        import psutil

        for addrs in psutil.net_if_addrs().values():
            for addr in addrs:
                if (
                    addr.family == socket.AF_INET
                    and not addr.address.startswith("127.")
                ):
                    ips.append(addr.address)

    except ImportError:
        hostname = socket.gethostname()
        ips = [
            ip for ip in socket.gethostbyname_ex(hostname)[2]
            if not ip.startswith("127.")
        ]

    return sorted(set(ips))


def receive_message(reader):
    line = reader.readline()

    if not line:
        raise ConnectionError("Connexion fermee")

    return decode_message(line)


def handle_message(client, msg):
    msg_type = msg.get("type")
    msg_id = msg.get("id")

    print(f"[*] Commande recue : {msg_type}")

    if msg_type == MessageType.PING.value:
        response = make_message(
            MessageType.PONG,
            msg_id=msg_id
        )

    elif msg_type == MessageType.SYSINFO.value:
        info = {
            "os": platform.system(),
            "version": platform.release(),
            "hostname": platform.node(),
        }
        response = result({"info": info})
        response["id"] = msg_id

    elif msg_type == MessageType.CMD.value:
        data = msg.get("data", {})
        if not isinstance(data, dict):
            data = {}

        commande = data.get("command")
        arguments = data.get("args", [])

        if (
            commande not in ("date", "ordinateur", "windows")
            or arguments != []
        ):
            response = error(
                "Diagnostic non autorise ou arguments invalides",
                "COMMAND_NOT_ALLOWED"
            )
        else:
            diagnostic = executer_diagnostic(commande)

            if diagnostic["ok"]:
                response = result({
                    "commande": commande,
                    "diagnostic": diagnostic,
                })
            else:
                response = error(
                    diagnostic.get("erreur", "Echec du diagnostic"),
                    "DIAGNOSTIC_FAILED"
                )

        response["id"] = msg_id

    elif msg_type == MessageType.REGISTRY.value:
        response = result({
            "fonction": "registry",
            "statut": "disponible",
            "execution": "locale uniquement"
        })
        response["id"] = msg_id

    elif msg_type == MessageType.SCREENSHOT.value:
        response = result({
            "fonction": "screenshot",
            "statut": "disponible",
            "execution": "locale uniquement"
        })
        response["id"] = msg_id

    else:
        print(f"[!] Commande inconnue : {msg_type}")
        response = error(
            f"Commande non reconnue : {msg_type}",
            "UNKNOWN_COMMAND"
        )
        response["id"] = msg_id

    client.sendall(encode_message(response))
    print(f"[+] Reponse envoyee : {response['type']}")


def connect_and_listen(ip, port, name):
    print(f"[*] Connexion a {ip}:{port}...")

    with socket.create_connection(
        (ip, port), timeout=10
    ) as client:

        client.settimeout(30)

        with client.makefile("rb") as reader:
            ips = get_real_ips()
            print(f"[+] Connecte ! Mes IP : {ips}")

            client.sendall(
                encode_message(
                    hello(name, "Windows", ips)
                )
            )

            ack = receive_message(reader)

            if ack.get("type") != MessageType.HELLO_ACK.value:
                raise ValueError("HELLO_ACK attendu")

            agent_id = ack.get("data", {}).get("agent_id")
            print(f"[+] HELLO_ACK recu : {agent_id}")

            while True:
                try:
                    message = receive_message(reader)

                except ConnectionError:
                    print("[*] Serveur deconnecte")
                    break

                handle_message(client, message)


def main():
    print("=== Agent Windows - Demarrage ===")

    args = parse_args()

    print(
        f"[*] Serveur={args.ip}:{args.port} "
        f"| Nom={args.name}"
    )

    try:
        connect_and_listen(
            args.ip,
            args.port,
            args.name
        )

    except KeyboardInterrupt:
        print("\n[*] Arret demande")

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[-] Erreur : {exc}")


if __name__ == "__main__":
    main()
