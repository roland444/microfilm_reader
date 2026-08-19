import "./Loading.css";

interface LoadingProps {
  label: string;
  pct?: number;
}

export function Loading({ label, pct = 0 }: LoadingProps) {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p className="loading-text">{label}</p>

      <div className="progress-bar-track">
        <div
          className="progress-bar-fill"
          style={{ width: `${Math.min(Math.max(pct, 0), 100)}%` }}
        />
      </div>
      <span className="progress-pct">{pct}%</span>
    </div>
  );
}
