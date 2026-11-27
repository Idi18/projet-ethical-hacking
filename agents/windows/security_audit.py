import base64
import io
from PIL import ImageGrab

def take_screenshot():
    """
    Prend une capture d'écran et la renvoie encodée en base64.
    """
    try:
        # Prend la capture d'écran
        screenshot = ImageGrab.grab()
        
        # Sauvegarde dans un buffer mémoire (pas sur le disque)
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        
        # Encode en base64 pour l'envoyer en texte dans le JSON
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {"status": "success", "image_base64": img_base64}
    except Exception as e:
        return {"status": "error", "message": str(e)}