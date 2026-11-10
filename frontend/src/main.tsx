import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

type Health = { status: string; db: boolean };
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function App() {
  const [health, setHealth] = useState<Health | null>(null);
  useEffect(() => {
    fetch(`${apiBaseUrl}/health`)
      .then((response) => response.json() as Promise<Health>)
      .then(setHealth)
      .catch(() => setHealth({ status: "unavailable", db: false }));
  }, []);

  return (
    <main className="shell">
      <aside><div className="brand">ROOTWISE</div><nav><span className="active">Console</span><span>Incidents</span><span>Evidence</span></nav></aside>
      <section className="workspace">
        <header><span>Incident intelligence console</span><span className="environment">ENV: LOCAL</span></header>
        <div className="content"><h1>Awaiting incident evidence</h1><p>The workspace is ready for the first incident run.</p></div>
        <footer><span className={health?.status === "ok" ? "dot online" : "dot"} /> API {health?.status === "ok" ? "online" : "offline"} · Database {health?.db ? "connected" : "unavailable"}</footer>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
