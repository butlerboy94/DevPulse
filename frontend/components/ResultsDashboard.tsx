// Composes every report card (stats, quality meter, timing chart, hotspots,
// static issues, AI recommendations) into the full results view. Used on
// both /analyze (fresh results) and /results/[id] (past results).
import type { AnalysisOut } from "@/types/analysis";
import StatTile from "@/components/StatTile";
import QualityMeter from "@/components/QualityMeter";
import TimingChart from "@/components/TimingChart";
import HotspotTable from "@/components/HotspotTable";
import StaticIssues from "@/components/StaticIssues";
import AIRecommendations from "@/components/AIRecommendations";

// Same sub-millisecond-friendly formatting as TimingChart.tsx.
function formatMs(ms: number | null): string {
  if (ms == null) return "—";
  if (ms < 1) return `${(ms * 1000).toFixed(1)} µs`;
  return `${ms.toFixed(2)} ms`;
}

function formatBytes(bytes: number | null): string {
  if (bytes == null || bytes <= 0) return "N/A";
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  return `${(kb / 1024).toFixed(2)} MB`;
}

export default function ResultsDashboard({ result }: { result: AnalysisOut }) {
  // The sandboxed code itself failed (crash, timeout, syntax error, etc.).
  if (result.status === "error") {
    return (
      <div className="rounded-lg border border-[#d03b3b]/30 bg-[#d03b3b]/10 px-4 py-4">
        <h3 className="text-sm font-semibold text-[#e66767] mb-1">Analysis failed</h3>
        <p className="text-sm text-zinc-300">{result.error_message ?? "An unknown error occurred."}</p>
        {result.raw_results?.sandbox?.stdout && (
          <pre className="mt-3 text-xs text-zinc-400 bg-zinc-950 rounded p-2 overflow-x-auto whitespace-pre-wrap">
            {result.raw_results.sandbox.stdout}
          </pre>
        )}
      </div>
    );
  }

  // /analyze is synchronous today, so this branch rarely renders, but it's
  // here in case the pipeline ever becomes async.
  if (result.status === "pending" || result.status === "running") {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-6 text-center text-sm text-zinc-400">
        Analysis in progress…
      </div>
    );
  }

  const raw = result.raw_results;

  return (
    <div className="space-y-4">
      {/* Headline numbers */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatTile label="Execution time" value={formatMs(result.execution_time_ms)} />
        <StatTile label="Memory used" value={formatBytes(result.memory_bytes)} />
        <StatTile label="Lines of code" value={String(result.lines_of_code ?? "—")} />
        <StatTile
          label="Cyclomatic complexity"
          value={result.cyclomatic_complexity != null ? result.cyclomatic_complexity.toFixed(1) : "—"}
          sub={result.function_count != null ? `${result.function_count} functions` : undefined}
        />
      </div>

      {result.quality_score != null && <QualityMeter score={result.quality_score} />}

      {raw?.benchmark && <TimingChart benchmark={raw.benchmark} />}

      {raw?.profile && <HotspotTable hotspots={raw.profile.hotspots} />}

      {raw?.static_analysis && <StaticIssues report={raw.static_analysis} />}

      {/* AI recommendations are optional — no key configured, or the call failed */}
      {result.ai_recommendations ? (
        <AIRecommendations report={result.ai_recommendations} />
      ) : raw?.ai_error ? (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-500">
          AI recommendations unavailable: {raw.ai_error}
        </div>
      ) : (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-500">
          AI recommendations are not configured for this deployment.
        </div>
      )}
    </div>
  );
}
