from one_page import one_page
from two_pages import two_pages
from PIL import Image
from google import genai
from dotenv import load_dotenv
import os
import cv2
import io
import json

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def main(path_file, num):
    try:
        with Image.open(path_file) as img:
            width, height = img.size

            if height > width:
                one_page(num, img)
            elif height < width:
                two_pages(num, img)
            else:
                return "Incorrect resolution"
    except ValueError as e:
        return f"Error: {e}"

    final_data = []

    # for i in range(len(y_coords) - 1):
    #     y_start = y_coords[i]
    #     y_end = y_coords[i + 1]

    #     if (y_end - y_start) < 40: continue

    #     print(f"Przetwarzanie wiersza {i+1} (y: {y_start} - {y_end})...")

    #     row_crop = image[y_start:y_end, 0:image.shape[1]]

    #     row_crop_rgb = cv2.cvtColor(row_crop, cv2.COLOR_BGR2RGB)
    #     pil_image = PIL.Image.fromarray(row_crop_rgb)

    #     prompt = """
    #     Rozczytaj metrykę z tego dokumentu. Do każdego słowa rozczytanego, dopisz ocenę pewności swojej transkrypcji od 1 do 10(najwyższa ocena pewności to 10). Wynik powinien wyglądać w następujący sposób:
        
    #     Wymagane pola JSON:
    #     - numer_wpisu (Nr. posit.)
    #     - data_urodzenia_i_chrztu
    #     - imie_dziecka (Nomen)
    #     - dane_rodzicow (Nomen et conditio Parentes)
    #     - chrzestni (Nomen et conditio Patrini)
    #     - uwagi_dodatkowe (jeśli są)
        
    #     Pamiętaj o łacińskich skrótach (np. 'filius' jako fil., 'uxor' jako ux.) i zachowaj oryginalną pisownię nazwisk.
    #     Zwróć tylko czysty obiekt JSON, bez żadnych dodatkowych opisów ani formatowania markdown.
    #     """
    
    #     try:
    #         response = client.models.generate_content(
    #             model="gemini-3-flash-preview", 
    #             contents=[prompt, pil_image]
    #         )
    #         try:
    #             json_respone = json.loads(response.text.replace('```json', '').replace('```', '').strip())
    #             final_data.append(json_respone)
    #         except json.JSONDecodeError:
    #             print(f"Błąd parsowania JSON dla wiersza {i+1}. Surowa odpowiedź: {response.text}")
    #             final_data.append({"error": "Błąd parsowania", "raw": response.text})
    
    #     except Exception as e:
    #         return f"Wystąpił błąd: {e}"
    
    # return final_data


if __name__ == "__main__":
    user_input = input("Ile promptow chcesz zuzyc?: ")
    result_json_list = main("480782_2str_1850.jpg", int(user_input))
    # print("\n--- ZAKOŃCZONO. WYNIKOWE DANE ---")
    # print(json.dumps(result_json_list, indent=2, ensure_ascii=False))

    # # Opcjonalnie: zapis do pliku
    # with open('metryka_dane_02.json', 'w', encoding='utf-8') as f:
    #     json.dump(result_json_list, f, indent=2, ensure_ascii=False)
    # print("Dane zapisano do pliku metryka_dane.json")





