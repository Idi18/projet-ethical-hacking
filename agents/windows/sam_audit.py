import subprocess
import os
import tempfile

def audit_sam():
    """
    Fait un audit de la base SAM (récupération de la structure).
    """
    try:
        temp_dir = tempfile.gettempdir()
        sam_path = os.path.join(temp_dir, "sam_audit.hiv")
        system_path = os.path.join(temp_dir, "system_audit.hiv")
        
        # Ajout de errors='ignore' pour éviter le crash Unicode
        cmd_sam = f'reg save HKLM\\SAM "{sam_path}" /y'
        res_sam = subprocess.run(cmd_sam, shell=True, capture_output=True, text=True, errors='ignore')
        
        cmd_sys = f'reg save HKLM\\SYSTEM "{system_path}" /y'
        res_sys = subprocess.run(cmd_sys, shell=True, capture_output=True, text=True, errors='ignore')
        
        output = "=== AUDIT SAM & SYSTEM ===\n"
        if res_sam.returncode == 0:
            output += f"[OK] SAM sauvegardé dans {sam_path}\n"
        else:
            output += f"[ERREUR SAM] {res_sam.stderr}\n"
            
        if res_sys.returncode == 0:
            output += f"[OK] SYSTEM sauvegardé dans {system_path}\n"
        else:
            output += f"[ERREUR SYSTEM] {res_sys.stderr}\n"
            
        if os.path.exists(sam_path): os.remove(sam_path)
        if os.path.exists(system_path): os.remove(system_path)
        
        output += "[INFO] Fichiers temporaires nettoyés."
        return output
    except Exception as e:
        return f"Erreur lors de l'audit SAM : {str(e)}"