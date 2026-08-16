// Horizontal 0-100 quality meter, colored green/yellow/red by score. Used in
// ResultsDashboard.tsx to visualize static_analysis.quality_score.
interface QualityMeterProps {
  score: number;
  label?: string;
}

// Picks the fill color by severity band (matches the dataviz status palette).
function severityColor(score: number): { fill: string; text: string } {
  if (score >= 80) return { fill: "#0ca30c", text: "text-[#0ca30c]" }; // good
  if (score >= 50) return { fill: "#fab219", text: "text-[#fab219]" }; // warning
  return { fill: "#d03b3b", text: "text-[#e66767]" }; // critical
}

export default function QualityMeter({ score, label = "Quality score" }: QualityMeterProps) {
  const clamped = Math.max(0, Math.min(100, score));
  const { fill, text } = severityColor(clamped);

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3">
      <div className="flex items-baseline justify-between">
        <span className="text-xs text-zinc-400">{label}</span>
        <span className={`text-2xl font-semibold ${text}`}>{clamped.toFixed(0)}</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-zinc-800 overflow-hidden">
        <div
          className="h-full rounded-full transition-[width]"
          style={{ width: `${clamped}%`, backgroundColor: fill }}
        />
      </div>
    </div>
  );
}
