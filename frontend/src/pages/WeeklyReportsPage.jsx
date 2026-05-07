import { useEffect, useState } from "react";
import client from "../api/client";
import CategoryBreakdownChart from "../components/charts/CategoryBreakdownChart";
import WeeklyReportChart from "../components/charts/WeeklyReportChart";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import DashboardLayout from "../components/layout/DashboardLayout";

export default function WeeklyReportsPage() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    client
      .get("/reports/weekly/")
      .then((response) => {
        setReport(response.data);
        setError("");
      })
      .catch(() => setError("Unable to load the weekly report."));
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-brand-ink">Weekly Reports</h2>
          <p className="mt-2 text-sm text-slate-600">Understand how you spent your time, which categories drove XP, and which tasks were toughest.</p>
        </div>
        {error && <ErrorMessage message={error} />}
        {!report ? (
          <EmptyState title="No weekly report yet" description="Complete a few tasks this week to generate charts and summaries." />
        ) : (
          <>
            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="panel p-5">
                <p className="text-xs uppercase tracking-[0.2em] text-brand-lagoon">Tasks Completed</p>
                <h3 className="mt-3 text-4xl font-extrabold text-brand-ink">{report.tasks_completed_count}</h3>
              </div>
              <div className="panel p-5">
                <p className="text-xs uppercase tracking-[0.2em] text-brand-ember">Total XP</p>
                <h3 className="mt-3 text-4xl font-extrabold text-brand-ink">{report.total_xp_earned}</h3>
              </div>
              <div className="panel p-5">
                <p className="text-xs uppercase tracking-[0.2em] text-brand-gold">Active Days</p>
                <h3 className="mt-3 text-4xl font-extrabold text-brand-ink">{report.daily_xp_chart?.length || 0}</h3>
              </div>
              <div className="panel p-5">
                <p className="text-xs uppercase tracking-[0.2em] text-brand-lagoon">Top Sessions</p>
                <h3 className="mt-3 text-4xl font-extrabold text-brand-ink">{report.hardest_tasks?.length || 0}</h3>
              </div>
            </section>
            <section className="grid gap-6 xl:grid-cols-2">
              <WeeklyReportChart data={report.daily_xp_chart || []} />
              <CategoryBreakdownChart data={report.category_breakdown || []} />
            </section>
            <section className="panel p-5">
              <h3 className="panel-title">Top Sessions This Week</h3>
              <div className="mt-4 overflow-auto">
                <table className="min-w-full divide-y divide-slate-100 text-sm">
                  <thead>
                    <tr className="text-left text-slate-500">
                      <th className="py-3 pr-4">Task</th>
                      <th className="py-3 pr-4">Difficulty</th>
                      <th className="py-3 pr-4">XP</th>
                      <th className="py-3 pr-4">Completed At</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {(report.hardest_tasks || []).map((task) => (
                      <tr key={task.task_id}>
                        <td className="py-3 pr-4 font-semibold text-brand-ink">{task.title}</td>
                        <td className="py-3 pr-4">{task.difficulty}</td>
                        <td className="py-3 pr-4">{task.earned_xp}</td>
                        <td className="py-3 pr-4">{new Date(task.completed_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
