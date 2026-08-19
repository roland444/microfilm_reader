import "./Loading.css";

interface LoadingProps {
  message?: string;
}

export function Loading({
  message = "Przetwarzanie skanów przez AI...",
}: LoadingProps) {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p className="loading-text">{message}</p>
    </div>
  );
}
