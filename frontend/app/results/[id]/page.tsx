// Single-analysis page ("/results/[id]") — lets History rows (and shared
// links) reopen a past report. Reuses ResultsDashboard, same as /analyze.
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import axios from "axios";
import { getResult } from "@/lib/api";
import ResultsDashboard from "@/components/ResultsDashboard";
import type { AnalysisOut } from "@/types/analysis";

export default function ResultPage() {
  const params = useParams<{ id: string }>();
  const [result, setResult] = useState<AnalysisOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // params.id here is actually the analysis's public_token — the folder
    // is still named [id] since that's just the URL segment name, but the
    // value itself is a random string now, not a number (see
    // backend/app/models/analysis.py's public_token field for why).
    getResult(params.id)
      .then(setResult)
      .catch((err) => {
        if (axios.isAxiosError(err) && err.response?.status === 403) {
          setError("You do not have access to this analysis.");
        } else if (axios.isAxiosError(err) && err.response?.status === 404) {
          setError("Analysis not found.");
        } else {
          setError("Could not load this analysis.");
        }
      });
  }, [params.id]);

  return (
    <main className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">
        {result ? `${result.language} analysis` : "Analysis"}
      </h1>
      {error && <p className="text-sm text-[#e66767]">{error}</p>}
      {!error && !result && <p className="text-sm text-zinc-500">Loading…</p>}
      {result && <ResultsDashboard result={result} />}
    </main>
  );
}
