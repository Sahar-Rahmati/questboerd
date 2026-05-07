const styles = {
  easy: "bg-emerald-100 text-emerald-700",
  medium: "bg-sky-100 text-sky-700",
  hard: "bg-orange-100 text-orange-700",
  extreme: "bg-rose-100 text-rose-700",
};

export default function DifficultyBadge({ difficulty = "easy" }) {
  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${styles[difficulty] || styles.easy}`}>{difficulty}</span>;
}
