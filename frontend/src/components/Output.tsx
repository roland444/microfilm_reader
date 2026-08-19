import { useState } from "react";
import "./Output.css";

interface OutputProps {
  data: string | null;
}

export function Output({ data }: OutputProps) {
  const [copied, setCopied] = useState(false);

  if (!data) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(data);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Błąd kopiowania:", err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transkrypcja_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="output-container">
      <div className="output-header">
        <h3>Wynik transkrypcji (JSON)</h3>
        <div className="output-actions">
          <button type="button" onClick={handleCopy} className="action-btn">
            {copied ? "✓ Skopiowano" : "Kopiuj"}
          </button>
          <button
            type="button"
            onClick={handleDownload}
            className="action-btn download-btn"
          >
            Pobierz .json
          </button>
        </div>
      </div>

      <pre className="output-code">
        <code>{data}</code>
      </pre>
    </div>
  );
}
