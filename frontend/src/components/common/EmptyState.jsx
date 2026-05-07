export default function EmptyState({ title, description }) {
  return (
    <div className="panel flex min-h-[180px] flex-col items-center justify-center px-6 py-10 text-center">
      <h3 className="text-lg font-semibold text-brand-ink">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-slate-600">{description}</p>
    </div>
  );
}
