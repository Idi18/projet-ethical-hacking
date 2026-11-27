
"""
Gestion des erreurs du serveur Kali.
Projet universitaire Ethical Hacking.
"""

import json
import logging
import socket
from pathlib import Path


# Journal des erreurs dans le dossier du serveur
LOG_FILE = Path(__file__).resolve().parent / "server_errors.log"

logger = logging.getLogger("ethical_hacking_server")
logger.setLevel(logging.WARNING)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )
    logger.addHandler(handler)


def classifier_erreur(erreur):
    """Determine la categorie d'une erreur."""

    if isinstance(erreur, socket.timeout):
        return "TIMEOUT"

    if isinstance(erreur, ConnectionError):
        return "CONNECTION_ERROR"

    if isinstance(erreur, json.JSONDecodeError):
        return "INVALID_JSON"

    if isinstance(erreur, (ValueError, TypeError)):
        return "INVALID_MESSAGE"

    if isinstance(erreur, OSError):
        return "NETWORK_ERROR"

    return "INTERNAL_ERROR"


def gerer_erreur(erreur, contexte="serveur"):
    """
    Affiche et journalise une erreur sans enregistrer
    le contenu des messages recus.
    """

    categorie = classifier_erreur(erreur)

    message = (
        f"[ERREUR] Contexte={contexte} "
        f"| Code={categorie}"
    )

    print(message, flush=True)

    logger.warning(
        "Contexte=%s | Code=%s",
        contexte,
        categorie
    )

    return {
        "ok": False,
        "code": categorie,
        "contexte": contexte
    }
