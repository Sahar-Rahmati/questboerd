import { useEffect, useState } from "react";
import client from "../api/client";
import DashboardLayout from "../components/layout/DashboardLayout";
import ErrorMessage from "../components/common/ErrorMessage";
import LevelCard from "../components/gamification/LevelCard";
import { useAuth } from "../hooks/useAuth";

export default function ProfilePage() {
  const { user } = useAuth();
  const [xpTransactions, setXpTransactions] = useState([]);
  const [levelHistory, setLevelHistory] = useState([]);
  const [error, setError] = useState("");
  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(" ") || "Not provided";

  useEffect(() => {
    Promise.all([client.get("/gamification/transactions/"), client.get("/gamification/levels/")])
      .then(([xpRes, levelRes]) => {
        setXpTransactions(xpRes.data);
        setLevelHistory(levelRes.data);
        setError("");
      })
      .catch(() => setError("Unable to load profile activity."));
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-brand-ink">Profile</h2>
          <p className="mt-2 text-sm text-slate-600">Your account overview, recent XP events, and level milestones.</p>
        </div>
        {error && <ErrorMessage message={error} />}
        <section className="grid gap-4 md:grid-cols-2">
          <LevelCard level={user?.level || 1} totalXp={user?.total_xp || 0} />
          <div className="panel p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-lagoon">Session Progress</p>
            <div className="mt-4 grid gap-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">XP events logged</span>
                <span className="font-semibold text-brand-ink">{xpTransactions.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Levels reached</span>
                <span className="font-semibold text-brand-ink">{levelHistory.length}</span>
              </div>
            </div>
          </div>
        </section>
        <section className="panel p-6">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-lagoon">Account Information</p>
              <h3 className="mt-2 text-2xl font-bold text-brand-ink">{fullName}</h3>
              <p className="mt-2 text-sm text-slate-600">
                This page shows who the account belongs to and how their session-based progress is evolving over time.
              </p>
            </div>
            <div className="rounded-2xl bg-brand-mint/50 px-4 py-3 text-right">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Account role</p>
              <p className="mt-1 text-lg font-semibold text-brand-ink">Productivity Player</p>
            </div>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Full name</p>
              <p className="mt-2 text-lg font-semibold text-brand-ink">{fullName}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Username</p>
              <p className="mt-2 text-lg font-semibold text-brand-ink">{user?.username || "Not provided"}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Email</p>
              <p className="mt-2 text-lg font-semibold text-brand-ink">{user?.email || "Not provided"}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Level</p>
              <p className="mt-2 text-lg font-semibold text-brand-ink">{user?.level || 1}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Total XP</p>
              <p className="mt-2 text-lg font-semibold text-brand-ink">{user?.total_xp || 0}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Member since</p>
              <p className="mt-2 text-lg font-semibold text-brand-ink">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Not available"}
              </p>
            </div>
          </div>
        </section>
        <section className="grid gap-6 xl:grid-cols-2">
          <div className="panel p-5">
            <h3 className="panel-title">Recent XP Transactions</h3>
            <div className="mt-4 space-y-3">
              {xpTransactions.map((transaction) => (
                <div key={transaction.id} className="rounded-2xl bg-slate-50 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-brand-ink">{transaction.description}</p>
                    <span className="text-sm font-semibold text-brand-lagoon">{transaction.amount} XP</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{transaction.transaction_type}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="panel p-5">
            <h3 className="panel-title">Level History</h3>
            <div className="mt-4 space-y-3">
              {levelHistory.map((entry) => (
                <div key={entry.id} className="rounded-2xl bg-brand-mint/40 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-brand-ink">
                      Level {entry.old_level} → Level {entry.new_level}
                    </p>
                    <span className="text-xs font-semibold uppercase tracking-[0.12em] text-brand-ember">
                      {entry.reward_granted ? "Legacy reward" : "Level reached"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
