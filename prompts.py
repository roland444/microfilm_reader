
def_label_prompt = """

Przeanalizuj strukturę nagłówków tabeli widocznej na obrazie. Zidentyfikuj wszystkie nagłówki kolumn — zarówno nadrzędne, jak i podrzędne — dokładnie tak, jak są zapisane w dokumencie (zachowaj oryginalną pisownię i język).
Zwróć wyłącznie schemat struktury kolumn w formacie JSON, gdzie:

-każdy nagłówek staje się kluczem,
-kolumny podrzędne są zagnieżdżone jako obiekty wewnątrz klucza nadrzędnego,
-wszystkie wartości końcowe ustawione są na null

Jeśli kolumna posiada podkolumny, przedstaw ją jako obiekt zagnieżdżony; jeśli jest samodzielna — jako klucz z wartością null.

Nie zwracaj żadnych danych z komórek, komentarzy ani znaczników Markdown — wyłącznie czysty JSON.

"""

first_prompt = """Jesteś ekspertem w dziedzinie paleografii i genealogii, specjalizującym się w odczytywaniu XIX-wiecznych metryk kościelnych (łacina, polski, niemiecki).

Twoim zadaniem jest dokładna transkrypcja fragmentu dokumentu z załączonego obrazu.

### ZASADY TRANSKRYPCJI:
1. **Dosłowność**: Przepisz tekst dokładnie tak, jak jest widoczny. Zachowaj oryginalną pisownię nazwisk i miejscowości.
2. **Obsługa cięć (KRYTYCZNE)**: 
   - Jeśli słowo na samej górze lub samym dole obrazu jest ucięte w połowie, zapisz tylko tę część, którą widzisz (np. "Kowal..." lub "...ski"). 
   - Nie zgaduj uciętych końcówek na tym etapie – zajmiesz się tym przy scalaniu całości.
3. **Skróty**: Rozwijaj popularne skróty w nawiasach kwadratowych, jeśli jesteś pewien (np. "fil.[ius]", "ux.[or]").
4. **Niepewność**: Jeśli słowo jest nieczytelne, wstaw [nieczytelne].

### FORMAT WYJŚCIOWY:
Zwróć dane TYLKO w formacie JSON, aby ułatwić późniejsze scalanie.

Zwróć TYLKO czysty kod JSON. Nie dodawaj żadnych wstępów ani komentarzy.

"""

