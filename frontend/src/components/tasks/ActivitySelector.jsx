export default function ActivitySelector({ activities, value, onChange }) {
  return (
    <label className="grid gap-2 text-sm font-medium text-brand-ink">
      Activity
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none ring-brand-lagoon focus:ring-2"
      >
        <option value="">Select an activity</option>
        {activities.map((activity) => (
          <option key={activity.id} value={activity.id}>
            {activity.title} ({activity.category})
          </option>
        ))}
      </select>
    </label>
  );
}
