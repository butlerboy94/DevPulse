// Renders Claude's structured optimization report (ai_recommendations):
// a summary, an overall score, and a list of severity-tagged suggestions.
import type { AIReport } from "@/types/analysis";

// Badge color per severity level, using the dataviz status palette.
const SEVERITY_STYLE: Record<string, string> = {
  high: "bg-[#d03b3b]/15 text-[#e66767] border-[#d03b3b]/30",
  medium: "bg-[#fab219]/15 text-[#fab219] border-[#fab219]/30",
  low: "bg-[#0ca30c]/15 text-[#0ca30c] border-[#0ca30c]/30",
};

export default function AIRecommendations({ report }: { report: AIReport }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-white">AI recommendations</h3>
        <span className="text-xs text-zinc-500">Overall score: {report.overall_score}/100</span>
      </div>
      <p className="text-sm text-zinc-400 mb-4">{report.summary}</p>
      <div className="space-y-3">
        {report.recommendations.map((rec, i) => (
          <div key={i} className="rounded-md border border-zinc-800 px-3 py-3">
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="text-sm font-medium text-zinc-100">{rec.title}</span>
              <span
                className={`text-[10px] uppercase tracking-wide font-semibold px-2 py-0.5 rounded-full border shrink-0 ${
                  SEVERITY_STYLE[rec.severity] ?? SEVERITY_STYLE.low
                }`}
              >
                {rec.severity}
              </span>
            </div>
            <p className="text-sm text-zinc-400 mb-2">{rec.explanation}</p>
            <p className="text-sm text-sky-300/90 bg-sky-500/5 border border-sky-500/10 rounded px-2 py-1.5">
              {rec.suggested_fix}
            </p>
          </div>
        ))}
        {report.recommendations.length === 0 && (
          <p className="text-sm text-zinc-500">No issues found — nice work.</p>
        )}
      </div>
    </div>
  );
}
