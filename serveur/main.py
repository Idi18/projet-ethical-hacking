
import json
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore

from shared.protocol import (
    MessageType,
    encode_message,
    hello_ack,
)

from serveur.socket_server import SocketServer
from serveur.error_handler import gerer_erreur
from serveur.clients_manager import ClientsManager
from serveur.command_interpreter import CommandInterpreter


HOST = "0.0.0.0"
PORT = 5001
MAX_MESSAGE_SIZE = 1024 * 1024
MAX_CLIENTS = 4


def envoyer(sock, message):
    """Envoie un message JSON termine par une nouvelle ligne."""
    sock.sendall(encode_message(message))


def recevoir(fichier):
    """Recoit et valide un message JSON."""
    ligne = fichier.readline(MAX_MESSAGE_SIZE + 1)

    if not ligne:
        raise ConnectionError("Connexion fermee par le client")

    if len(ligne) > MAX_MESSAGE_SIZE:
        raise ValueError("Message trop volumineux")

    if not ligne.endswith(b"\n"):
        raise ValueError("Message JSON incomplet")

    message = json.loads(ligne.decode("utf-8"))

    if not isinstance(message, dict):
        raise ValueError("Message JSON invalide")

    if not isinstance(message.get("type"), str):
        raise ValueError("Type de message manquant")

    return message


def diagnostic(sock, fichier, message, interpreteur):
    """Envoie un diagnostic autorise et valide la reponse."""
    envoyer(sock, message)

    print(
        f"[ENVOI] Type={message['type']} "
        f"| ID={message['id']}",
        flush=True,
    )

    reponse = recevoir(fichier)

    interpreteur.verifier_reponse(
        reponse,
        identifiant_attendu=message["id"],
    )

    interpreteur.afficher_reponse(reponse)

    return reponse


def traiter_client(sock, adresse, gestionnaire, interpreteur):
    """Traite une session client dans son propre thread."""
    client_id = None

    try:
        sock.settimeout(15)

        with sock.makefile("rb") as fichier:
            premier_message = recevoir(fichier)

            if premier_message["type"] != MessageType.HELLO.value:
                raise ValueError("Message HELLO attendu")

            donnees = premier_message.get("data", {})

            if not isinstance(donnees, dict):
                raise ValueError("Informations HELLO invalides")

            nom = str(donnees.get("name", "Agent inconnu"))
            systeme = str(donnees.get("os", "Inconnu"))
            ips = donnees.get("ips", [])

            if not isinstance(ips, list):
                ips = []

            client_id = gestionnaire.enregistrer(
                nom,
                adresse[0],
                systeme,
                ips,
            )

            envoyer(
                sock,
                hello_ack(client_id, "Serveur Kali"),
            )

            print(
                f"[SERVEUR] HELLO accepte "
                f"| Client={client_id}",
                flush=True,
            )

            # Diagnostics communs : Windows et Linux
            diagnostic(
                sock,
                fichier,
                interpreteur.preparer_ping(),
                interpreteur,
            )

            diagnostic(
                sock,
                fichier,
                interpreteur.preparer_sysinfo(),
                interpreteur,
            )

            # Diagnostic Windows autorise
            if "windows" in systeme.lower():
                diagnostic(
                    sock,
                    fichier,
                    interpreteur.preparer_commande("date"),
                    interpreteur,
                )

                diagnostic(
                    sock,
                    fichier,
                    interpreteur.preparer_registry(),
                    interpreteur,
                )

            # Diagnostic Linux : interfaces reseau
            elif "linux" in systeme.lower():
                diagnostic(
                    sock,
                    fichier,
                    interpreteur.preparer_interfaces(),
                    interpreteur,
                )

            print(
                f"[SUCCES] Session de diagnostic terminee "
                f"| Client={client_id}",
                flush=True,
            )

    except Exception as erreur:
        gerer_erreur(erreur, "session_client")

    finally:
        if client_id is not None:
            gestionnaire.deconnecter(client_id)

        sock.close()

        print(
            f"[SERVEUR] Clients connectes : "
            f"{gestionnaire.nombre_connectes()}",
            flush=True,
        )


def session_thread(
    sock,
    adresse,
    gestionnaire,
    interpreteur,
    places,
):
    """Execute la session et libere sa place."""
    try:
        traiter_client(
            sock,
            adresse,
            gestionnaire,
            interpreteur,
        )
    finally:
        places.release()


def main():
    """Serveur TCP avec plusieurs clients simultanes."""
    gestionnaire = ClientsManager()
    interpreteur = CommandInterpreter()

    places = BoundedSemaphore(MAX_CLIENTS)

    print("[SERVEUR] Demarrage Kali V5", flush=True)
    print(
        f"[SERVEUR] Maximum clients simultanes : "
        f"{MAX_CLIENTS}",
        flush=True,
    )

    interpreteur.afficher_commandes()

    try:
        with ThreadPoolExecutor(
            max_workers=MAX_CLIENTS
        ) as executant:

            with SocketServer(HOST, PORT) as serveur:

                while True:
                    connexion = serveur.accepter_client()

                    if connexion is None:
                        continue

                    sock, adresse = connexion

                    if not places.acquire(blocking=False):
                        print(
                            "[SERVEUR] Limite de clients atteinte",
                            flush=True,
                        )
                        sock.close()
                        continue

                    print(
                        f"[SERVEUR] Connexion depuis "
                        f"{adresse[0]}:{adresse[1]}",
                        flush=True,
                    )

                    try:
                        executant.submit(
                            session_thread,
                            sock,
                            adresse,
                            gestionnaire,
                            interpreteur,
                            places,
                        )
                    except Exception:
                        places.release()
                        sock.close()
                        raise

    except KeyboardInterrupt:
        print(
            "\n[SERVEUR] Arret demande",
            flush=True,
        )

    except OSError as erreur:
        gerer_erreur(erreur, "demarrage_serveur")

    finally:
        print(
            "[SERVEUR] Arret du serveur Kali V5",
            flush=True,
        )


if __name__ == "__main__":
    main()
