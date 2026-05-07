import { useEffect, useState } from "react";
import client from "../api/client";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import DashboardLayout from "../components/layout/DashboardLayout";
import DifficultyBadge from "../components/tasks/DifficultyBadge";

export default function ActivityExplorerPage() {
  const [activities, setActivities] = useState([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    category: "other",
    difficulty: "easy",
    estimated_duration_minutes: 15,
  });
  const [error, setError] = useState("");

  const fetchActivities = async () => {
    try {
      const response = await client.get("/activities/");
      setActivities(response.data.results || response.data);
    } catch {
      setError("Unable to load activities.");
    }
  };

  useEffect(() => {
    fetchActivities();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await client.post("/activities/", form);
      setForm({
        title: "",
        description: "",
        category: "other",
        difficulty: "easy",
        estimated_duration_minutes: 15,
      });
      setError("");
      fetchActivities();
    } catch {
      setError("Unable to create custom activity.");
    }
  };

  return (
    <DashboardLayout>
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <section className="space-y-4">
          <div>
            <h2 className="text-3xl font-bold text-brand-ink">Activity Explorer</h2>
            <p className="mt-2 text-sm text-slate-600">Browse predefined activities or add your own reusable custom ones.</p>
          </div>
          {activities.length === 0 ? (
            <EmptyState title="No activities available" description="Seed predefined activities or create your own custom activity." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {activities.map((activity) => (
                <div key={activity.id} className="panel p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-semibold text-brand-ink">{activity.title}</h3>
                      <p className="mt-2 text-sm text-slate-600">{activity.description || "No description provided."}</p>
                    </div>
                    <DifficultyBadge difficulty={activity.difficulty} />
                  </div>
                  <div className="mt-4 flex flex-wrap gap-3 text-xs font-medium text-slate-500">
                    <span>{activity.category}</span>
                    <span>{activity.estimated_duration_minutes} min</span>
                    <span>{activity.is_predefined ? "Predefined" : "Custom"}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
        <form onSubmit={handleSubmit} className="panel space-y-4 p-6">
          <h3 className="text-xl font-bold text-brand-ink">Create Custom Activity</h3>
          {error && <ErrorMessage message={error} />}
          <input className="w-full rounded-2xl border border-slate-200 px-4 py-3" placeholder="Title" value={form.title} onChange={(e) => setForm((c) => ({ ...c, title: e.target.value }))} required />
          <textarea className="w-full rounded-2xl border border-slate-200 px-4 py-3" placeholder="Description" value={form.description} onChange={(e) => setForm((c) => ({ ...c, description: e.target.value }))} rows="4" />
          <select className="w-full rounded-2xl border border-slate-200 px-4 py-3" value={form.category} onChange={(e) => setForm((c) => ({ ...c, category: e.target.value }))}>
            <option value="reading">reading</option>
            <option value="studying">studying</option>
            <option value="workout">workout</option>
            <option value="coding">coding</option>
            <option value="cleaning">cleaning</option>
            <option value="other">other</option>
          </select>
          <select className="w-full rounded-2xl border border-slate-200 px-4 py-3" value={form.difficulty} onChange={(e) => setForm((c) => ({ ...c, difficulty: e.target.value }))}>
            <option value="easy">easy</option>
            <option value="medium">medium</option>
            <option value="hard">hard</option>
            <option value="extreme">extreme</option>
          </select>
          <input type="number" min="5" className="w-full rounded-2xl border border-slate-200 px-4 py-3" value={form.estimated_duration_minutes} onChange={(e) => setForm((c) => ({ ...c, estimated_duration_minutes: Number(e.target.value) }))} />
          <button className="w-full rounded-2xl bg-brand-lagoon px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-ink">
            Save Activity
          </button>
        </form>
      </div>
    </DashboardLayout>
  );
}
