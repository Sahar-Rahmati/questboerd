import { useState } from "react";
import AIClassificationPreview from "./AIClassificationPreview";

export default function DashboardTaskPlanner({ onSubmit }) {
  const [form, setForm] = useState({
    title: "",
    description: "",
  });
  const [preview, setPreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const updateField = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  const resetForm = () => {
    setForm({
      title: "",
      description: "",
    });
  };

  const handleAdd = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      if (!form.title.trim()) {
        throw new Error("Please enter a task title.");
      }
      const createdTask = await onSubmit({
        title: form.title,
        description: form.description,
      });
      setPreview({
        detected_category: createdTask.ai_detected_category,
        detected_difficulty: createdTask.ai_detected_difficulty,
        estimated_duration_minutes: createdTask.ai_estimated_duration_minutes,
        estimated_xp: createdTask.estimated_xp,
        explanation: createdTask.ai_explanation,
        is_quick_task: createdTask.ai_estimated_duration_minutes <= 15,
        estimated_workload: createdTask.ai_estimated_duration_minutes <= 15 ? "light" : createdTask.ai_estimated_duration_minutes <= 60 ? "moderate" : "deep",
      });
      resetForm();
    } catch (submitError) {
      const message =
        submitError.code === "ECONNABORTED"
          ? "The AI took too long to respond. Please try again."
          : submitError.response?.data?.detail || submitError.message || "Unable to add this task.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <form onSubmit={handleAdd} className="panel space-y-5 p-6">
        <div>
          <h2 className="text-2xl font-bold text-brand-ink">Add a task</h2>
          <p className="mt-2 text-sm text-slate-600">Write what you want to do now. Start the timer when you are ready to begin.</p>
        </div>

        <label className="grid gap-2 text-sm font-medium text-brand-ink">
          Title
          <input
            value={form.title}
            onChange={(event) => updateField("title", event.target.value)}
            className="rounded-2xl border border-slate-200 px-4 py-3 outline-none ring-brand-lagoon focus:ring-2"
            placeholder="Drink water"
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
            placeholder="Add a few details about what you want to get done."
          />
        </label>

        {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-2xl bg-brand-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-lagoon"
        >
          {submitting ? "Adding task..." : "Add task to queue"}
        </button>
      </form>

      <AIClassificationPreview preview={preview} />
    </div>
  );
}
