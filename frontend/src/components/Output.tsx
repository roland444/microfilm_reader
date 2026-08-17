import { useState } from "react";
import "./Output.css";

interface OutputProps {
  data: string | null;
}

export function Output({ data }: OutputProps) {
  const [copied, setCopied] = useState(false);

  if (!data) return null;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(data);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `metryka_transkrypcja_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="output-container">
      <div className="output-header">
        <h3>Wynik transkrypcji</h3>
        <div className="output-actions">
          <button type="button" onClick={handleCopy} className="action-btn">
            {copied ? "Skopiowano!" : "Kopiuj JSON"}
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
      <pre className="output-code">{data}</pre>
    </section>
  );
}
