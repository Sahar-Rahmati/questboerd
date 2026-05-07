import { useEffect, useState } from "react";
import client from "../api/client";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import LoadingSpinner from "../components/common/LoadingSpinner";
import LevelCard from "../components/gamification/LevelCard";
import XPProgressBar from "../components/gamification/XPProgressBar";
import DashboardLayout from "../components/layout/DashboardLayout";
import DashboardTaskPlanner from "../components/tasks/DashboardTaskPlanner";
import TaskCard from "../components/tasks/TaskCard";
import { useAuth } from "../hooks/useAuth";

export default function DashboardPage() {
  const { refreshProfile } = useAuth();
  const [summary, setSummary] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [rank, setRank] = useState(null);
  const [latestTask, setLatestTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const readyTasks = tasks.filter((task) => task.status === "pending");
  const completedTasks = [...tasks.filter((task) => task.status === "completed")].sort(
    (left, right) => new Date(right.completion?.completed_at || 0) - new Date(left.completion?.completed_at || 0)
  );

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const [summaryRes, tasksRes, rankRes] = await Promise.all([
        client.get("/gamification/summary/"),
        client.get("/tasks/"),
        client.get("/leaderboard/me/"),
      ]);
      setSummary(summaryRes.data);
      setTasks(tasksRes.data.results || tasksRes.data);
      setRank(rankRes.data);
      setError("");
    } catch (err) {
      setError("Unable to load the dashboard.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleComplete = async (taskId) => {
    const response = await client.post(`/tasks/${taskId}/complete/`);
    await Promise.all([fetchDashboard(), refreshProfile()]);
    return response.data;
  };

  const handleStart = async (taskId) => {
    const response = await client.post(`/tasks/${taskId}/start-session/`);
    await fetchDashboard();
    return response.data;
  };

  const handlePause = async (taskId) => {
    const response = await client.post(`/tasks/${taskId}/pause-session/`);
    await fetchDashboard();
    return response.data;
  };

  const handleResume = async (taskId) => {
    const response = await client.post(`/tasks/${taskId}/resume-session/`);
    await fetchDashboard();
    return response.data;
  };

  const handleDelete = async (taskId) => {
    await client.delete(`/tasks/${taskId}/`);
    await fetchDashboard();
  };

  const handleRefreshAi = async (taskId) => {
    const response = await client.post(`/tasks/${taskId}/refresh-ai/`);
    setLatestTask(response.data);
    await fetchDashboard();
    return response.data;
  };

  const handleCreateTask = async (payload) => {
    const response = await client.post("/tasks/", payload);
    setLatestTask(response.data);
    await fetchDashboard();
    return response.data;
  };

  if (loading) {
    return (
      <DashboardLayout>
        <LoadingSpinner label="Loading your dashboard..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      {error && <ErrorMessage message={error} />}
      {summary && (
        <>
          <section className="grid gap-4 xl:grid-cols-3">
            <LevelCard level={summary.profile.level} totalXp={summary.profile.total_xp} />
            <div className="panel p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-ember">Your Progress</p>
              <div className="mt-4 grid gap-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">All-time</span>
                  <span className="font-semibold text-brand-ink">#{rank?.all_time_rank ?? "-"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">This week</span>
                  <span className="font-semibold text-brand-ink">#{rank?.weekly_rank ?? "-"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Weekly XP</span>
                  <span className="font-semibold text-brand-lagoon">{summary.weekly_xp}</span>
                </div>
              </div>
            </div>
            <div className="panel p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-lagoon">Session Snapshot</p>
              <div className="mt-4 grid gap-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Ready to start</span>
                  <span className="font-semibold text-brand-ink">{readyTasks.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Completed sessions</span>
                  <span className="font-semibold text-brand-ink">{completedTasks.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Weekly XP</span>
                  <span className="font-semibold text-brand-lagoon">{summary.weekly_xp}</span>
                </div>
              </div>
            </div>
          </section>
          <section className="mt-4">
            <XPProgressBar totalXp={summary.profile.total_xp} level={summary.profile.level} />
          </section>
        </>
      )}
      <section className="mt-6">
        <DashboardTaskPlanner onSubmit={handleCreateTask} />
      </section>
      {latestTask && (
        <section className="mt-6">
          <div className="panel p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-ember">Task Added</p>
            <h2 className="mt-2 text-2xl font-bold text-brand-ink">{latestTask.title}</h2>
            <p className="mt-2 text-sm text-slate-600">
              Start the timer when you begin. With the current AI difficulty, this session is estimated at about {latestTask.estimated_xp} XP.
            </p>
            {latestTask.ai_explanation && <p className="mt-3 text-sm text-slate-600">{latestTask.ai_explanation}</p>}
          </div>
        </section>
      )}
      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-brand-ink">Ready to start</h2>
            <span className="rounded-full bg-brand-mint px-3 py-1 text-xs font-semibold text-brand-ink">{readyTasks.length} tasks</span>
          </div>
          {readyTasks.length === 0 ? (
            <EmptyState title="No tasks in your queue" description="Add a task above and start it when you are ready." />
          ) : (
            <div className="space-y-4">
              {readyTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onStart={handleStart}
                  onPause={handlePause}
                  onResume={handleResume}
                  onComplete={handleComplete}
                  onDelete={handleDelete}
                  onRefreshAi={handleRefreshAi}
                />
              ))}
            </div>
          )}
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-brand-ink">Completed sessions</h2>
            <span className="rounded-full bg-brand-sand px-3 py-1 text-xs font-semibold text-brand-ink">{completedTasks.length} tasks</span>
          </div>
          {completedTasks.length === 0 ? (
            <EmptyState title="Nothing completed yet" description="Finish a task and it will move here with the XP you earned." />
          ) : (
            <div className="space-y-4">
              {completedTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onStart={handleStart}
                  onPause={handlePause}
                  onResume={handleResume}
                  onComplete={handleComplete}
                  onDelete={handleDelete}
                  onRefreshAi={handleRefreshAi}
                />
              ))}
            </div>
          )}
        </div>
      </section>
    </DashboardLayout>
  );
}
