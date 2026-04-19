from api import gemini_api
from prompts import def_label_prompt
import json

def define_label(img):
    width, height = img.size
    header_crop = img.crop((0, 0, width, int(height * 0.2)))

    try:
        response = gemini_api(def_label_prompt, header_crop)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        structure = json.loads(clean_text)
        
        return structure

    except json.JSONDecodeError as e:
        print(f"Błąd parsowania JSON: {e}")
        return None
    
    except Exception as e:
        print(f"Błąd podczas analizy: {e}")
        return None

