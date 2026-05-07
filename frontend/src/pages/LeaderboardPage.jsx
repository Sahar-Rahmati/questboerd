import { useEffect, useState } from "react";
import client from "../api/client";
import ErrorMessage from "../components/common/ErrorMessage";
import DashboardLayout from "../components/layout/DashboardLayout";
import LeaderboardTable from "../components/charts/LeaderboardTable";

export default function LeaderboardPage() {
  const [tab, setTab] = useState("all-time");
  const [data, setData] = useState({ results: [] });
  const [error, setError] = useState("");

  useEffect(() => {
    client
      .get(`/leaderboard/${tab}/`)
      .then((response) => {
        setData(response.data);
        setError("");
      })
      .catch(() => setError("Unable to load the leaderboard."));
  }, [tab]);

  return (
    <DashboardLayout>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-3xl font-bold text-brand-ink">Leaderboard</h2>
            <p className="mt-2 text-sm text-slate-600">Track how your progress compares across all-time and weekly rankings.</p>
          </div>
          <div className="flex gap-2 rounded-2xl bg-white/70 p-1">
            {["all-time", "weekly"].map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setTab(item)}
                className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${tab === item ? "bg-brand-lagoon text-white" : "text-slate-600"}`}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
        {error && <ErrorMessage message={error} />}
        <LeaderboardTable rows={data.results || []} scoreKey={tab === "all-time" ? "total_xp" : "weekly_xp"} />
      </div>
    </DashboardLayout>
  );
}
