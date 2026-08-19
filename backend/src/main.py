from core.page import Page
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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

def load_image(path_file: str):
    with Image.open(path_file) as img:
        return img.copy()

def stream_transcription(files: List[UploadFile], num_fragments: int):
    total_files = len(files)
    all_results = []

    for file_idx, file in enumerate(files):
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Powiadomienie o rozpoczęciu pliku
        yield json.dumps({
            "status": "progress",
            "label": f"[{file_idx + 1}/{total_files}] Wczytywanie: {file.filename}",
            "pct": int((file_idx / total_files) * 100)
        }) + "\n"

        img = load_image(file_path)
        width, height = img.size

        page = Page(num_fragments, img)
        mode = "two" if width > height else "one"

        file_result = None

        # Przekazujemy na żywo każdy krok z Page.process()
        for step in page.process(mode=mode):
            if step.get("status") == "progress":
                # Obliczanie całościowego procentu dla wszystkich plików
                file_base_pct = (file_idx / total_files) * 100
                step_pct = (step.get("pct", 0) / total_files)
                combined_pct = int(file_base_pct + step_pct)

                yield json.dumps({
                    "status": "progress",
                    "label": f"[{file_idx + 1}/{total_files}] {file.filename}: {step.get('label', 'Przetwarzanie...')}",
                    "pct": min(combined_pct, 98)
                }) + "\n"

            elif step.get("status") == "done":
                file_result = step.get("result")
            elif step.get("status") == "error":
                file_result = {"błąd": step.get("message")}

        all_results.append({
            "plik": file.filename,
            "wynik": file_result
        })

    # Ostateczny wynik po zakończeniu wszystkich plików
    yield json.dumps({
        "status": "done",
        "transcription": json.dumps(all_results, indent=2, ensure_ascii=False),
        "pct": 100
    }) + "\n"

@app.post("/api/transcribe")
def transcribe(
    files: List[UploadFile] = File(...),
    num_fragments: int = Form(3)
):
    return StreamingResponse(
        stream_transcription(files, num_fragments),
        media_type="application/x-ndjson"
    )