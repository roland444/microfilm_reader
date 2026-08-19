import "./App.css";
import { Home } from "./components/Home";

const MOCK_DATA = JSON.stringify(
  [
    {
      plik: "metryka_urodzenia_1892.jpg",
      wynik: {
        rok: 1892,
        akt_nr: 45,
        imie: "Jan",
        nazwisko: "Kowalski",
        parafia: "Św. Wojciecha",
      },
    },
  ],
  null,
  2,
);

export default function App() {
  return (
    <main>
      <Home />
    </main>
  );
}
