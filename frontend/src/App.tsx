import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type ApiStatus = "checking" | "online" | "offline";

export default function App() {
  const [status, setStatus] = useState<ApiStatus>("checking");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => (res.ok ? setStatus("online") : setStatus("offline")))
      .catch(() => setStatus("offline"));
  }, []);

  const statusLabel: Record<ApiStatus, string> = {
    checking: "verificando…",
    online: "online",
    offline: "offline",
  };

  const statusColor: Record<ApiStatus, string> = {
    checking: "bg-yellow-400",
    online: "bg-green-500",
    offline: "bg-red-500",
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center p-6">
      <div className="max-w-md w-full text-center space-y-6">
        <h1 className="text-5xl font-bold tracking-tight">
          🔥 Finix
        </h1>
        <p className="text-zinc-400">
          Agente financeiro pessoal. A fundação está de pé — em breve, upload de
          extratos, categorização e insights.
        </p>

        <div className="inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm">
          <span className={`h-2.5 w-2.5 rounded-full ${statusColor[status]}`} />
          <span className="text-zinc-300">
            Backend: {statusLabel[status]}
          </span>
        </div>

        <p className="text-xs text-zinc-600">
          API em <code className="text-zinc-400">{API_URL}</code>
        </p>
      </div>
    </div>
  );
}
