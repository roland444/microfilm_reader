from page import Page
from PIL import Image
import json
import re

def main(path_file, num):
    try:
        with Image.open(path_file) as img:
            img_copy = img.copy()
            width, height = img_copy.size

            page = Page(num, img_copy)

            if height > width:
                return page.onePage()
            elif height < width:
                return page.twoPages()
            else:
                return "Nieprawidłowa rozdzielczość (kwadrat)"

    except FileNotFoundError:
        return f"Błąd: nie znaleziono pliku '{path_file}'"
    except Exception as e:
        return f"Błąd: {e}"


if __name__ == "__main__":
    # user_scan = input("Podaj nazwę pliku skanu: ").strip()
    user_scan = "770198-kopia.jpg"
    user_input = input("Ile fragmentów (promptów) chcesz użyć?: ").strip()

    result = main(user_scan, int(user_input))

    match = re.match(r"^[^.]+", user_scan)
    if match:
        output_name = match.group()
        output_path = f"{output_name}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Dane zapisano do pliku: {output_path}")
    else:
        print("Nie udało się ustalić nazwy pliku wyjściowego.")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    





