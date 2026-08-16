// Lists naming-convention violations and unused variables found by the
// ast-based static analyzer (raw_results.static_analysis).
import type { StaticAnalysisRaw } from "@/types/analysis";

export default function StaticIssues({ report }: { report: StaticAnalysisRaw }) {
  const totalIssues = report.naming_violations.length + report.unused_variables.length;

  if (totalIssues === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-zinc-500">
        No naming or unused-variable issues found.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3">
      <div className="text-xs text-zinc-400 mb-3">Code style issues ({totalIssues})</div>
      <ul className="space-y-1.5 text-sm">
        {report.naming_violations.map((v, i) => (
          <li key={`naming-${i}`} className="flex items-start gap-2 text-zinc-300">
            <span className="text-[#fab219] shrink-0">line {v.line_number}</span>
            <span>
              <span className="font-mono text-zinc-100">{v.name}</span> — {v.reason}
            </span>
          </li>
        ))}
        {report.unused_variables.map((v, i) => (
          <li key={`unused-${i}`} className="flex items-start gap-2 text-zinc-300">
            <span className="text-[#fab219] shrink-0">line {v.line_number}</span>
            <span>
              <span className="font-mono text-zinc-100">{v.name}</span> is assigned but never used (in{" "}
              {v.scope})
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
