from utils.prompts import build_first_prompt
from api.client import gemini_api
from core.def_label import define_label
from core.merge import merge_fragments
import json

class Page:
    overlap_pct = 0.2

    def __init__(self, num, img):
        self.num = num
        self.img = img

    def process(self, mode: str = "one"):
        width, height = self.img.size

        yield {"status": "progress", "label": "Przetwarzanie nagłówków", "pct": 0}
        structure = self._read_structure()

        if structure is None:
            yield {"status": "error", "message": "Nie udało się odczytać struktury nagłówków."}
            return

        context_prompt = build_first_prompt(structure)

        if mode == "two":
            middle = width // 2
            columns = [
                {"name": "left_page", "label": "Lewa strona", "x0": 0, "x1": middle, "pct_range": (10, 50)},
                {"name": "right_page", "label": "Prawa strona", "x0": middle, "x1": width, "pct_range": (50, 90)}
            ]
        else:
            columns = [
                {"name": "single_page", "label": "Strona", "x0": 0, "x1": width, "pct_range": (10, 90)}
            ]
        
        result = {}

        for col in columns:
            crops = list(self._generate_crops(height, col["x0"], col["x1"]))
            raw_data = []

            stream = self._process_fragments_stream(
                crops,
                context_prompt,
                label=col["label"],
                pct_start=col["pct_range"][0],
                pct_end=col["pct_range"][1]
            )

            for update in stream:
                if "status" in update and update["status"] == "progress":
                    yield update
                elif "result_data" in update:
                    raw_data = update["result_data"]
            
            result[col["name"]] = self._merge(raw_data, structure)
        
        yield {"status": "progress", "label": "Finalizacja", "pct": 95}

        final_output = result if mode == "two" else result["single_page"]
        yield {"status": "done", "result": final_output, "pct": 100}

    def _generate_crops(self, height, x0, x1):
        base_h  = height / self.num
        overlap = int(base_h * self.overlap_pct)

        for i in range(self.num):
            y0   = max(0, int(i * base_h) - overlap)
            y1   = min(height, int((i + 1) * base_h) + overlap)
            crop = self.img.crop((x0, y0, x1, y1))

            yield i, crop

    def _process_fragments_stream(self, fragments, context_prompt, label="", pct_start=0, pct_end=100):
        total = len(fragments)
        all_data = []

        for idx, (i, crop) in enumerate(fragments):
            current_pct = int(pct_start + ((idx + 1) / total) * (pct_end - pct_start))
            frag_label = f"{label} — fragment {i + 1}/{total}"

            yield {
                "status": "progress",
                "label": frag_label,
                "current": i + 1,
                "total": total,
                "pct": current_pct
            }

            try:
                response = gemini_api(context_prompt, crop)
                clean_text = response.text.replace('```json', '').replace('```', '').strip()
                parsed = json.loads(clean_text)

                if isinstance(parsed, list):
                    all_data.extend(parsed)
                else:
                    all_data.append(parsed)

            except json.JSONDecodeError:
                all_data.append({
                    "fragment": i + 1,
                    "błąd": "nieprawidłowy JSON",
                    "surowa_odpowiedź": getattr(response, "text", "")
                })
            except Exception as e:
                all_data.append({
                    "fragment": i + 1,
                    "błąd": str(e)
                })

        yield {"result_data": all_data}

    def _read_structure(self):
        return define_label(self.img)

    def _merge(self, raw_data, structure):
        return merge_fragments(raw_data, structure)