
from shared.protocol import MessageType, cmd, make_message


class CommandInterpreter:
    """Prepare et valide les messages de diagnostic."""

    COMMANDES_AUTORISEES = {
        "date": "Afficher la date du client",
        "ordinateur": "Afficher le nom de l'ordinateur",
        "windows": "Afficher les informations Windows",
    }

    def afficher_commandes(self):
        """Affiche les diagnostics disponibles."""
        print("[COMMANDES] Diagnostics autorises :")

        for nom, description in self.COMMANDES_AUTORISEES.items():
            print(f"  {nom} : {description}")

    def preparer_commande(self, nom):
        """Construit un message CMD pour un diagnostic Windows autorise."""
        nom = nom.strip().lower()

        if nom not in self.COMMANDES_AUTORISEES:
            raise ValueError(
                f"Commande non autorisee : {nom}"
            )

        return cmd(nom, [])

    def preparer_ping(self):
        """Construit un message PING."""
        return make_message(MessageType.PING, {})

    def preparer_sysinfo(self):
        """Construit une demande SYSINFO."""
        return make_message(MessageType.SYSINFO, {})

    def preparer_interfaces(self):
        """Construit une demande des interfaces reseau Linux."""
        return make_message("interfaces", {})

    def verifier_reponse(self, message, identifiant_attendu=None):
        """Verifie le format et l'identifiant d'une reponse."""
        if not isinstance(message, dict):
            raise ValueError("La reponse doit etre un dictionnaire")

        if identifiant_attendu is not None:
            if message.get("id") != identifiant_attendu:
                raise ValueError("Identifiant de reponse incorrect")

        type_reponse = message.get("type")

        if type_reponse not in (
            MessageType.RESULT.value,
            MessageType.ERROR.value,
            MessageType.PONG.value,
            MessageType.SYSINFO.value,
        ):
            raise ValueError(
                f"Type de reponse inattendu : {type_reponse}"
            )

        return True

    def afficher_reponse(self, message):
        """Affiche une reponse deja validee."""
        self.verifier_reponse(message)

        type_reponse = message["type"]
        donnees = message.get("data", {})

        print(f"[REPONSE] Type={type_reponse}")
        print(f"[REPONSE] Donnees={donnees}")

        return donnees
