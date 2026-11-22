
import subprocess


COMMANDES_AUTORISEES = {
    "date": [
        "powershell", "-NoProfile", "-NonInteractive",
        "-Command", "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"
    ],
    "ordinateur": [
        "powershell", "-NoProfile", "-NonInteractive",
        "-Command", "$env:COMPUTERNAME"
    ],
    "windows": [
        "powershell", "-NoProfile", "-NonInteractive",
        "-Command", "[System.Environment]::OSVersion.VersionString"
    ],
}


def executer_diagnostic(nom):
    """
    Execute localement une commande de diagnostic autorisee.
    Aucune commande arbitraire n'est acceptee.
    """
    if nom not in COMMANDES_AUTORISEES:
        return {
            "ok": False,
            "erreur": "Commande non autorisee"
        }

    try:
        resultat = subprocess.run(
            COMMANDES_AUTORISEES[nom],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )

        return {
            "ok": resultat.returncode == 0,
            "sortie": resultat.stdout.strip(),
            "erreur": resultat.stderr.strip(),
            "code_retour": resultat.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "erreur": "Delai d'execution depasse"
        }

    except OSError as exc:
        return {
            "ok": False,
            "erreur": str(exc)
        }


if __name__ == "__main__":
    for nom in COMMANDES_AUTORISEES:
        print(f"[{nom}] {executer_diagnostic(nom)}")
