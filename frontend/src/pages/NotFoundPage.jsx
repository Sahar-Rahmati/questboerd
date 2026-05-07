import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="panel max-w-lg p-10 text-center">
        <p className="text-xs uppercase tracking-[0.3em] text-brand-ember">404</p>
        <h1 className="mt-3 text-4xl font-extrabold text-brand-ink">This quest page does not exist.</h1>
        <Link to="/" className="mt-6 inline-flex rounded-2xl bg-brand-lagoon px-5 py-3 text-sm font-semibold text-white">
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
