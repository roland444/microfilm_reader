=============================================================
  METRICS READER (AVUS) — Church Records Transcription
=============================================================

A web application for the automated transcription of 19th-century
church records (baptisms, marriages, deaths) from scans into JSON format.
Powered by the Gemini model for image analysis and data extraction.

-------------------------------------------------------------
REQUIREMENTS
-------------------------------------------------------------

- Python 3.9+
- Google Gemini API Key (model: gemini-3-flash-preview)
- Dependencies from requirements.txt (see: INSTALLATION)

Key Technologies:
  - Backend: FastAPI, Uvicorn, Pillow, google-genai, python-multipart
  - Frontend: React 18+, TypeScript, Vite

Key Libraries:
  - google-genai        — Gemini API client
  - Pillow              — Image processing
  - python-dotenv       — Environment variable loader
  - FastAPI             — Building a high-performance API

-------------------------------------------------------------
INSTALLATION
-------------------------------------------------------------

1. Backend Setup (Python):
   a) Navigate to the project root directory and create a virtual environment:
        python -m venv venv
        # Windows:
        .\venv\Scripts\activate
        # Linux/macOS:
        source venv/bin/activate

   b) Install the required dependencies:
        pip install -r requirements.txt
      (Make sure you have: fastapi, uvicorn, python-multipart, pillow, google-genai)

   c) Create a .env file in the root directory:
        GEMINI_API_KEY=your_api_key_here

2. Frontend Setup (React):
   a) Navigate to the frontend directory:
        cd frontend
   b) Install npm packages:
        npm install

-------------------------------------------------------------
RUNNING THE APPLICATION
-------------------------------------------------------------

You need two separate terminal windows:

TERMINAL 1 — Backend Server (FastAPI):
  uvicorn main:app --reload --port 8000

TERMINAL 2 — Frontend Application (Vite):
  cd frontend
  npm run dev

Once running, open your browser and navigate to:
  http://localhost:5173

-------------------------------------------------------------
PROJECT STRUCTURE
-------------------------------------------------------------

metrics_reader/
├── .env                        # API Key (GEMINI_API_KEY)
├── requirements.txt            # Python dependencies
├── README.txt                  # This file
├── backend/ (or src/)
│   ├── main.py                 # FastAPI endpoints + event streaming
│   ├── uploads/                # Temporary directory for uploaded scans
│   ├── api/
│   │   └── client.py           # Gemini API client
│   ├── core/
│   │   ├── page.py             # Image cropping logic & step generator
│   │   ├── def_label.py        # Table header structure extraction
│   │   └── merge.py            # Record merging and deduplication
│   └── utils/
│       ├── prompts.py          # Gemini prompt templates
│       └── translation.py      # Key normalization (Latin -> Polish)
│
└── frontend/                   # React + TypeScript app (Vite)
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── index.css
        └── components/
            ├── Home.tsx        # Upload & scan preview screen
            ├── Home.css
            ├── Loading.tsx     # Progress bar & loading animation
            ├── Loading.css
            ├── Output.tsx      # JSON display, download & copy
            └── Output.css

-------------------------------------------------------------
HOW THE PROCESSING PIPELINE WORKS
-------------------------------------------------------------

1. The user drops image files (JPG, PNG) into the upload area.
2. Clicking "Start Transcription" sends a POST request from the frontend
   to the `/api/transcribe` endpoint and listens for an NDJSON stream.
3. The backend processes each scan sequentially:
   a) Detects aspect ratio (single page vs. two-page spread).
   b) Analyzes the top 20% of the image to extract table headers.
   c) Splits the scan into horizontal chunks with 20% overlap.
   d) Queries Gemini for each slice, streaming live progress updates.
   e) Merges the chunks, deduplicates entries, and normalizes Latin field names.
4. Upon reaching 100%, the progress bar hides, and the final structured
   JSON is displayed with options to copy or download.

-------------------------------------------------------------
APPLICATION WORKFLOW & INTERNAL LOGIC
-------------------------------------------------------------

1. IMAGE LOADING
   The script loads the JPG/PNG file.

2. ORIENTATION DETECTION
   Based on the aspect ratio, the system distinguishes:
   - Portrait (height > width)  → single page record
   - Landscape (height < width) → two-page spread (left + right page)

3. HEADER ANALYSIS
   The top 20% of the image is analyzed by Gemini to identify
   the table column structure (Latin/Polish/German headers).
   The output is a JSON schema used as a template for transcription.

4. SLICING INTO CHUNKS
   The image is sliced into N horizontal strips with a 20% overlap,
   ensuring no record row gets cut off at the boundary between chunks.

5. TRANSCRIPTION
   Each chunk is sent to Gemini alongside a prompt containing the
   column schema. The model returns data as an array of JSON objects
   (one object = one record row).

6. MERGING & DEDUPLICATION
   Extracted chunks are merged via Gemini: duplicate records are removed,
   split rows are joined, and data is sorted by entry/row number.

7. KEY NORMALIZATION
   Latin keys (e.g., "baptisavit", "nomen", "sepultus") are
   automatically translated to standardized Polish equivalents
   (e.g., "chrzcil", "imie", "data_pochowku").

-------------------------------------------------------------
OUTPUT FORMAT (Example for chrzty.json)
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
SUPPORTED RECORD TYPES
-------------------------------------------------------------

- Baptisms   (data/inputs/chrzty*.jpg)
- Marriages  (data/inputs/sluby*.jpg)
- Deaths     (data/inputs/zgony*.jpg)

The program supports records written in: Latin, Polish, and German.

-------------------------------------------------------------
NOTES & RECOMMENDATIONS
-------------------------------------------------------------

- Transcription accuracy directly depends on scan quality. A minimum
  resolution of 300 DPI is recommended.

- On API errors (timeouts, rate limits), the client automatically
  retries up to 5 times using exponential backoff.

- For very long registers (more than 50 entries per page), it is recommended
  to increase the chunk count so each slice contains no more than ~10 rows.

=============================================================