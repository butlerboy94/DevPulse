// Table of the slowest functions found by the cProfile-based profiler
// (raw_results.profile.hotspots), ranked by cumulative time.
import type { ProfileHotspot } from "@/types/analysis";

export default function HotspotTable({ hotspots }: { hotspots: ProfileHotspot[] }) {
  if (hotspots.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-500">
        No profiling hotspots recorded.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 overflow-hidden">
      <div className="px-4 py-3 text-xs text-zinc-400 border-b border-zinc-800">
        Slowest functions (by cumulative time)
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-zinc-500 text-xs">
              <th className="px-4 py-2 font-medium">Function</th>
              <th className="px-4 py-2 font-medium">Line</th>
              <th className="px-4 py-2 font-medium text-right">Calls</th>
              <th className="px-4 py-2 font-medium text-right tabular-nums">Total (ms)</th>
              <th className="px-4 py-2 font-medium text-right tabular-nums">Cumulative (ms)</th>
            </tr>
          </thead>
          <tbody>
            {/* Cap at 10 rows — the backend already sends the top 10 (see CodeProfiler(top_n=10)) */}
            {hotspots.slice(0, 10).map((h, i) => (
              <tr key={`${h.function_name}-${i}`} className="border-t border-zinc-800/60">
                <td className="px-4 py-2 text-zinc-200 font-mono text-xs">{h.function_name}</td>
                <td className="px-4 py-2 text-zinc-500 text-xs">
                  {/* filename is "~" for built-ins with no real source line */}
                  {h.filename !== "~" ? `${h.filename.split(/[\\/]/).pop()}:${h.line_number}` : "—"}
                </td>
                <td className="px-4 py-2 text-zinc-300 text-right tabular-nums">{h.call_count}</td>
                <td className="px-4 py-2 text-zinc-300 text-right tabular-nums">
                  {h.total_time_ms.toFixed(3)}
                </td>
                <td className="px-4 py-2 text-zinc-300 text-right tabular-nums">
                  {h.cumulative_time_ms.toFixed(3)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
