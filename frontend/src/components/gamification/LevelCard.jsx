export default function LevelCard({ level = 1, totalXp = 0 }) {
  return (
    <div className="panel p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-ember">Current Level</p>
      <div className="mt-4 flex items-end justify-between">
        <h3 className="text-5xl font-extrabold text-brand-ink">{level}</h3>
        <p className="text-sm text-slate-600">{totalXp} total XP</p>
      </div>
    </div>
  );
}
