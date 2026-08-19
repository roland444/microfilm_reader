import { type ChangeEvent, type DragEvent, useState } from "react";
import "./Home.css";
import { Loading } from "./Loading";
import { Output } from "./Output";

interface PreviewItem {
  id: string;
  file: File;
  url: string;
}

interface TranscriptionResponse {
  status: string;
  files_count: number;
  transcription: string;
}

export function Home() {
  const [previews, setPreviews] = useState<PreviewItem[]>([]);
  const [transcription, setTranscription] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const processFiles = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;

    // Filtrujemy tylko pliki graficzne (PIL nie obsługuje PDF bezpośrednio)
    const validFiles = Array.from(fileList).filter((f) =>
      f.type.startsWith("image/"),
    );

    if (validFiles.length === 0) {
      setError("Proszę wybrać pliki graficzne (JPG, PNG, TIFF, WEBP).");
      return;
    }

    const newItems: PreviewItem[] = validFiles.map((file) => ({
      id: `${file.name}-${file.lastModified}-${Math.random()}`,
      file,
      url: URL.createObjectURL(file),
    }));

    setPreviews((prev) => [...prev, ...newItems]);
    setTranscription(null);
    setError(null);
  };

  const handleFilesChange = (event: ChangeEvent<HTMLInputElement>) => {
    processFiles(event.target.files);
    event.target.value = "";
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);

    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      processFiles(event.dataTransfer.files);
    }
  };

  const handleRemoveFile = (idToRemove: string) => {
    setPreviews((prev) => {
      const itemToRemove = prev.find((item) => item.id === idToRemove);
      if (itemToRemove) {
        URL.revokeObjectURL(itemToRemove.url);
      }
      return prev.filter((item) => item.id !== idToRemove);
    });
  };

  const handleUpload = async () => {
    if (previews.length === 0) return;

    setIsLoading(true);
    setError(null);
    setTranscription(null);

    const formData = new FormData();
    previews.forEach((item) => {
      formData.append("files", item.file);
    });
    // Domyślna liczba fragmentów
    formData.append("num_fragments", "3");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/transcribe", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Błąd serwera: ${response.status}`);
      }

      const data = await response.json();
      console.log("4. Dane JSON z backendu:", data);

      // Ta linijka zawsze wyciągnie dane, niezależnie jak backend je nazwał:
      const rawResult = data.transcription || data.results || data;
      setTranscription(
        typeof rawResult === "string"
          ? rawResult
          : JSON.stringify(rawResult, null, 2),
      );
    } catch (err: any) {
      setError(err.message || "Wystąpił błąd podczas wysyłania plików.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Microfilm Reader</h1>
      <h2>Transkrypcja metryk kościelnych</h2>

      <div className="input-area">
        <div
          className={`upload-box ${isDragging ? "dragging" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById("file-upload")?.click()}
        >
          <input
            id="file-upload"
            type="file"
            multiple
            accept="image/*"
            onChange={handleFilesChange}
          />
          <p>
            {isDragging
              ? "Upuść skany tutaj..."
              : "Kliknij lub przeciągnij skany metryk (JPG, PNG)"}
          </p>
        </div>

        {previews.length > 0 && (
          <div className="preview-section">
            <h3>Podgląd skanów ({previews.length}):</h3>
            <div className="preview-grid">
              {previews.map((item) => (
                <div key={item.id} className="preview-card">
                  <img
                    src={item.url}
                    alt={item.file.name}
                    className="image-preview"
                  />
                  <button
                    type="button"
                    className="delete-badge"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveFile(item.id);
                    }}
                    title="Usuń ten skan"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={previews.length === 0 || isLoading}
          className="submit-btn"
        >
          {isLoading
            ? `Przetwarzanie (${previews.length} skanów)...`
            : `Rozpocznij transkrypcję (${previews.length})`}
        </button>

        {isLoading && (
          <Loading
            message={`Analizowanie ${previews.length} skanów przez Gemini AI...`}
          />
        )}

        {error && <div className="error-box">{error}</div>}

        <Output data={transcription} />
      </div>
    </div>
  );
}
