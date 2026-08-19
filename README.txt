=============================================================
  METRICS READER (AVUS) — Transkrypcja metryk kościelnych
=============================================================

Aplikacja webowa do automatycznej transkrypcji XIX-wiecznych metryk
kościelnych (chrztów, ślubów, zgonów) ze skanów do formatu JSON.
Wykorzystuje model Gemini do analizy obrazów i ekstrakcji danych.

-------------------------------------------------------------
WYMAGANIA
-------------------------------------------------------------

- Python 3.9+
- Klucz API do Google Gemini (model: gemini-3-flash-preview)
- Zależności z requirements.txt (patrz: INSTALACJA)

Kluczowe technologie:
  - Backend: FastAPI, Uvicorn, Pillow, google-genai, python-multipart
  - Frontend: React 18+, TypeScript, Vite

Kluczowe biblioteki:
  - google-genai        — klient Gemini API
  - Pillow              — przetwarzanie obrazów
  - python-dotenv       — wczytywanie zmiennych środowiskowych
  - FastAPI             — budowanie wydajnego interfejsu API

-------------------------------------------------------------
INSTALACJA
-------------------------------------------------------------

1. Konfiguracja Backendu (Python):
   a) Przejdź do katalogu projektu i utwórz środowisko wirtualne:
        python -m venv venv
        # Windows:
        .\venv\Scripts\activate
        # Linux/macOS:
        source venv/bin/activate

   b) Zainstaluj wymagane biblioteki:
        pip install -r requirements.txt
      (Upewnij się, że masz: fastapi, uvicorn, python-multipart, pillow, google-genai)

   c) Utwórz plik .env w katalogu głównym:
        GEMINI_API_KEY=twój_klucz_api_tutaj

2. Konfiguracja Frontendu (React):
   a) Przejdź do katalogu frontendu:
        cd frontend
   b) Zainstaluj pakiety npm:
        npm install

-------------------------------------------------------------
URUCHOMIENIE APLIKACJI
-------------------------------------------------------------

Potrzebne są dwa otwarte terminale:

TERMINAL 1 — Serwer Backend (FastAPI):
  uvicorn main:app --reload --port 8000

TERMINAL 2 — Aplikacja Frontend (Vite):
  cd frontend
  npm run dev

Po uruchomieniu otwórz w przeglądarce adres:
  http://localhost:5173

-------------------------------------------------------------
STRUKTURA PROJEKTU
-------------------------------------------------------------

metrics_reader/
├── .env                        # Klucz API (GEMINI_API_KEY)
├── requirements.txt            # Zależności Pythona
├── README.txt                  # Ten plik
├── backend/ (lub src/)
│   ├── main.py                 # Endpointy FastAPI + streaming zdarzeń
│   ├── uploads/                # Katalog tymczasowy na wysyłane skany
│   ├── api/
│   │   └── client.py           # Klient Gemini API
│   ├── core/
│   │   ├── page.py             # Logika cięcia obrazu i generator kroków
│   │   ├── def_label.py        # Ekstrakcja struktury nagłówków tabeli
│   │   └── merge.py            # Scalanie i deduplikacja rekordów
│   └── utils/
│       ├── prompts.py          # Szablony promptów dla Gemini
│       └── translation.py      # Normalizacja kluczy (łacina -> polski)
│
└── frontend/                   # Aplikacja React + TypeScript (Vite)
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── index.css
        └── components/
            ├── Home.tsx        # Ekran wgrywania i podglądu skanów
            ├── Home.css
            ├── Loading.tsx     # Pasek postępu i animacja ładowania
            ├── Loading.css
            ├── Output.tsx      # Prezentacja JSON-a, pobieranie i kopiowanie
            └── Output.css

-------------------------------------------------------------
JAK DZIAŁA PRZETWARZANIE
-------------------------------------------------------------

1. Użytkownik przeciąga pliki graficzne (JPG, PNG) do strefy uploadu.
2. Po kliknięciu „Rozpocznij transkrypcję”, frontend wysyła zapytanie
   POST do endpointu `/api/transcribe` i nasłuchuje strumienia NDJSON.
3. Backend po kolei dla każdego skanu:
   a) Odczytuje proporcje (1 strona vs rozkładówka 2 stron).
   b) Analizuje górne 20% obrazu w celu wykrycia nagłówków tabeli.
   c) Dzieli skan na fragmenty z 20% nakładaniem (overlap).
   d) Odpytuje Gemini dla każdego fragmentu, wysyłając statusy na żywo.
   e) Scala fragmenty, usuwa duplikaty i normalizuje łacińskie nazwy pól.
4. Po osiągnięciu 100% pasek postępu znika, a na ekranie pojawia się
   gotowy wynik w formacie JSON z opcją pobrania na dysk.

-------------------------------------------------------------
JAK DZIAŁA APLIKACJA
-------------------------------------------------------------

1. WCZYTANIE OBRAZU
   Skrypt wczytuje plik JPG/PNG

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