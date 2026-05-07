import DifficultyBadge from "./DifficultyBadge";

export default function AIClassificationPreview({ preview }) {
  if (!preview) return null;

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <h3 className="panel-title">Smart Estimate</h3>
        <DifficultyBadge difficulty={preview.detected_difficulty} />
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div className="rounded-2xl bg-brand-mint/50 p-4">
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Focus</p>
          <p className="mt-2 text-lg font-semibold text-brand-ink">{preview.detected_category}</p>
        </div>
        <div className="rounded-2xl bg-brand-sand p-4">
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Workload</p>
          <p className="mt-2 text-lg font-semibold text-brand-ink">{preview.estimated_workload}</p>
        </div>
        <div className="rounded-2xl bg-brand-sand p-4">
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Estimated Duration</p>
          <p className="mt-2 text-lg font-semibold text-brand-ink">{preview.estimated_duration_minutes} minutes</p>
        </div>
        <div className="rounded-2xl bg-brand-mint/50 p-4">
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Expected Reward</p>
          <p className="mt-2 text-lg font-semibold text-brand-ink">{preview.estimated_xp}</p>
        </div>
        <div className="rounded-2xl bg-brand-mint/50 p-4">
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Task Type</p>
          <p className="mt-2 text-lg font-semibold text-brand-ink">{preview.is_quick_task ? "Quick task" : "Focused session"}</p>
        </div>
      </div>
      <p className="mt-4 text-sm text-slate-600">{preview.explanation}</p>
    </div>
  );
}
