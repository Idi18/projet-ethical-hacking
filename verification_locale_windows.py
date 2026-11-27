
import sys
from pathlib import Path

print("=== VERIFICATION LOCALE WINDOWS ===")
print("Python :", sys.version.split()[0])

# Vérification du registre
try:
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\MonProjetTP"
    ) as key:
        valeur, _ = winreg.QueryValueEx(key, "Status")

    print("Registre Windows :", valeur)
except Exception as e:
    print("Registre Windows : non valide -", e)

# Vérification du module de capture
try:
    from agents.windows.security_audit import take_screenshot
    print("Module de capture : disponible")
except Exception as e:
    print("Module de capture : erreur -", e)

# Vérification des fichiers
for fichier in [
    "agents/windows/main.py",
    "agents/windows/registry.py",
    "agents/windows/security_audit.py",
    "agents/windows/sam_audit.py",
    "agent-windows-v4.spec"
]:
    etat = "PRESENT" if Path(fichier).is_file() else "ABSENT"
    print(f"{fichier} : {etat}")

print("=== VERIFICATION TERMINEE ===")
