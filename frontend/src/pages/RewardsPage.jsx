import { useMemo, useState } from "react";
import client from "../api/client";
import ErrorMessage from "../components/common/ErrorMessage";
import DashboardLayout from "../components/layout/DashboardLayout";
import { useAuth } from "../hooks/useAuth";

const MILESTONE_STEP = 5;

const REWARD_OPTIONS = [
  {
    id: "bookstore",
    label: "Book Reward",
    eyebrow: "Reading reward",
    description: "Every 5 levels, unlock a free book reward you can claim through your book partner path.",
    milestoneRewards: ["1 free book reward"],
  },
  {
    id: "cafe_discount",
    label: "Cafe / Restaurant Discount",
    eyebrow: "Food partner reward",
    description: "Every 5 levels, unlock a 20% discount at selected cafe or restaurant partners.",
    milestoneRewards: ["20% off at Urth Caffe", "20% off at Pete's Cafe", "20% off at Alou Beirut"],
  },
];

function getMilestoneReward(option, level) {
  const milestoneIndex = Math.max(0, Math.floor(level / MILESTONE_STEP) - 1);
  return option.milestoneRewards[milestoneIndex % option.milestoneRewards.length];
}

export default function RewardsPage() {
  const { user, refreshProfile } = useAuth();
  const initialPreference =
    user?.reward_preference === "study_cafe" || user?.reward_preference === "gym_pool"
      ? "cafe_discount"
      : user?.reward_preference || "bookstore";
  const [selected, setSelected] = useState(initialPreference);
  const [saving, setSaving] = useState(false);
  const [claiming, setClaiming] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [claimDetails, setClaimDetails] = useState(null);

  const activeReward = useMemo(
    () => REWARD_OPTIONS.find((option) => option.id === selected) || REWARD_OPTIONS[0],
    [selected]
  );

  const nextUnlockLevel = user?.reward_current_target_level || MILESTONE_STEP;
  const xpRemaining = user?.reward_xp_remaining ?? 0;
  const levelsRemaining = user?.reward_levels_remaining ?? 0;
  const unlockedRewardCount = user?.reward_claims_count || 0;
  const rewardMemberId = user?.reward_member_id || "Generating...";
  const canClaimReward = Boolean(user?.reward_can_claim);
  const currentLevel = user?.level || 1;
  const progressWithinRewardCycle = Math.min(100, Math.max(0, ((MILESTONE_STEP - levelsRemaining) / MILESTONE_STEP) * 100));
  const nextReward = getMilestoneReward(activeReward, nextUnlockLevel);

  const handleSave = async () => {
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await client.patch("/auth/profile/", { reward_preference: selected });
      await refreshProfile();
      setMessage("Your reward path was saved.");
      setClaimDetails(null);
    } catch (saveError) {
      setError(saveError.response?.data?.detail || "Unable to save your reward path.");
    } finally {
      setSaving(false);
    }
  };

  const handleClaimReward = async () => {
    setClaiming(true);
    setError("");
    setMessage("");
    try {
      const response = await client.post("/auth/rewards/claim/");
      setClaimDetails(response.data);
      await refreshProfile();
      setMessage(`Reward claimed for level ${response.data.reward_level}.`);
    } catch (claimError) {
      setError(claimError.response?.data?.detail || "Unable to claim this reward right now.");
    } finally {
      setClaiming(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-brand-ink">Rewards</h2>
          <p className="mt-2 text-sm text-slate-600">
            Pick the kind of reward you want. The app always updates your next claim target automatically.
          </p>
        </div>

        {error && <ErrorMessage message={error} />}
        {message && <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div>}

        <section className="grid gap-4 xl:grid-cols-2">
          {REWARD_OPTIONS.map((option) => {
            const isActive = option.id === selected;
            return (
              <button
                key={option.id}
                type="button"
                onClick={() => setSelected(option.id)}
                className={`panel p-5 text-left transition ${
                  isActive ? "ring-2 ring-brand-lagoon bg-brand-mint/30" : "hover:bg-brand-mint/20"
                }`}
              >
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-ember">{option.eyebrow}</p>
                <h3 className="mt-2 text-2xl font-bold text-brand-ink">{option.label}</h3>
                <p className="mt-3 text-sm text-slate-600">{option.description}</p>
                <div className="mt-4 space-y-2 text-sm text-brand-ink">
                  {option.milestoneRewards.map((perk) => (
                    <p key={perk}>{perk}</p>
                  ))}
                </div>
              </button>
            );
          })}
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="panel p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-lagoon">Selected Path</p>
            <h3 className="mt-2 text-3xl font-bold text-brand-ink">{activeReward.label}</h3>
            <p className="mt-3 text-sm text-slate-600">{activeReward.description}</p>

            <div className="mt-4 rounded-2xl bg-brand-mint/30 p-4">
              <p className="text-sm text-slate-600">Current reward target</p>
              <p className="mt-1 text-2xl font-bold text-brand-ink">Level {nextUnlockLevel}</p>
              <p className="mt-2 text-sm font-medium text-brand-ink">{nextReward}</p>
              <div className="mt-4 h-3 overflow-hidden rounded-full bg-white/80">
                <div className="h-full rounded-full bg-brand-lagoon transition-all" style={{ width: `${progressWithinRewardCycle}%` }} />
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Current Level</p>
                  <p className="mt-1 text-lg font-semibold text-brand-ink">{currentLevel}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Remaining XP</p>
                  <p className="mt-1 text-lg font-semibold text-brand-ink">{xpRemaining.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Remaining Levels</p>
                  <p className="mt-1 text-lg font-semibold text-brand-ink">{levelsRemaining}</p>
                </div>
              </div>
              <div className="mt-4 rounded-2xl bg-white/80 p-4">
                <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Your Reward ID</p>
                <p className="mt-1 text-lg font-semibold text-brand-ink">{rewardMemberId}</p>
                <p className="mt-2 text-sm text-slate-600">Show this ID at the partner location when you claim a reward.</p>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleSave}
                disabled={saving}
                className="rounded-2xl bg-brand-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-lagoon"
              >
                {saving ? "Saving..." : "Save reward choice"}
              </button>
              <button
                type="button"
                onClick={handleClaimReward}
                disabled={!canClaimReward || claiming}
                className={`rounded-2xl px-5 py-3 text-sm font-semibold transition ${
                  canClaimReward
                    ? "bg-brand-lagoon text-white hover:bg-brand-ink"
                    : "cursor-not-allowed bg-slate-200 text-slate-500"
                }`}
              >
                {claiming ? "Claiming..." : `Claim level ${nextUnlockLevel} reward`}
              </button>
            </div>
          </div>

          <div className="panel p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-gold">Claim Instructions</p>
            <div className="mt-4 space-y-3">
              {claimDetails ? (
                <div className="rounded-2xl bg-brand-mint/30 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-brand-ink">{claimDetails.reward_title}</p>
                    <span className="text-xs font-semibold uppercase tracking-[0.12em] text-brand-ember">Claimed</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-600">Partner: {claimDetails.partner_name}</p>
                  <p className="mt-2 text-sm text-brand-ink">{claimDetails.instructions}</p>
                  <p className="mt-3 text-sm text-slate-600">
                    Show this ID: <span className="font-semibold text-brand-ink">{claimDetails.reward_member_id}</span>
                  </p>
                </div>
              ) : (
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="font-semibold text-brand-ink">How it works</p>
                  <p className="mt-2 text-sm text-slate-600">
                    When you reach level {nextUnlockLevel}, the claim button becomes active. After you claim that reward, your next target automatically moves to the next 5-level milestone.
                  </p>
                  <p className="mt-3 text-sm text-slate-600">
                    Book rewards can be collected by showing your Reward ID at the book partner desk. Cafe or restaurant discounts can be claimed by showing the same ID at the partner location.
                  </p>
                  <p className="mt-3 text-sm text-slate-600">
                    Rewards already claimed: <span className="font-semibold text-brand-ink">{unlockedRewardCount}</span>
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
