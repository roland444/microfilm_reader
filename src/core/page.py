from utils.prompts import build_first_prompt
from api.client import gemini_api
from core.def_label import define_label
from core.merge import merge_fragments
from utils.progress import log_step, with_progress_bar, console
import json

class Page:
    overlap_pct = 0.2

    def __init__(self, num, img):
        self.num = num
        self.img = img

    def onePage(self):
        width, height = self.img.size

        structure = self._read_structure()
        if structure is None:
            return "Błąd: nie udało się odczytać struktury nagłówków."

        context_prompt = build_first_prompt(structure)
        fragments = list(self._generate_crops_one(width, height))
        raw_data = self._process_fragments(fragments, context_prompt, label="Strona")

        console.print(f"\n[dim]Zebrano {len(raw_data)} surowych fragmentów.[/dim]")
        return self._merge(raw_data, structure)

    def twoPages(self):
        width, height = self.img.size
        middle = width // 2

        structure = self._read_structure()
        if structure is None:
            return "Błąd: nie udało się odczytać struktury nagłówków."

        context_prompt = build_first_prompt(structure)

        left_crops = list(self._generate_crops_two(width, height, middle, side="lewa"))
        right_crops = list(self._generate_crops_two(width, height, middle, side="prawa"))

        left_raw = self._process_fragments(left_crops,  context_prompt, label="Lewa strona")
        right_raw = self._process_fragments(right_crops, context_prompt, label="Prawa strona")

        merged_left = self._merge(left_raw,  structure)
        merged_right = self._merge(right_raw, structure)
        return {"lewa_strona": merged_left, "prawa_strona": merged_right}

    def _generate_crops_one(self, width, height):
        """Generator zwracający kolejne wycinki obrazu (jedna strona)."""
        base_h   = height / self.num
        overlap  = int(base_h * self.overlap_pct)
        for i in range(self.num):
            y0   = max(0, int(i * base_h) - overlap)
            y1   = min(height, int((i + 1) * base_h) + overlap)
            crop = self.img.crop((0, y0, width, y1))
            yield i, crop

    def _generate_crops_two(self, width, height, middle, side="lewa"):
        """Generator zwracający wycinki lewej lub prawej połowy obrazu."""
        base_h  = height / self.num
        overlap = int(base_h * self.overlap_pct)
        for i in range(self.num):
            y0 = max(0, int(i * base_h) - overlap)
            y1 = min(height, int((i + 1) * base_h) + overlap)
            if side == "lewa":
                crop = self.img.crop((0, y0, middle, y1))
            else:
                crop = self.img.crop((middle, y0, width, y1))
            yield i, crop

    @with_progress_bar(label="Transkrypcja fragmentów", color="magenta")
    def _process_fragments(self, fragments, context_prompt, label="", progress_callback=None):
        """
        Iterator przetwarzający fragmenty obrazu przez API.
        Dekorator @with_progress_bar wstrzykuje progress_callback.
        """
        total = len(fragments)
        all_data = []

        for idx, (i, crop) in enumerate(fragments):
            frag_label = f"{label} — fragment {i + 1}/{total}"

            if progress_callback:
                progress_callback(idx, total, frag_label)

            try:
                response = gemini_api(context_prompt, crop)
                clean_text = response.text.replace('```json', '').replace('```', '').strip()
                parsed = json.loads(clean_text)

                if isinstance(parsed, list):
                    all_data.extend(parsed)
                else:
                    all_data.append(parsed)

            except json.JSONDecodeError as e:
                console.print(f"  [yellow]⚠  Fragment {i+1}: błąd JSON — {e}[/yellow]")
                all_data.append({
                    "fragment": i + 1,
                    "błąd": "nieprawidłowy JSON",
                    "surowa_odpowiedź": response.text
                })
            except Exception as e:
                console.print(f"  [bold red]✗  Fragment {i+1}: {e}[/bold red]")
                raise

        if progress_callback:
            progress_callback(total, total, f"{label} — ukończono")

        return all_data

    @log_step("Analiza nagłówków tabeli", color="blue")
    def _read_structure(self):
        return define_label(self.img)

    @log_step("Scalanie i deduplikacja fragmentów", color="yellow")
    def _merge(self, raw_data, structure):
        return merge_fragments(raw_data, structure)