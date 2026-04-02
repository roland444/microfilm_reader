from page import Page
from PIL import Image
import json
import re

def main(path_file, num):
    try:
        with Image.open(path_file) as img:
            width, height = img.size
            if height > width:
                return Page.onePage(num, img)
            elif height < width:
                return Page.twoPages(num, img)
            else:
                return "Incorrect resolution"
    except ValueError as e:
        return f"Error: {e}"
    

if __name__ == "__main__":
    user_scan = "770198 - kopia.jpg"
    user_input = input("Ile promptow chcesz zuzyc?: ")
    result_json_list = main(user_scan, int(user_input))

    match = re.match(r"^[^.]+", user_scan)

    if match:
        match = match.group()

        with open(f'{match}.json', 'w', encoding='utf-8') as f:
            json.dump(result_json_list, f, indent=2, ensure_ascii=False)
        print(f"Dane zapisano do pliku {match}.json")

    





