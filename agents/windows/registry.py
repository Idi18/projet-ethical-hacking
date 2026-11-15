import winreg

def add_registry_key(key_path="Software\\MonProjetTP", value_name="Status", value_data="Actif"):
    """
    Ajoute une clé dans le registre Windows (HKEY_CURRENT_USER).
    Exemple : HKEY_CURRENT_USER\\Software\\MonProjetTP
    """
    try:
        # Ouvre ou crée la clé
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        # Ajoute la valeur
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)
        winreg.CloseKey(key)
        return f"Clé '{key_path}' créée avec succès (Valeur: {value_name}={value_data})"
    except Exception as e:
        return f"Erreur registre : {str(e)}"