import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import ErrorMessage from "../components/common/ErrorMessage";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(form);
      navigate(location.state?.from?.pathname || "/");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="panel grid max-w-5xl overflow-hidden lg:grid-cols-[1.1fr_0.9fr]">
        <div className="bg-brand-ink p-10 text-white">
          <p className="text-xs uppercase tracking-[0.3em] text-brand-mint">Questboard</p>
          <h1 className="mt-4 text-5xl font-extrabold leading-tight">Turn daily work into a game you can win.</h1>
          <p className="mt-4 max-w-lg text-sm text-brand-mint">
            AI-assisted task scoring, live sessions, level progression, leaderboards, and weekly reports in one focused workspace.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5 p-10">
          <div>
            <h2 className="text-3xl font-bold text-brand-ink">Login</h2>
            <p className="mt-2 text-sm text-slate-600">Pick up where you left off and continue your session journey.</p>
          </div>
          {error && <ErrorMessage message={error} />}
          <label className="grid gap-2 text-sm font-medium text-brand-ink">
            Email
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
              className="rounded-2xl border border-slate-200 px-4 py-3 outline-none ring-brand-lagoon focus:ring-2"
              required
            />
          </label>
          <label className="grid gap-2 text-sm font-medium text-brand-ink">
            Password
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
              className="rounded-2xl border border-slate-200 px-4 py-3 outline-none ring-brand-lagoon focus:ring-2"
              required
            />
          </label>
          <button className="w-full rounded-2xl bg-brand-lagoon px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-ink">
            {loading ? "Signing in..." : "Sign In"}
          </button>
          <p className="text-sm text-slate-600">
            No account yet?{" "}
            <Link to="/register" className="font-semibold text-brand-lagoon">
              Register
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
