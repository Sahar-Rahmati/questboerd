import { useEffect, useState } from "react";
import client from "../api/client";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import LoadingSpinner from "../components/common/LoadingSpinner";
import DashboardLayout from "../components/layout/DashboardLayout";
import TaskCard from "../components/tasks/TaskCard";
import { useAuth } from "../hooks/useAuth";

export default function TasksPage() {
  const { refreshProfile } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await client.get("/tasks/");
      setTasks(response.data.results || response.data);
      setError("");
    } catch (err) {
      setError("Unable to load tasks.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleComplete = async (taskId, actualDurationMinutes) => {
    const response = await client.post(`/tasks/${taskId}/complete/`, { actual_duration_minutes: actualDurationMinutes });
    await Promise.all([fetchTasks(), refreshProfile()]);
    return response.data;
  };

  const handleDelete = async (taskId) => {
    await client.delete(`/tasks/${taskId}/`);
    await fetchTasks();
  };

  return (
    <DashboardLayout>
      <div className="space-y-4">
        <div>
          <h2 className="text-3xl font-bold text-brand-ink">Tasks</h2>
          <p className="mt-2 text-sm text-slate-600">Manage pending, completed, and cancelled quests in one place.</p>
        </div>
        {error && <ErrorMessage message={error} />}
        {loading ? (
          <LoadingSpinner label="Loading tasks..." />
        ) : tasks.length === 0 ? (
          <EmptyState title="No tasks found" description="Create a task from the Create Task page to start building momentum." />
        ) : (
          <div className="space-y-4">
            {tasks.map((task) => (
              <TaskCard key={task.id} task={task} onComplete={handleComplete} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
