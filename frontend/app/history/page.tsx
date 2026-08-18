// History page ("/history") — table of the logged-in user's past analyses.
// Redirects to /login if nobody's signed in, since this data is per-account.
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getHistory } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import type { AnalysisHistoryItem } from "@/types/analysis";

// Row status text color, by AnalysisStatus.
const STATUS_STYLE: Record<string, string> = {
  complete: "text-[#0ca30c]",
  error: "text-[#e66767]",
  running: "text-[#fab219]",
  pending: "text-zinc-400",
};

export default function HistoryPage() {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const [items, setItems] = useState<AnalysisHistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    getHistory()
      .then(setItems)
      .catch(() => setError("Could not load your analysis history."));
  }, [token, router]);

  if (!token) return null;

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">Analysis history</h1>

      {error && <p className="text-sm text-[#e66767]">{error}</p>}

      {!error && items === null && <p className="text-sm text-zinc-500">Loading…</p>}

      {items !== null && items.length === 0 && (
        <p className="text-sm text-zinc-500">
          No analyses yet.{" "}
          <Link href="/analyze" className="text-sky-400 hover:underline">
            Run your first one
          </Link>
          .
        </p>
      )}

      {items !== null && items.length > 0 && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 overflow-hidden">
          {/* overflow-x-auto lets the table scroll sideways on narrow
              screens instead of squeezing 5 columns into a phone-width
              container (same pattern as HotspotTable.tsx) */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-zinc-500 text-xs border-b border-zinc-800">
                  <th className="px-4 py-2 font-medium">Language</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium text-right">Quality</th>
                  <th className="px-4 py-2 font-medium text-right">Execution time</th>
                  <th className="px-4 py-2 font-medium text-right">Submitted</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.public_id} className="border-t border-zinc-800/60 hover:bg-zinc-800/40">
                    <td className="px-4 py-2">
                      <Link href={`/results/${item.public_id}`} className="text-sky-400 hover:underline">
                        {item.language}
                      </Link>
                    </td>
                    <td className={`px-4 py-2 ${STATUS_STYLE[item.status] ?? "text-zinc-400"}`}>
                      {item.status}
                    </td>
                    <td className="px-4 py-2 text-right tabular-nums text-zinc-300">
                      {item.quality_score != null ? item.quality_score.toFixed(0) : "—"}
                    </td>
                    <td className="px-4 py-2 text-right tabular-nums text-zinc-300">
                      {item.execution_time_ms != null ? `${item.execution_time_ms.toFixed(2)} ms` : "—"}
                    </td>
                    <td className="px-4 py-2 text-right text-zinc-500">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </main>
  );
}
