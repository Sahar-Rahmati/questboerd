export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="flex min-h-[180px] items-center justify-center">
      <div className="flex items-center gap-3 rounded-full bg-white/80 px-5 py-3 shadow-panel">
        <div className="h-3 w-3 animate-pulse rounded-full bg-brand-lagoon" />
        <span className="text-sm font-medium text-brand-ink">{label}</span>
      </div>
    </div>
  );
}
