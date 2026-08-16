// Small "report card" for a single number — e.g. execution time, memory
// used. Used in a grid at the top of ResultsDashboard.tsx.
interface StatTileProps {
  label: string;
  value: string;
  sub?: string;
}

export default function StatTile({ label, value, sub }: StatTileProps) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3">
      <div className="text-xs text-zinc-400">{label}</div>
      <div className="text-2xl font-semibold text-white mt-1">{value}</div>
      {sub && <div className="text-xs text-zinc-500 mt-1">{sub}</div>}
    </div>
  );
}
