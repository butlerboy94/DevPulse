// Horizontal bar comparison of min/median/mean/p95/max execution time for
// one analysis run. Plain HTML/CSS bars rather than a charting library, so
// the rounded ends and spacing are easy to control exactly.
import type { BenchmarkRaw } from "@/types/analysis";

const SERIES_COLOR = "#3987e5"; // dark-mode categorical slot 1 (blue)

// Formats a millisecond value as either "62.6 µs" (sub-millisecond) or
// "1.23 ms", so fast runs don't show a string of leading zeros.
function formatMs(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(1)} µs`;
  return `${ms.toFixed(2)} ms`;
}

export default function TimingChart({ benchmark }: { benchmark: BenchmarkRaw }) {
  const rows: { label: string; value: number }[] = [
    { label: "Min", value: benchmark.min_time_ms },
    { label: "Median", value: benchmark.median_time_ms },
    { label: "Mean", value: benchmark.execution_time_ms },
    { label: "P95", value: benchmark.p95_time_ms },
    { label: "Max", value: benchmark.max_time_ms },
  ];
  // Longest bar is scaled to 100% width; the rest are relative to it.
  const max = Math.max(...rows.map((r) => r.value), 0.0001);

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-zinc-400">Execution time across {benchmark.iterations} runs</span>
        <span className="text-xs text-zinc-500">
          {benchmark.source === "cpp_engine" ? "C++ engine" : "Python fallback"}
        </span>
      </div>
      <div className="space-y-2">
        {rows.map((row) => (
          <div key={row.label} className="flex items-center gap-3">
            <span className="w-14 text-xs text-zinc-400 shrink-0">{row.label}</span>
            <div className="flex-1 h-4 rounded-full bg-zinc-800 overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${(row.value / max) * 100}%`,
                  backgroundColor: SERIES_COLOR,
                }}
              />
            </div>
            <span className="w-20 text-xs text-zinc-300 text-right tabular-nums shrink-0">
              {formatMs(row.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
