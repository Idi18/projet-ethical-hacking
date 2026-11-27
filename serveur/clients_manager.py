
from datetime import datetime
from threading import Lock
from uuid import uuid4


class ClientsManager:
    def __init__(self):
        self.clients = {}
        self.verrou = Lock()

    def enregistrer(self, nom, adresse, os_name, ips=None):
        """Enregistre un client de maniere securisee."""
        client_id = uuid4().hex[:8]

        client = {
            "id": client_id,
            "nom": nom,
            "adresse": adresse,
            "os": os_name,
            "ips": list(ips) if ips else [],
            "connecte_le": datetime.now().isoformat(
                timespec="seconds"
            ),
            "statut": "connecte",
        }

        with self.verrou:
            self.clients[client_id] = client

        print(
            f"[CLIENT] Connexion : {nom} ({os_name}) "
            f"| ID={client_id} | Adresse={adresse}",
            flush=True,
        )

        return client_id

    def deconnecter(self, client_id):
        """Marque un client comme deconnecte."""
        with self.verrou:
            client = self.clients.get(client_id)

            if client is None:
                return False

            client["statut"] = "deconnecte"
            client["deconnecte_le"] = datetime.now().isoformat(
                timespec="seconds"
            )
            nom = client["nom"]

        print(
            f"[CLIENT] Deconnexion : {nom} "
            f"| ID={client_id}",
            flush=True,
        )
        return True

    def liste_clients(self, connectes_seulement=False):
        """Retourne une copie de la liste des clients."""
        with self.verrou:
            clients = [
                {
                    **client,
                    "ips": list(client["ips"]),
                }
                for client in self.clients.values()
            ]

        if connectes_seulement:
            clients = [
                client for client in clients
                if client["statut"] == "connecte"
            ]

        return clients

    def nombre_connectes(self):
        """Compte les clients actuellement connectes."""
        with self.verrou:
            return sum(
                1
                for client in self.clients.values()
                if client["statut"] == "connecte"
            )
