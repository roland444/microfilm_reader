from src.core.page import Page
from src.utils.progress import log_step, print_summary, console
from rich.panel import Panel
from PIL import Image
import json
import re


@log_step("Wczytywanie i analiza obrazu", color="cyan")
def load_image(path_file):
    with Image.open(path_file) as img:
        return img.copy()

def main(path_file, num):
    img = load_image(path_file)
    width, height = img.size

    page = Page(num, img)

    if height > width:
        return page.onePage()
    elif height < width:
        return page.twoPages()
    else:
        return "Nieprawidłowa rozdzielczość (kwadrat)"


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold cyan]Microfilm Reader[/bold cyan]\n"
        "[dim]Transkrypcja metryk kościelnych[/dim]",
        border_style="cyan"
    ))

    user_scan  = input("\nPodaj nazwę pliku skanu: ").strip()
    user_input = input("Ile fragmentów (promptów) chcesz użyć?: ").strip()

    result = main(user_scan, int(user_input))

    match = re.match(r"^[^.]+", user_scan)
    if match:
        output_name = match.group()
        output_name = re.sub(r"[\s\-]+", "_", output_name)
        output_path = f"{output_name}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        records = result if isinstance(result, list) else result.get("lewa_strona", [])
        print_summary(records, output_path)
    else:
        console.print("[red]Nie udało się ustalić nazwy pliku wyjściowego.[/red]")
        console.print_json(json.dumps(result, ensure_ascii=False))