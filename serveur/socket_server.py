
import socket


class SocketServer:
    """Serveur TCP pour le laboratoire VMware."""

    def __init__(self, host="192.168.109.129", port=5001):
        self.host = host
        self.port = port
        self.socket = None

    def demarrer(self):
        """Ouvre le port TCP et attend les connexions."""
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1)

            print(
                f"[SERVEUR] En attente sur "
                f"{self.host}:{self.port}",
                flush=True
            )

        except OSError:
            self.fermer()
            raise

    def accepter_client(self):
        """Accepte une connexion TCP."""
        if self.socket is None:
            raise RuntimeError("Serveur non demarre")

        try:
            return self.socket.accept()

        except socket.timeout:
            return None

    def fermer(self):
        """Libere proprement la socket du serveur."""
        if self.socket is not None:
            try:
                self.socket.close()
            finally:
                self.socket = None

    def __enter__(self):
        self.demarrer()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fermer()
        return False
