from prompts import build_first_prompt
from api import gemini_api
from def_label import define_label
import json

class Page:
    overlap_pct = 0.2

    def __init__(self, num, img):
        self.num = num
        self.img = img

    def onePage(self):
        width, height = self.img.size

        structure = define_label(self.img)
        if structure is None:
            return "Błąd: nie udało się odczytać struktury nagłówków."

        context_prompt = build_first_prompt(structure)

        base_part_height = height / self.num
        overlap_px = int(base_part_height * self.overlap_pct)

        final_data = []

        for i in range(self.num):
            y0 = max(0, int(i * base_part_height) - overlap_px)
            y1 = min(height, int((i + 1) * base_part_height) + overlap_px)

            crop = self.img.crop((0, y0, width, y1))

            try:
                response = gemini_api(context_prompt, crop)
                clean_text = response.text.replace('```json', '').replace('```', '').strip()
                json_response = json.loads(clean_text)

                # Obsługa zarówno pojedynczego obiektu jak i tablicy wierszy
                if isinstance(json_response, list):
                    final_data.extend(json_response)
                else:
                    final_data.append(json_response)

            except json.JSONDecodeError as e:
                print(f"Błąd parsowania JSON we fragmencie {i+1}: {e}")
                final_data.append({"fragment": i + 1, "błąd": "nieprawidłowy JSON", "surowa_odpowiedź": response.text})
            except Exception as e:
                return f"Wystąpił błąd we fragmencie {i+1}: {e}"

        return final_data

    def twoPages(self):
        width, height = self.img.size
        middle = width // 2

        structure = define_label(self.img)
        if structure is None:
            return "Błąd: nie udało się odczytać struktury nagłówków."

        context_prompt = build_first_prompt(structure)

        base_part_height = height / self.num
        overlap_px = int(base_part_height * self.overlap_pct)

        left_data = []
        right_data = []

        for i in range(self.num):
            y0 = max(0, int(i * base_part_height) - overlap_px)
            y1 = min(height, int((i + 1) * base_part_height) + overlap_px)

            left_crop = self.img.crop((0, y0, middle, y1))
            right_crop = self.img.crop((middle, y0, width, y1))

            print(f"Przetwarzanie fragment {i+1}/{self.num}...")

            try:
                # Lewa strona
                resp_left = gemini_api(context_prompt, left_crop)
                clean_left = resp_left.text.replace('```json', '').replace('```', '').strip()
                json_left = json.loads(clean_left)
                if isinstance(json_left, list):
                    left_data.extend(json_left)
                else:
                    left_data.append(json_left)

                # Prawa strona
                resp_right = gemini_api(context_prompt, right_crop)
                clean_right = resp_right.text.replace('```json', '').replace('```', '').strip()
                json_right = json.loads(clean_right)
                if isinstance(json_right, list):
                    right_data.extend(json_right)
                else:
                    right_data.append(json_right)

            except json.JSONDecodeError as e:
                print(f"Błąd parsowania JSON we fragmencie {i+1}: {e}")
            except Exception as e:
                return f"Wystąpił błąd we fragmencie {i+1}: {e}"

        return {"lewa_strona": left_data, "prawa_strona": right_data}
