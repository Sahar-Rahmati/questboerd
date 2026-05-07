import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="panel sticky top-4 z-20 flex items-center justify-between px-5 py-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-lagoon">Questboard</p>
        <h1 className="text-xl font-bold text-brand-ink">Productivity, leveled up</h1>
      </div>
      <div className="flex items-center gap-3">
        <div className="rounded-2xl bg-brand-mint px-4 py-2 text-right">
          <p className="text-sm font-semibold text-brand-ink">{user?.username}</p>
          <p className="text-xs text-slate-600">Level {user?.level}</p>
        </div>
        <button
          type="button"
          onClick={async () => {
            await logout();
            navigate("/login");
          }}
          className="rounded-2xl bg-brand-ink px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-lagoon"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
