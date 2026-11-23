
from datetime import datetime
from uuid import uuid4


class ClientsManager:
    def __init__(self):
        self.clients = {}

    def enregistrer(self, nom, adresse, os_name, ips=None):
        """Enregistre un client et retourne son identifiant."""
        client_id = uuid4().hex[:8]

        self.clients[client_id] = {
            "id": client_id,
            "nom": nom,
            "adresse": adresse,
            "os": os_name,
            "ips": ips or [],
            "connecte_le": datetime.now().isoformat(timespec="seconds"),
            "statut": "connecte",
        }

        print(
            f"[CLIENT] Connexion : {nom} ({os_name}) "
            f"| ID={client_id} | Adresse={adresse}",
            flush=True,
        )

        return client_id

    def deconnecter(self, client_id):
        """Marque un client comme deconnecte."""
        client = self.clients.get(client_id)

        if client is None:
            return False

        client["statut"] = "deconnecte"
        client["deconnecte_le"] = datetime.now().isoformat(
            timespec="seconds"
        )

        print(
            f"[CLIENT] Deconnexion : {client['nom']} "
            f"| ID={client_id}",
            flush=True,
        )
        return True

    def liste_clients(self, connectes_seulement=False):
        """Retourne la liste des clients connus."""
        clients = list(self.clients.values())

        if connectes_seulement:
            clients = [
                client for client in clients
                if client["statut"] == "connecte"
            ]

        return clients

    def nombre_connectes(self):
        """Compte les clients actuellement connectes."""
        return len(self.liste_clients(connectes_seulement=True))
