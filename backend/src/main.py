from core.page import Page
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from typing import List
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

def load_image(path_file):
    with Image.open(path_file) as img:
        return img.copy()

def process_scan(path_file: str, num: int):
    img = load_image(path_file)
    width, height = img.size

    page = Page(num, img)
    mode = "two" if width > height else "one"

    # Konsumujemy generator, aby wyciągnąć wynik końcowy
    final_result = None
    for step in page.process(mode=mode):
        if step.get("status") == "done":
            final_result = step.get("result")
        elif step.get("status") == "error":
            return {"błąd": step.get("message")}

    return final_result

# Zmiana z async def na def (blokujące operacje I/O w tle)
@app.post("/api/transcribe")
def transcribe(
    files: List[UploadFile] = File(...),
    num_fragments: int = Form(1)
):
    all_results = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

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

    return {
        "status": "success",
        "files_count": len(files),
        "results": all_results
    }