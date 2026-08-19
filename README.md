[🇵🇱 Wersja polska](README.pl.md) | [🇬🇧 English version](README.md)

---

# Metrics Reader (AVUS) — Church Records Transcription

A web application for the automated transcription of 19th-century church records (baptisms, marriages, deaths) from scanned documents into structured JSON format. Powered by Google Gemini for image analysis and structured data extraction.

---

## Requirements

- Python 3.9+
- Google Gemini API Key (model: gemini-3-flash-preview)
- Dependencies listed in requirements.txt (see Installation)

### Key Technologies

- Backend: FastAPI, Uvicorn, Pillow, google-genai, python-multipart
- Frontend: React 18+, TypeScript, Vite

### Key Libraries

- google-genai — Gemini API client
- Pillow — Image processing
- python-dotenv — Environment variable management
- FastAPI — High-performance backend API

---

## Installation

### 1. Backend Setup (Python)

a) Navigate to the project root directory and create a virtual environment:

python -m venv venv

# Windows:

.\venv\Scripts\activate

# Linux / macOS:

source venv/bin/activate

b) Install required dependencies:

pip install -r requirements.txt

(Ensure you have: fastapi, uvicorn, python-multipart, pillow, google-genai)

c) Create a .env file in the root directory:

GEMINI_API_KEY=your_api_key_here

### 2. Frontend Setup (React)

a) Navigate to the frontend directory:

cd frontend

b) Install npm packages:

npm install

---

## Running the Application

You need two open terminals:

Terminal 1 — Backend Server (FastAPI):
uvicorn main:app --reload --port 8000

Terminal 2 — Frontend Application (Vite):
cd frontend
npm run dev

Once running, open your browser and navigate to:
http://localhost:5173

---

## Project Structure

metrics_reader/
├── .env # API Key (GEMINI_API_KEY)
├── requirements.txt # Python dependencies
├── README.md # English documentation
├── README.pl.md # Polish documentation
├── backend/ (or src/)
│ ├── main.py # FastAPI endpoints + event streaming
│ ├── uploads/ # Temporary directory for uploaded scans
│ ├── api/
│ │ └── client.py # Gemini API client
│ ├── core/
│ │ ├── page.py # Image cropping logic & step generator
│ │ ├── def_label.py # Table header structure extraction
│ │ └── merge.py # Record merging and deduplication
│ └── utils/
│ ├── prompts.py # Gemini prompt templates
│ └── translation.py # Key normalization (Latin -> Polish)
│
└── frontend/ # React + TypeScript app (Vite)
├── package.json
├── vite.config.ts
└── src/
├── App.tsx
├── index.css
└── components/
├── Home.tsx # Upload & scan preview screen
├── Home.css
├── Loading.tsx # Progress bar & loading animation
├── Loading.css
├── Output.tsx # JSON display, download & copy
└── Output.css

---

## Processing Pipeline

1. Upload: The user drags and drops image files (.jpg, .png) into the upload zone.
2. Execution: Clicking "Start Transcription" triggers a POST request to /api/transcribe and starts listening to an NDJSON stream.
3. Backend Processing (per scan):
   - Aspect Ratio Detection: Identifies single page vs. two-page spread.
   - Header Analysis: Scans the top 20% of the image to detect column headers.
   - Horizontal Slicing: Splits the scan into strips with 20% overlap.
   - AI Extraction: Queries Gemini for each slice while streaming live progress.
   - Merging: Merges chunks, eliminates duplicates, and standardizes field names.
4. Completion: When progress reaches 100%, the structured JSON is displayed with options to copy or download.

---

## Application Workflow & Internal Logic

1. Image Loading: Loads the input image file.
2. Orientation Detection:
   - Portrait (height > width) -> Single page record.
   - Landscape (height < width) -> Two-page spread (left + right page).
3. Header Analysis: Top 20% of the image is analyzed by Gemini to extract column layout (Latin / Polish / German headers).
4. Slicing into Chunks: Slices the image into N horizontal strips with a 20% overlap so no rows are lost on boundaries.
5. Transcription: Each chunk is parsed via Gemini with schema constraints, returning an array of JSON objects.
6. Merging & Deduplication: Gemini aggregates slices, resolves overlapping rows, and sorts records by entry number.
7. Key Normalization: Translates Latin keys (e.g., baptisavit, nomen, sepultus) into Polish counterparts (e.g., chrzcil, imie, data_pochowku).

---

## Output Format Example

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

## Supported Record Types & Languages

- Baptisms (data/inputs/chrzty\*.jpg)
- Marriages (data/inputs/sluby\*.jpg)
- Deaths (data/inputs/zgony\*.jpg)

Languages supported: Latin, Polish, German.

---

## Notes & Recommendations

- Scan Quality: Transcription accuracy depends on image clarity. A minimum resolution of 300 DPI is recommended.
- Error Handling: Built-in client retry mechanism with exponential backoff (up to 5 attempts) on rate limits/timeouts.
- Dense Registers: For documents with over 50 entries per page, increasing chunk count (~10 rows per slice) yields best results.
