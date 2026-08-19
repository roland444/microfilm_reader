[🇵🇱 Wersja polska](README.pl.md) | [🇬🇧 English version](README.md)

---

# Metrics Reader (AVUS) — Transkrypcja metryk kościelnych

Aplikacja webowa do automatycznej transkrypcji XIX-wiecznych metryk kościelnych (chrztów, ślubów, zgonów) ze skanów do ustrukturyzowanego formatu JSON. Wykorzystuje model Google Gemini do analizy obrazu i ekstrakcji danych.

---

## Wymagania

- Python 3.9+
- Klucz API do Google Gemini (model: gemini-3-flash-preview)
- Zależności z requirements.txt (patrz: Instalacja)

### Kluczowe technologie

- Backend: FastAPI, Uvicorn, Pillow, google-genai, python-multipart
- Frontend: React 18+, TypeScript, Vite

### Kluczowe biblioteki

- google-genai — klient Gemini API
- Pillow — przetwarzanie obrazów
- python-dotenv — wczytywanie zmiennych środowiskowych
- FastAPI — budowanie wydajnego interfejsu API

---

## Instalacja

### 1. Konfiguracja Backendu (Python)

a) Przejdź do katalogu projektu i utwórz środowisko wirtualne:

python -m venv venv

# Windows:

.\venv\Scripts\activate

# Linux / macOS:

source venv/bin/activate

b) Zainstaluj wymagane biblioteki:

pip install -r requirements.txt

(Upewnij się, że zainstalowano: fastapi, uvicorn, python-multipart, pillow, google-genai)

c) Utwórz plik .env w katalogu głównym:

GEMINI_API_KEY=twój_klucz_api_tutaj

### 2. Konfiguracja Frontendu (React)

a) Przejdź do katalogu frontendu:

cd frontend

b) Zainstaluj pakiety npm:

npm install

---

## Uruchomienie aplikacji

Wymagane są dwa otwarte terminale:

Terminal 1 — Serwer Backend (FastAPI):
uvicorn main:app --reload --port 8000

Terminal 2 — Aplikacja Frontend (Vite):
cd frontend
npm run dev

Po uruchomieniu otwórz w przeglądarce adres:
http://localhost:5173

---

## Struktura projektu

metrics_reader/
├── .env # Klucz API (GEMINI_API_KEY)
├── requirements.txt # Zależności Pythona
├── README.md # Dokumentacja w j. angielskim
├── README.pl.md # Dokumentacja w j. polskim
├── backend/ (lub src/)
│ ├── main.py # Endpointy FastAPI + streaming zdarzeń
│ ├── uploads/ # Katalog tymczasowy na wysyłane skany
│ ├── api/
│ │ └── client.py # Klient Gemini API
│ ├── core/
│ │ ├── page.py # Logika cięcia obrazu i generator kroków
│ │ ├── def_label.py # Ekstrakcja struktury nagłówków tabeli
│ │ └── merge.py # Scalanie i deduplikacja rekordów
│ └── utils/
│ ├── prompts.py # Szablony promptów dla Gemini
│ └── translation.py # Normalizacja kluczy (łacina -> polski)
│
└── frontend/ # Aplikacja React + TypeScript (Vite)
├── package.json
├── vite.config.ts
└── src/
├── App.tsx
├── index.css
└── components/
├── Home.tsx # Ekran wgrywania i podglądu skanów
├── Home.css
├── Loading.tsx # Pasek postępu i animacja ładowania
├── Loading.css
├── Output.tsx # Prezentacja JSON-a, pobieranie i kopiowanie
└── Output.css

---

## Jak działa przetwarzanie

1. Wgrywanie: Użytkownik przeciąga pliki graficzne (.jpg, .png) do strefy uploadu.
2. Start: Kliknięcie „Rozpocznij transkrypcję” wysyła żądanie POST do /api/transcribe i nasłuchuje strumienia NDJSON.
3. Przetwarzanie Backendowe:
   - Wykrycie proporcji: Rozpoznaje 1 stronę lub rozkładówkę 2 stron.
   - Analiza nagłówków: Analizuje górne 20% skanu, aby wykryć strukturę kolumn.
   - Cięcie na paski: Dzieli obraz na fragmenty z 20% nakładaniem (overlap).
   - Ekstrakcja AI: Odpytuje Gemini dla każdego fragmentu i przesyła status na żywo.
   - Scalanie: Łączy fragmenty, eliminuje duplikaty i normalizuje nazwy pól.
4. Finał: Po osiągnięciu 100% pasek postępu znika, a wynik w formacie JSON jest gotowy do skopiowania lub pobrania.

---

## Logika działania aplikacji

1. Wczytanie obrazu: Skrypt wczytuje plik graficzny.
2. Wykrycie orientacji:
   - Pion (height > width) -> Pojedyncza strona metryki.
   - Poziom (height < width) -> Dwie strony metryki (lewa + prawa).
3. Analiza nagłówka: Górne 20% obrazu jest analizowane przez Gemini w celu wykrycia nagłówków tabeli (łacina, polski, niemiecki).
4. Podział na fragmenty: Obraz dzielony jest na N poziomych pasków z 20% nakładaniem, co zapobiega ucięciu wierszy na łączeniach.
5. Transkrypcja: Każdy fragment jest wysyłany do Gemini wraz ze schematem kolumn, zwracając tablicę obiektów JSON.
6. Scalanie i deduplikacja: Gemini scala fragmenty, usuwa zduplikowane wpisy i sortuje dane według numeru pozycji.
7. Normalizacja kluczy: Łacińskie nazwy pól (np. baptisavit, nomen, sepultus) są automatycznie mapowane na język polski (np. chrzcil, imie, data_pochowku).

---

## Przykładowy format wyjściowy

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
}
]

---

## Obsługiwane typy metryk i języki

- Chrzty (data/inputs/chrzty\*.jpg)
- Śluby (data/inputs/sluby\*.jpg)
- Zgony (data/inputs/zgony\*.jpg)

Obsługiwane języki dokumentów: łacina, polski, niemiecki.

---

## Uwagi

- Jakość skanu: Dokładność zależy od czytelności materiału źródłowego (zalecane min. 300 DPI).
- Obsługa błędów: W przypadku limitów zapytań klient ponawia próbę do 5 razy z rosnącym czasem oczekiwania (exponential backoff).
- Gęste metryki: Przy ponad 50 wpisach na stronę warto zwiększyć liczbę pasków, aby na jeden fragment przypadało do ~10 wierszy.
