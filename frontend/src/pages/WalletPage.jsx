import { useEffect, useState } from "react";
import client from "../api/client";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import DashboardLayout from "../components/layout/DashboardLayout";
import WalletCard from "../components/gamification/WalletCard";
import { useAuth } from "../hooks/useAuth";

export default function WalletPage() {
  const { user, refreshProfile } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [form, setForm] = useState({
    wallet_cardholder_name: "",
    wallet_card_number: "",
    wallet_card_expiry_month: "",
    wallet_card_expiry_year: "",
    apple_pay_enabled: false,
    samsung_pay_enabled: false,
    wallet_permissions_granted: false,
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    client
      .get("/gamification/wallet/")
      .then((response) => {
        setTransactions(response.data);
        setError("");
      })
      .catch(() => setError("Unable to load wallet transactions."));
  }, []);

  useEffect(() => {
    setForm({
      wallet_cardholder_name: user?.wallet_cardholder_name || "",
      wallet_card_number: "",
      wallet_card_expiry_month: user?.wallet_card_expiry_month || "",
      wallet_card_expiry_year: user?.wallet_card_expiry_year || "",
      apple_pay_enabled: Boolean(user?.apple_pay_enabled),
      samsung_pay_enabled: Boolean(user?.samsung_pay_enabled),
      wallet_permissions_granted: Boolean(user?.wallet_permissions_granted),
    });
  }, [user]);

  const updateField = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  const handleSaveWalletSettings = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await client.patch("/auth/profile/", {
        wallet_cardholder_name: form.wallet_cardholder_name,
        wallet_card_number: form.wallet_card_number,
        wallet_card_expiry_month: form.wallet_card_expiry_month ? Number(form.wallet_card_expiry_month) : null,
        wallet_card_expiry_year: form.wallet_card_expiry_year ? Number(form.wallet_card_expiry_year) : null,
        apple_pay_enabled: form.apple_pay_enabled,
        samsung_pay_enabled: form.samsung_pay_enabled,
        wallet_permissions_granted: form.wallet_permissions_granted,
      });
      await refreshProfile();
      setForm((current) => ({ ...current, wallet_card_number: "" }));
      setMessage("Wallet access settings were saved.");
    } catch (saveError) {
      setError(saveError.response?.data?.detail || "Unable to save wallet settings.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-brand-ink">Wallet</h2>
          <p className="mt-2 text-sm text-slate-600">Track milestone rewards and show linked wallet access preferences.</p>
        </div>
        {error && <ErrorMessage message={error} />}
        {message && <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div>}
        <WalletCard balance={user?.wallet_balance || 0} />
        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <form onSubmit={handleSaveWalletSettings} className="panel space-y-4 p-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-ember">Wallet Access</p>
              <h3 className="mt-2 text-2xl font-bold text-brand-ink">Apple Pay and Samsung Pay</h3>
              <p className="mt-2 text-sm text-slate-600">Use this section to demonstrate card capture and wallet permission preferences inside the app.</p>
            </div>
            <label className="grid gap-2 text-sm font-medium text-brand-ink">
              Cardholder name
              <input
                value={form.wallet_cardholder_name}
                onChange={(event) => updateField("wallet_cardholder_name", event.target.value)}
                className="rounded-2xl border border-slate-200 px-4 py-3"
                placeholder="Sahar Rahmati"
              />
            </label>
            <label className="grid gap-2 text-sm font-medium text-brand-ink">
              Card number
              <input
                value={form.wallet_card_number}
                onChange={(event) => updateField("wallet_card_number", event.target.value)}
                className="rounded-2xl border border-slate-200 px-4 py-3"
                placeholder="4111 1111 1111 1111"
                inputMode="numeric"
              />
            </label>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-2 text-sm font-medium text-brand-ink">
                Expiry month
                <input
                  type="number"
                  min="1"
                  max="12"
                  value={form.wallet_card_expiry_month}
                  onChange={(event) => updateField("wallet_card_expiry_month", event.target.value)}
                  className="rounded-2xl border border-slate-200 px-4 py-3"
                  placeholder="12"
                />
              </label>
              <label className="grid gap-2 text-sm font-medium text-brand-ink">
                Expiry year
                <input
                  type="number"
                  min="2024"
                  value={form.wallet_card_expiry_year}
                  onChange={(event) => updateField("wallet_card_expiry_year", event.target.value)}
                  className="rounded-2xl border border-slate-200 px-4 py-3"
                  placeholder="2028"
                />
              </label>
            </div>
            <label className="flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm font-medium text-brand-ink">
              <input
                type="checkbox"
                checked={form.apple_pay_enabled}
                onChange={(event) => updateField("apple_pay_enabled", event.target.checked)}
              />
              Enable Apple Pay access
            </label>
            <label className="flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm font-medium text-brand-ink">
              <input
                type="checkbox"
                checked={form.samsung_pay_enabled}
                onChange={(event) => updateField("samsung_pay_enabled", event.target.checked)}
              />
              Enable Samsung Pay access
            </label>
            <label className="flex items-center gap-3 rounded-2xl bg-brand-mint/40 px-4 py-3 text-sm font-medium text-brand-ink">
              <input
                type="checkbox"
                checked={form.wallet_permissions_granted}
                onChange={(event) => updateField("wallet_permissions_granted", event.target.checked)}
              />
              Permission to use wallet-linked payment methods was granted
            </label>
            <button
              type="submit"
              disabled={saving}
              className="w-full rounded-2xl bg-brand-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-lagoon"
            >
              {saving ? "Saving..." : "Save wallet settings"}
            </button>
          </form>
          <div className="panel space-y-4 p-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-lagoon">Linked Methods</p>
              <h3 className="mt-2 text-2xl font-bold text-brand-ink">Wallet presentation view</h3>
            </div>
            <div className="rounded-3xl bg-brand-ink p-5 text-white">
              <p className="text-xs uppercase tracking-[0.2em] text-brand-mint">{user?.wallet_card_brand || "Card"}</p>
              <p className="mt-4 text-2xl font-bold">{user?.wallet_card_masked || "No card saved yet"}</p>
              <div className="mt-4 flex items-center justify-between text-sm text-brand-mint">
                <span>{user?.wallet_cardholder_name || "Cardholder name"}</span>
                <span>
                  {user?.wallet_card_expiry_month && user?.wallet_card_expiry_year
                    ? `${String(user.wallet_card_expiry_month).padStart(2, "0")}/${user.wallet_card_expiry_year}`
                    : "MM/YYYY"}
                </span>
              </div>
            </div>
            <div className="grid gap-3">
              <div className="rounded-2xl bg-slate-50 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Apple Pay</p>
                <p className="mt-1 text-lg font-semibold text-brand-ink">{user?.apple_pay_enabled ? "Enabled" : "Not enabled"}</p>
              </div>
              <div className="rounded-2xl bg-slate-50 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Samsung Pay</p>
                <p className="mt-1 text-lg font-semibold text-brand-ink">{user?.samsung_pay_enabled ? "Enabled" : "Not enabled"}</p>
              </div>
              <div className="rounded-2xl bg-slate-50 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Wallet permission</p>
                <p className="mt-1 text-lg font-semibold text-brand-ink">{user?.wallet_permissions_granted ? "Granted" : "Pending"}</p>
              </div>
            </div>
          </div>
        </section>
        {transactions.length === 0 ? (
          <EmptyState title="No wallet rewards yet" description="Every 5 levels unlocks a 5 AED reward once per milestone." />
        ) : (
          <div className="panel overflow-hidden">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-brand-mint/50 text-left text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-semibold">Amount</th>
                  <th className="px-4 py-3 font-semibold">Reason</th>
                  <th className="px-4 py-3 font-semibold">Level</th>
                  <th className="px-4 py-3 font-semibold">Created At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td className="px-4 py-3 font-semibold text-brand-gold">{transaction.amount} AED</td>
                    <td className="px-4 py-3">{transaction.reason}</td>
                    <td className="px-4 py-3">{transaction.related_level || "-"}</td>
                    <td className="px-4 py-3">{new Date(transaction.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
