// Main analysis page ("/analyze") — code editor on the left, results on the
// right. Works for both logged-in and anonymous visitors (the backend saves
// anonymous submissions without an owner).
"use client";

import { useState } from "react";
import axios from "axios";
import CodeEditor from "@/components/CodeEditor";
import ResultsDashboard from "@/components/ResultsDashboard";
import { analyzeCode } from "@/lib/api";
import type { AnalysisOut, Language } from "@/types/analysis";

// Pre-filled starter snippet so the editor isn't empty on first load.
const DEFAULT_CODE = `def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


for i in range(20):
    print(fibonacci(i))
`;

export default function AnalyzePage() {
  const [language, setLanguage] = useState<Language>("python");
  const [code, setCode] = useState(DEFAULT_CODE);
  const [iterations, setIterations] = useState(5);
  const [result, setResult] = useState<AnalysisOut | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setLoading(true);
    setSubmitError(null);
    setResult(null);
    try {
      const data = await analyzeCode({ language, source_code: code, iterations });
      setResult(data);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setSubmitError(String(err.response.data.detail));
      } else {
        setSubmitError("Something went wrong reaching the DevPulse API. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Analyze your code</h1>
        <p className="text-zinc-400 text-sm mt-1">
          Paste or write code below. DevPulse will benchmark it, check its quality, and give you
          AI-powered optimization tips.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          <CodeEditor language={language} onLanguageChange={setLanguage} code={code} onCodeChange={setCode} />
          <div className="flex items-center justify-between gap-4">
            <label className="flex items-center gap-2 text-sm text-zinc-400">
              Iterations
              <input
                type="number"
                min={1}
                max={50}
                value={iterations}
                onChange={(e) => setIterations(Number(e.target.value))}
                className="w-16 bg-zinc-900 text-zinc-200 text-sm rounded-md px-2 py-1 border border-zinc-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </label>
            <button
              onClick={handleSubmit}
              disabled={loading || code.trim().length === 0}
              className="bg-sky-500 hover:bg-sky-400 disabled:bg-zinc-700 disabled:cursor-not-allowed text-white font-semibold px-6 py-2 rounded-lg transition-colors"
            >
              {loading ? "Analyzing…" : "Run analysis"}
            </button>
          </div>
          {submitError && (
            <div className="rounded-lg border border-[#d03b3b]/30 bg-[#d03b3b]/10 px-4 py-3 text-sm text-[#e66767]">
              {submitError}
            </div>
          )}
        </div>

        <div>
          {result ? (
            <ResultsDashboard result={result} />
          ) : (
            <div className="rounded-lg border border-dashed border-zinc-800 h-full min-h-[300px] flex items-center justify-center text-sm text-zinc-500">
              Run an analysis to see results here.
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
