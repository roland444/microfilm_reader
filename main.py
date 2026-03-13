import os
import PIL.Image
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def main(file):
    try:
        img = PIL.Image.open(file)

        prompt = """
        Rozczytaj metrykę z tego dokumentu. Do każdego słowa rozczytanego, dopisz ocenę pewności swojej transkrypcji od 1 do 10(najwyższa ocena pewności to 10) . Wynik powinien wyglądać w następujący sposób:
        {
            "Nr-pozycji-<numer z pierwszej kolumny>": {
                "imie": ["<rozczytaj>", <skala-pewności-transkrypcji>],
                "data-urodzenia": ["<rozczytaj>", <skala-pewności-transkrypcji>],
                "data-chrztu": ["<rozczytaj ", <skala-pewności-transkrypcji>],
                "imie-nazwisko-ojca": ["<rozczytaj>", <skala-pewności-transkrypcji>],
                "imie-nazwisko-matki": ["<rozczytaj>", <skala-pewności-transkrypcji>],
                "imie-nazwisko-ojca-chrzestnego": ["<rozczytaj>", <skala-pewności-transkrypcji>],
                "imie-nazwisko-matki-chrzestnej": ["<rozczytaj>", <skala-pewności-transkrypcji>]
                }
        }
        Zwróć tylko czysty kod JSON.
        """

        response = client.models.generate_content(model="gemini-3-flash-preview", contents=[prompt, img])

        return response.text
    
    except Exception as e:
        return f"Wystąpił błąd: {e}"

wynik = main("metryka jeden wiersz.png")
print(wynik)





