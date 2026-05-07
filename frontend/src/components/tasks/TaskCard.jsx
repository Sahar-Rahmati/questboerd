import { useEffect, useState } from "react";
import DifficultyBadge from "./DifficultyBadge";
import XPBreakdownCard from "../gamification/XPBreakdownCard";

function formatElapsed(totalSeconds) {
  const safeSeconds = Math.max(0, totalSeconds);
  const hours = String(Math.floor(safeSeconds / 3600)).padStart(2, "0");
  const minutes = String(Math.floor((safeSeconds % 3600) / 60)).padStart(2, "0");
  const seconds = String(safeSeconds % 60).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

export default function TaskCard({ task, onStart, onPause, onResume, onComplete, onDelete, onRefreshAi }) {
  const [breakdown, setBreakdown] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [refreshingAi, setRefreshingAi] = useState(false);
  const [sessionLoading, setSessionLoading] = useState(false);
  const [error, setError] = useState("");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    if (!task.session?.is_active) {
      setElapsedSeconds(task.session?.elapsed_seconds || 0);
      return undefined;
    }

    if (task.session?.is_paused || !task.session?.started_at) {
      setElapsedSeconds(task.session?.elapsed_seconds || 0);
      return undefined;
    }

    const updateElapsed = () => {
      const startedAt = new Date(task.session.started_at).getTime();
      const baseSeconds = task.session?.accumulated_seconds || 0;
      setElapsedSeconds(baseSeconds + Math.max(0, Math.floor((Date.now() - startedAt) / 1000)));
    };

    updateElapsed();
    const intervalId = window.setInterval(updateElapsed, 1000);
    return () => window.clearInterval(intervalId);
  }, [task.session]);

  const handleStart = async () => {
    setSessionLoading(true);
    setError("");
    try {
      await onStart(task.id);
    } catch (startError) {
      setError(startError.response?.data?.detail || "Unable to start this task.");
    } finally {
      setSessionLoading(false);
    }
  };

  const handleComplete = async () => {
    setSubmitting(true);
    setError("");
    try {
      const result = await onComplete(task.id);
      setBreakdown(result.xp_breakdown);
    } catch (completeError) {
      setError(completeError.response?.data?.detail || "Unable to finish this task.");
    } finally {
      setSubmitting(false);
    }
  };

  const handlePause = async () => {
    setSessionLoading(true);
    setError("");
    try {
      await onPause(task.id);
    } catch (pauseError) {
      setError(pauseError.response?.data?.detail || "Unable to pause this task.");
    } finally {
      setSessionLoading(false);
    }
  };

  const handleResume = async () => {
    setSessionLoading(true);
    setError("");
    try {
      await onResume(task.id);
    } catch (resumeError) {
      setError(resumeError.response?.data?.detail || "Unable to resume this task.");
    } finally {
      setSessionLoading(false);
    }
  };

  const handleRefreshAi = async () => {
    setRefreshingAi(true);
    setError("");
    try {
      await onRefreshAi?.(task.id);
    } catch (refreshError) {
      setError(refreshError.response?.data?.detail || "Unable to update this estimate.");
    } finally {
      setRefreshingAi(false);
    }
  };

  const isRunning = task.session?.is_running;
  const isPaused = task.session?.is_paused;
  const isCompleted = task.status === "completed";
  const deleteLabel = isCompleted ? "Remove from list" : "Remove Task";
  const displayedReward = isCompleted ? task.completion?.earned_xp : task.estimated_xp;
  const rewardLabel = isCompleted ? "Earned reward" : "Estimated reward";

  return (
    <div className="panel p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h3 className="text-xl font-semibold text-brand-ink">{task.title}</h3>
            <DifficultyBadge difficulty={task.ai_detected_difficulty} />
          </div>
          {task.description && <p className="mt-2 text-sm text-slate-600">{task.description}</p>}
          <div className="mt-4 flex flex-wrap gap-3 text-xs font-medium text-slate-500">
            <span>Status: {task.status}</span>
            <span>{rewardLabel}: {displayedReward} XP</span>
            {isRunning && <span>Timer: {formatElapsed(elapsedSeconds)}</span>}
            {isPaused && <span>Paused at: {formatElapsed(elapsedSeconds)}</span>}
            {task.session?.tracked_duration_minutes > 0 && <span>Tracked: {task.session.tracked_duration_minutes} min</span>}
            {!isRunning && !task.session && <span>Not started yet</span>}
          </div>
          {task.ai_explanation && <p className="mt-3 text-sm text-slate-600">{task.ai_explanation}</p>}
        </div>
        <div className="w-full max-w-xs space-y-3">
          {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}
          {!isCompleted && (
            <>
              {!isRunning ? (
                isPaused ? (
                  <button
                    type="button"
                    onClick={handleResume}
                    disabled={sessionLoading}
                    className="w-full rounded-2xl bg-brand-lagoon px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-ink"
                  >
                    {sessionLoading ? "Resuming..." : "Resume task"}
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleStart}
                    disabled={sessionLoading}
                    className="w-full rounded-2xl bg-brand-lagoon px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-ink"
                  >
                    {sessionLoading ? "Starting..." : "Start task"}
                  </button>
                )
              ) : (
                <>
                  <button
                    type="button"
                    onClick={handlePause}
                    disabled={sessionLoading}
                    className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-brand-lagoon hover:text-brand-lagoon"
                  >
                    {sessionLoading ? "Pausing..." : "Pause task"}
                  </button>
                  <button
                    type="button"
                    onClick={handleComplete}
                    disabled={submitting}
                    className="w-full rounded-2xl bg-brand-lagoon px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-ink"
                  >
                    {submitting ? "Finishing..." : "Finish task"}
                  </button>
                </>
              )}
              {isPaused && (
                <button
                  type="button"
                  onClick={handleComplete}
                  disabled={submitting}
                  className="w-full rounded-2xl bg-brand-lagoon px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-ink"
                >
                  {submitting ? "Finishing..." : "Finish task"}
                </button>
              )}
              <button
                type="button"
                onClick={handleRefreshAi}
                disabled={refreshingAi || isRunning || isPaused}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-brand-lagoon hover:text-brand-lagoon"
              >
                {refreshingAi ? "Updating estimate..." : "Update estimate"}
              </button>
            </>
          )}
          <button
            type="button"
            onClick={() => onDelete(task.id)}
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-600 transition hover:border-rose-200 hover:text-rose-700"
          >
            {deleteLabel}
          </button>
        </div>
      </div>
      <XPBreakdownCard breakdown={breakdown || task.completion?.xp_breakdown} />
    </div>
  );
}
