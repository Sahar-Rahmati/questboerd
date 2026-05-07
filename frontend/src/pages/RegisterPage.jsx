import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import ErrorMessage from "../components/common/ErrorMessage";
import { useAuth } from "../hooks/useAuth";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const getErrorMessage = (err) => {
    const data = err.response?.data;

    if (!data) {
      return "Cannot reach the server. Make sure the backend is running on http://localhost:8000.";
    }

    return (
      data.email?.[0] ||
      data.username?.[0] ||
      data.password?.[0] ||
      data.detail ||
      data.non_field_errors?.[0] ||
      "Unable to register."
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register(form);
      navigate("/");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <form onSubmit={handleSubmit} className="panel w-full max-w-2xl space-y-5 p-10">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-brand-ember">New Player</p>
          <h1 className="mt-3 text-4xl font-extrabold text-brand-ink">Create your productivity account</h1>
        </div>
        {error && <ErrorMessage message={error} />}
        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2 text-sm font-medium text-brand-ink">
            First name
            <input className="rounded-2xl border border-slate-200 px-4 py-3" value={form.first_name} onChange={(e) => setForm((c) => ({ ...c, first_name: e.target.value }))} />
          </label>
          <label className="grid gap-2 text-sm font-medium text-brand-ink">
            Last name
            <input className="rounded-2xl border border-slate-200 px-4 py-3" value={form.last_name} onChange={(e) => setForm((c) => ({ ...c, last_name: e.target.value }))} />
          </label>
        </div>
        <label className="grid gap-2 text-sm font-medium text-brand-ink">
          Username
          <input className="rounded-2xl border border-slate-200 px-4 py-3" value={form.username} onChange={(e) => setForm((c) => ({ ...c, username: e.target.value }))} required />
        </label>
        <label className="grid gap-2 text-sm font-medium text-brand-ink">
          Email
          <input type="email" className="rounded-2xl border border-slate-200 px-4 py-3" value={form.email} onChange={(e) => setForm((c) => ({ ...c, email: e.target.value }))} required />
        </label>
        <label className="grid gap-2 text-sm font-medium text-brand-ink">
          Password
          <input type="password" className="rounded-2xl border border-slate-200 px-4 py-3" value={form.password} onChange={(e) => setForm((c) => ({ ...c, password: e.target.value }))} required />
        </label>
        <button className="w-full rounded-2xl bg-brand-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-lagoon">
          {loading ? "Creating account..." : "Register"}
        </button>
        <p className="text-sm text-slate-600">
          Already registered?{" "}
          <Link to="/login" className="font-semibold text-brand-lagoon">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}
