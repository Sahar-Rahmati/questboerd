import { useState } from "react";
import ActivitySelector from "./ActivitySelector";
import AIClassificationPreview from "./AIClassificationPreview";

export default function CreateTaskForm({ activities, onPreview, onSubmit }) {
  const [form, setForm] = useState({
    activity: "",
    title: "",
    description: "",
    planned_date: new Date().toISOString().slice(0, 10),
  });
  const [preview, setPreview] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const updateField = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  const handlePreview = async () => {
    setLoadingPreview(true);
    try {
      const data = await onPreview({ title: form.title, description: form.description });
      setPreview(data);
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(form);
      setForm({
        activity: "",
        title: "",
        description: "",
        planned_date: new Date().toISOString().slice(0, 10),
      });
      setPreview(null);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
      <form onSubmit={handleSubmit} className="panel space-y-5 p-6">
        <h2 className="text-2xl font-bold text-brand-ink">Create a new quest</h2>
        <ActivitySelector activities={activities} value={form.activity} onChange={(value) => updateField("activity", value)} />
        <label className="grid gap-2 text-sm font-medium text-brand-ink">
          Title
          <input
            value={form.title}
            onChange={(event) => updateField("title", event.target.value)}
            className="rounded-2xl border border-slate-200 px-4 py-3 outline-none ring-brand-lagoon focus:ring-2"
            placeholder="Build authentication system"
            required
          />
        </label>
        <label className="grid gap-2 text-sm font-medium text-brand-ink">
          Description
          <textarea
            value={form.description}
            onChange={(event) => updateField("description", event.target.value)}
            rows="4"
            className="rounded-2xl border border-slate-200 px-4 py-3 outline-none ring-brand-lagoon focus:ring-2"
            placeholder="Ship login, refresh tokens, logout, and profile endpoints."
          />
        </label>
        <label className="grid gap-2 text-sm font-medium text-brand-ink">
          Planned date
          <input
            type="date"
            value={form.planned_date}
            onChange={(event) => updateField("planned_date", event.target.value)}
            className="rounded-2xl border border-slate-200 px-4 py-3 outline-none ring-brand-lagoon focus:ring-2"
            required
          />
        </label>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handlePreview}
            disabled={loadingPreview || !form.title}
            className="rounded-2xl border border-brand-lagoon px-5 py-3 text-sm font-semibold text-brand-lagoon transition hover:bg-brand-mint"
          >
            {loadingPreview ? "Previewing..." : "Preview AI Classification"}
          </button>
          <button
            type="submit"
            disabled={submitting || !form.activity}
            className="rounded-2xl bg-brand-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-lagoon"
          >
            {submitting ? "Creating..." : "Create Task"}
          </button>
        </div>
      </form>
      <AIClassificationPreview preview={preview} />
    </div>
  );
}
