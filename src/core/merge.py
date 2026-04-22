from src.api.client import gemini_api
from src.utils.prompts import build_merge_prompt
from src.utils.translation import normalize_keys
import json

def merge_fragments(raw_fragments: list, structure: dict) -> list:
    merge_prompt = build_merge_prompt(structure)
    fragments_json = json.dumps(raw_fragments, ensure_ascii=False, indent=2)
    full_prompt = f"{merge_prompt}\n\n### DANE DO SCALENIA:\n{fragments_json}"

    print("Scalanie fragmentów...")

    try:
        response = gemini_api(full_prompt, "")
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        
        merged = json.loads(clean_text)
        merged = normalize_keys(merged)

        print(f"Scalono pomyślnie — {len(merged)} unikalnych rekordów.")
        
        return merged

    except json.JSONDecodeError as e:
        print(f"Błąd parsowania JSON przy scalaniu: {e}")
        print(f"Surowa odpowiedź: {response.text}")
        
        return normalize_keys(raw_fragments)
    
    except Exception as e:
        print(f"Błąd podczas scalania: {e}")
        
        return raw_fragments