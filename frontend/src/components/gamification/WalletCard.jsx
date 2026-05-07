export default function WalletCard({ balance = 0 }) {
  return (
    <div className="panel p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-gold">Wallet Rewards</p>
      <div className="mt-4 flex items-end justify-between">
        <h3 className="text-4xl font-extrabold text-brand-ink">{balance} AED</h3>
        <p className="text-sm text-slate-600">milestone rewards</p>
      </div>
    </div>
  );
}
