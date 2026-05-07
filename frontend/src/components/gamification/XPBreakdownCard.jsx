export default function XPBreakdownCard({ breakdown }) {
  if (!breakdown) return null;

  const rows = [
    ["Session time", `${breakdown.actual_duration_minutes} min`],
    ["Difficulty", breakdown.detected_difficulty],
    ["Earned XP", breakdown.final_xp],
  ];

  return (
    <div className="panel p-5">
      <h3 className="panel-title">XP Breakdown</h3>
      <div className="mt-4 space-y-3">
        {rows.map(([label, value]) => (
          <div key={label} className="flex items-center justify-between border-b border-slate-100 pb-2 text-sm">
            <span className="text-slate-500">{label}</span>
            <span className="font-semibold text-brand-ink">{value}</span>
          </div>
        ))}
      </div>
      {breakdown.anomaly_flags?.length > 0 && (
        <div className="mt-4 rounded-2xl bg-amber-50 p-3 text-sm text-amber-800">
          Reward limits were applied to keep this score fair.
        </div>
      )}
    </div>
  );
}
