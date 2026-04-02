from api import openai_api
from prompts import def_label_prompt

def define_label(img):
    width, height = img.size
    img = img.crop((0, 0, width, int(height * 0.2)))


    try:
        

    except Exception as e:
        print(f"Błąd podczas analizy: {e}")
        return None

