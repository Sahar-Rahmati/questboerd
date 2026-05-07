export default function XPProgressBar({ totalXp = 0, level = 1 }) {
  const xpIntoLevel = totalXp % 500;
  const progress = Math.min(100, Math.round((xpIntoLevel / 500) * 100));

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <h3 className="panel-title">XP Progress</h3>
        <span className="text-sm font-semibold text-brand-lagoon">Level {level}</span>
      </div>
      <div className="mt-4 h-4 overflow-hidden rounded-full bg-brand-mint">
        <div className="h-full rounded-full bg-gradient-to-r from-brand-lagoon to-brand-gold transition-all" style={{ width: `${progress}%` }} />
      </div>
      <p className="mt-3 text-sm text-slate-600">{xpIntoLevel} XP into the current level</p>
    </div>
  );
}
