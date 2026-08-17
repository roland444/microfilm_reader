from core.page import Page
from utils.progress import log_step
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from typing import List
import json
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@log_step("Wczytywanie i analiza obrazu", color="cyan")
def load_image(path_file):
    with Image.open(path_file) as img:
        return img.copy()

def process_scan(path_file: str, num: int):
    """Główna logika przeniesiona z dawnej funkcji main()"""
    img = load_image(path_file)
    width, height = img.size

    page = Page(num, img)

    if height > width:
        return page.onePage()
    elif height < width:
        return page.twoPages()
    else:
        return {"error": "Nieprawidłowa rozdzielczość (kwadrat)"}

@app.post("/api/transcribe")
async def transcribe(
    files: List[UploadFile] = File(...),
    num_fragments: int = Form(1) # Domyślna liczba promptów, jeśli frontend jej nie przekaże
):
    all_results = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # 1. Zapis pliku na dysku
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Przetworzenie pliku przez klasę Page
        try:
            result = process_scan(file_path, num_fragments)
            all_results.append({
                "plik": file.filename,
                "wynik": result
            })
        except Exception as e:
            all_results.append({
                "plik": file.filename,
                "błąd": str(e)
            })

    # 3. Zwrócenie zbiorczego wyniku w formacie oczekiwanym przez Reacta
    return {
        "status": "success",
        "files_count": len(files),
        # Zamieniamy słownik na ładnie sformatowany tekst JSON, 
        # by React mógł go wyświetlić w tagu <pre>
        "transcription": json.dumps(all_results, indent=2, ensure_ascii=False)
    }