import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/rewards", label: "Rewards" },
  { to: "/leaderboard", label: "Leaderboard" },
  { to: "/reports", label: "Weekly Reports" },
  { to: "/profile", label: "Profile" },
];

export default function Sidebar() {
  return (
    <aside className="panel h-fit p-4">
      <div className="rounded-3xl bg-brand-ink px-4 py-5 text-white">
        <p className="text-xs uppercase tracking-[0.3em] text-brand-mint">Questboard</p>
        <h2 className="mt-2 text-xl font-bold">Track sessions. Earn XP. Keep leveling up.</h2>
      </div>
      <nav className="mt-4 grid gap-2">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === "/"}
            className={({ isActive }) =>
              `rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                isActive ? "bg-brand-lagoon text-white" : "text-slate-600 hover:bg-brand-mint/60 hover:text-brand-ink"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
