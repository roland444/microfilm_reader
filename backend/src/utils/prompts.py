def_label_prompt = """

Przeanalizuj strukturę nagłówków tabeli widocznej na obrazie. Zidentyfikuj wszystkie nagłówki kolumn — zarówno nadrzędne, jak i podrzędne — dokładnie tak, jak są zapisane w dokumencie (zachowaj oryginalną pisownię i język).
Zwróć wyłącznie schemat struktury kolumn w formacie JSON, gdzie:

- każdy nagłówek staje się kluczem,
- kolumny podrzędne są zagnieżdżone jako obiekty wewnątrz klucza nadrzędnego,
- wszystkie wartości końcowe ustawione są na null.

Jeśli kolumna posiada podkolumny, przedstaw ją jako obiekt zagnieżdżony; jeśli jest samodzielna — jako klucz z wartością null.

Nie zwracaj żadnych danych z komórek, komentarzy ani znaczników Markdown — wyłącznie czysty JSON.

"""

def build_first_prompt(structure: dict) -> str:
    structure_json = __import__('json').dumps(structure, ensure_ascii=False, indent=2)

    return f"""Jesteś ekspertem w dziedzinie paleografii i genealogii, specjalizującym się w odczytywaniu XIX-wiecznych metryk kościelnych (łacina, polski, niemiecki).

Twoim zadaniem jest dokładna transkrypcja fragmentu dokumentu z załączonego obrazu.

### ZASADY TRANSKRYPCJI:
1. **Dosłowność**: Przepisz tekst dokładnie tak, jak jest widoczny. Zachowaj oryginalną pisownię nazwisk i miejscowości.
2. **Obsługa cięć (KRYTYCZNE)**:
   - Jeśli słowo na samej górze lub samym dole obrazu jest ucięte w połowie, zapisz tylko tę część, którą widzisz (np. "Kowal..." lub "...ski").
   - Nie zgaduj uciętych końcówek na tym etapie – zajmiesz się tym przy scalaniu całości.
3. **Skróty**: Rozwijaj popularne skróty w nawiasach kwadratowych, jeśli jesteś pewien (np. "fil.[ius]", "ux.[or]").
4. **Niepewność**: Jeśli słowo jest nieczytelne, wstaw [nieczytelne].

### ZASADY CZYSZCZENIA TEKSTU (KRYTYCZNE):
- Wartości tekstowe zapisuj jako **ciągły tekst** — bez znaków nowej linii (\\n), bez ukośników (/) używanych tylko jako łamanie wiersza w oryginale.
- Łączniki wyrazowe z podziałem na wiersze (np. "Wołgo-\\nkowski") scalaj w jedno słowo: "Wołgokowski".
- Myślniki znaczące (pauzy, separatory w tekście) zapisuj jako " — ".

### ZASADY PODZIAŁU WIERSZA:
Wiersz w dokumencie, może zawierać inne rodzaje informacji zależnie od typu metryki — rozdziel je na osobne klucze:
- **"obstetrix"** — dane położnej: imię i nazwisko po słowie "Obst.", "Obstet.", "Obstr." itp.
- **"baptisavit"** — dane księdza: imię i nazwisko po słowie "Bapt.", "Baptisavit" itp.
- **"sepelivit"** — dane grabarza: imię i nazwisko po słowie "Sep.", "Sepel.", "Sepelvit" itp.
- **"aspersit"** — dane księdza: imię i nazwisko po słowie "Asp.", "Aspersit" itp.

### UWAGA:
- Kolumna **"nomen"** — wyłącznie imię (i ewentualnie data śmierci, np. "+ 22/9. 882.")



### STRUKTURA DOKUMENTU:
Poniżej znajduje się schemat kolumn tabeli — użyj go jako wzoru do wypełnienia danymi z obrazu.
Każdy wiersz dokumentu = jeden obiekt JSON w tablicy wynikowej.
Zachowaj dokładnie te same klucze co w schemacie.

```json
{structure_json}
```

### FORMAT WYJŚCIOWY:
Zwróć dane TYLKO jako tablicę JSON (array) obiektów — po jednym na każdy wiersz widoczny na fragmencie obrazu.
Nie dodawaj żadnych komentarzy ani znaczników Markdown — wyłącznie czysty JSON.

"""

def build_merge_prompt(structure: dict) -> str:
    structure_json = __import__('json').dumps(structure, ensure_ascii=False, indent=2)

    return f"""Jesteś ekspertem w dziedzinie paleografii i genealogii, specjalizującym się w odczytywaniu XIX-wiecznych metryk kościelnych.

Otrzymujesz tablicę JSON zawierającą fragmenty odczytanej metryki. Fragmenty te powstały przez podział obrazu na zachodzące na siebie części (overlap), przez co:
- niektóre wpisy mogą być zduplikowane (ten sam nr. posit. lub te same dane),
- niektóre wpisy mogą być niekompletne (ucięte na górze lub dole fragmentu, oznaczone "..."),
- mogą istnieć puste lub śmieciowe obiekty (same null lub dane z nagłówka tabeli).

### TWOJE ZADANIE:
1. **Usuń duplikaty** — jeśli ten sam rekord pojawia się wielokrotnie, zostaw tylko jeden, najbardziej kompletny.
2. **Scal fragmenty** — jeśli rekord jest rozbity na dwa fragmenty, połącz je w jeden spójny wpis.
3. **Usuń śmieci** — usuń wpisy puste, z samymi null, lub zawierające tylko nazwy kolumn jako wartości.
4. **Zachowaj oryginalną treść** — nie poprawiaj pisowni, nie tłumacz, nie uzupełniaj domysłami.
5. **Sortuj** — według "Nr. posit." rosnąco.

### ZASADY CZYSZCZENIA TEKSTU (KRYTYCZNE):
- Wszystkie wartości tekstowe jako **ciągły tekst** — bez znaków nowej linii (\\n), bez ukośników (/) będących tylko łamaniem wiersza.
- Łączniki z podziałem na wiersze (np. "Wołgo-kowski") scalaj w jedno słowo: "Wołgokowski".
- Myślniki znaczące zapisuj jako " — ".

### ZASADY PODZIAŁU KLUCZA "NOMEN" / "N O M E N":
Jeśli w danych pojawia się klucz "nomen", "NOMEN" lub "N O M E N"(zwłaszcza w metryce chrztu) zawierający zmieszane informacje, rozdziel go na trzy osobne klucze:
- **"nomen"** — wyłącznie imię (i ewentualnie data śmierci, np. "+ 22/9. 882.")
- **"obstetrix"** — dane położnej po słowie "Obst.", "Obstet.", "Obstr." itp.
- **"baptisavit"** — dane księdza po słowie "Bapt.", "Baptisavit" itp.

### SCHEMAT STRUKTURY WYJŚCIOWEJ:
```json
{structure_json}
```

### FORMAT WYJŚCIOWY:
Zwróć TYLKO czystą tablicę JSON — bez komentarzy, bez znaczników Markdown.

"""
