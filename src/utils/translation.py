import json
import re

KEY_TRANSLATIONS = {
    # Daty i numery
    "nrposit"           : "nr_pozycji",
    "nrusposit"         : "nr_pozycji",
    "nrusserialis"      : "nr_pozycji",
    "numeruspositionis" : "nr_pozycji",
    "numerusdomus"      : "nr_domu",
    "nrusdomus"         : "nr_domu",
    "mensis"            : "miesiac",
    "nat"               : "data_urodzenia",
    "natus"             : "data_urodzenia",
    "bap"               : "data_chrztu",
    "bapt"              : "data_chrztu",
    "baptisat"          : "data_chrztu",
    "mortuus"           : "data_smierci",
    "sepultus"          : "data_pochowku",
    "dies"              : "dzien",
    "annus"             : "rok",
 
    # Dane osobowe
    "nomen"             : "imie",
    "nomenmortui"       : "imie",
    "nomeninfantis"     : "imie",
    "nomenetcognomine"  : "imie_i_nazwisko",
    "obstetrix"         : "polozna",
    "baptisavit"        : "chrzcil",
    "copulavit"         : "slub_udzielil",
    "celebravit"        : "celebrowal",
 
    # Religia i płeć
    "religiocatholica"  : "religia_katolicka",
    "religio"           : "religia",
    "catholica"         : "katolicka",
    "autalia"           : "inne_wyznanie",
    "sexus"             : "plec",
    "puer"              : "chlopiec",
    "puella"            : "dziewczynka",
    "masc"              : "mezczyzna",
    "masculus"          : "mezczyzna",
    "vir"               : "mezczyzna",
    "femina"            : "kobieta",
    "foemina"           : "kobieta",
    "uxor"              : "zona",
 
    # Ślubność
    "thori"             : "slubnosc",
    "coelebs"           : "kawaler",
    "viduus"            : "wdowiec",
    "legitimi"          : "slubny",
    "illegitimi"        : "nieslubny",
 
    # Rodzice i chrzestni
    "parentes"          : "rodzice",
    "patris"            : "ojciec",
    "matris"            : "matka",
    "patrini"           : "chrzestni",
    "nomenetconditio"   : "imie_i_stan",
 
    # Małżeństwo (śluby)
    "sponsus"           : "oblubieniec",
    "sponsa"            : "oblubienica",
    "testes"            : "swiadkowie",
    "testis"            : "swiadek",
    "locus"             : "miejsce",
    "parochia"          : "parafia",
    "pagus"             : "wies",
 
    # Zgony
    "morbus"            : "przyczyna",
    "defunctus"         : "zmarly",
    "defuncti"          : "zmarlego",
    "diesvitae"         : "wiek",
    "aetas"             : "wiek",
    "morbusetqualitasmortis"      : "przyczyna_smierci",
    "causamortis"       : "przyczyna_smierci",
    "minister"          : "duchowny",
}

def _normalize_key(key: str) -> str:
    key = key.replace(".", "")
    key = re.sub(r'(?<!\w)((\w)\s)+(\w)(?!\w)', lambda m: re.sub(r'\s', '', m.group(0)), key)
    key = re.sub(r'\s+', ' ', key).strip().lower()
 
    return key

def _translate_key(key: str) -> str:
    normalized = _normalize_key(key)

    if normalized in KEY_TRANSLATIONS:
        return KEY_TRANSLATIONS[normalized]
 
    compressed = re.sub(r'[\s\.\-_]', '', normalized)
    if compressed in KEY_TRANSLATIONS:
        return KEY_TRANSLATIONS[compressed]
 
    for pattern, translation in KEY_TRANSLATIONS.items():
        if pattern in normalized or pattern in compressed:
            return translation
 
    return normalized
 
 
def normalize_keys(obj):
    if isinstance(obj, dict):
        return {
            _translate_key(k): normalize_keys(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [normalize_keys(item) for item in obj]
    else:
        return obj
 
 
def normalize_json_file(input_path: str, output_path: str = None) -> list:
    if output_path is None:
        output_path = input_path
 
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
 
    normalized = normalize_keys(data)
 
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False)
 
    return normalized
