=============================================================
  METRICS READER — Transkrypcja metryk kościelnych
=============================================================

Narzędzie do automatycznej transkrypcji XIX-wiecznych metryk
kościelnych (chrztów, ślubów, zgonów) ze skanów do formatu JSON.
Wykorzystuje model Gemini do analizy obrazów i ekstrakcji danych.

-------------------------------------------------------------
WYMAGANIA
-------------------------------------------------------------

- Python 3.9+
- Klucz API do Google Gemini (model: gemini-3-flash-preview)
- Zależności z requirements.txt (patrz: INSTALACJA)

Kluczowe biblioteki:
  - google-genai        — klient Gemini API
  - Pillow              — przetwarzanie obrazów
  - rich                — interfejs CLI (kolory, paski postępu)
  - python-dotenv       — wczytywanie zmiennych środowiskowych

-------------------------------------------------------------
INSTALACJA
-------------------------------------------------------------

1. Sklonuj lub rozpakuj projekt.

2. Przejdź do katalogu projektu:
     cd metrics_reader

3. Zainstaluj zależności:
     pip install -r requirements.txt

4. Uzupełnij plik .env, wpisując swój klucz API:
     GEMINI_API_KEY=twój_klucz_api_tutaj

-------------------------------------------------------------
STRUKTURA PROJEKTU
-------------------------------------------------------------

metrics_reader/
├── .env                        # Klucz API
├── requirements.txt            # Lista zależności Pythona
├── README.txt                  # Ten plik
├── data/
│   ├── inputs/                 # Skany metryk (pliki JPG/PNG)
│   └── outputs/                # Wyniki transkrypcji (pliki JSON)
└── src/
    ├── main.py                 # Punkt wejścia aplikacji
    ├── api/
    │   └── client.py           # Klient Gemini API
    ├── core/
    │   ├── page.py             # Logika podziału i przetwarzania strony
    │   ├── def_label.py        # Wykrywanie struktury nagłówków tabeli
    │   └── merge.py            # Scalanie i deduplikacja fragmentów
    └── utils/
        ├── prompts.py          # Prompty dla modelu Gemini
        ├── translation.py      # Normalizacja kluczy (łacina → polski)
        └── progress.py         # Dekoratory logowania i pasków postępu

-------------------------------------------------------------
UŻYCIE
-------------------------------------------------------------

Uruchom skrypt z poziomu katalogu src/:

  cd src
  python main.py

Program zapyta o:
  1. Nazwę pliku skanu (np. chrzty.jpg)
     — plik musi znajdować się w katalogu data/inputs/
  2. Liczbę fragmentów (promptów), na które podzielić skan
     — zalecane: 3–6 dla jednej strony, 4–8 dla dwóch stron

Wynik zostanie zapisany w data/outputs/<nazwa_pliku>.json

-------------------------------------------------------------
JAK DZIAŁA APLIKACJA
-------------------------------------------------------------

1. WCZYTANIE OBRAZU
   Skrypt wczytuje plik JPG/PNG z data/inputs/.

2. WYKRYCIE ORIENTACJI
   Na podstawie proporcji obrazu program rozróżnia:
   - pion (height > width)  → jedna strona metryki
   - poziom (height < width) → dwie strony metryki (lewa + prawa)

3. ANALIZA NAGŁÓWKA
   Górne 20% obrazu jest analizowane przez Gemini w celu wykrycia
   struktury kolumn tabeli (nagłówki łacińskie/polskie/niemieckie).
   Wynik to schemat JSON używany jako wzorzec do transkrypcji.

4. PODZIAŁ NA FRAGMENTY
   Obraz jest dzielony na N poziomych pasków z 20% nakładaniem
   (overlap), aby żaden wpis nie został ucięty między fragmentami.

5. TRANSKRYPCJA
   Każdy fragment jest wysyłany do Gemini wraz z promptem
   zawierającym schemat kolumn. Model zwraca dane jako tablicę
   obiektów JSON (jeden obiekt = jeden wiersz metryki).

6. SCALANIE
   Zebrane fragmenty są scalane przez Gemini: duplikaty są usuwane,
   urwane wpisy łączone, dane sortowane po numerze pozycji.

7. NORMALIZACJA KLUCZY
   Klucze łacińskie (np. "baptisavit", "nomen", "sepultus") są
   automatycznie tłumaczone na polskie odpowiedniki
   (np. "chrzcil", "imie", "data_pochowku").

8. ZAPIS WYNIKU
   Gotowy JSON jest zapisywany do data/outputs/<nazwa>.json.

-------------------------------------------------------------
FORMAT WYJŚCIOWY (przykład dla chrzty.json)
-------------------------------------------------------------

[
  {
    "nr_pozycji": "1",
    "miesiac": "Januarii",
    "data_urodzenia": "3",
    "data_chrztu": "5",
    "imie": "Joannes",
    "plec": "puer",
    "slubnosc": "legitimi",
    "rodzice": "Stanislai Kowalski et Mariae",
    "nr_domu": "12",
    "chrzestni": "Thomas Nowak, Anna Wiśniewska",
    "polozna": "Catharina Zielinska",
    "chrzcil": "Joannes Malinowski"
  },
  ...
]

Dla skanów dwustronnych wynik ma postać:
  { "lewa_strona": [...], "prawa_strona": [...] }

-------------------------------------------------------------
OBSŁUGIWANE TYPY METRYK
-------------------------------------------------------------

- Chrzty    (data/inputs/chrzty*.jpg)
- Śluby     (data/inputs/sluby*.jpg)
- Zgony     (data/inputs/zgony*.jpg)

Program obsługuje metryki w językach: łacina, polski, niemiecki.

-------------------------------------------------------------
UWAGI
-------------------------------------------------------------

- Jakość transkrypcji zależy od jakości skanu. Zalecana rozdzielczość
  to minimum 300 DPI.

- Przy błędach API (timeout, limit zapytań) klient automatycznie
  ponawia próbę do 5 razy z rosnącym opóźnieniem (backoff).

- Dla bardzo długich metryk (powyżej 50 wpisów) zaleca się zwiększenie
  liczby fragmentów, aby każdy fragment nie przekraczał ~10 wierszy.

=============================================================