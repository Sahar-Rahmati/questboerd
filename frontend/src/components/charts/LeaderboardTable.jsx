export default function LeaderboardTable({ rows, scoreKey }) {
  return (
    <div className="panel overflow-hidden">
      <table className="min-w-full divide-y divide-slate-100 text-sm">
        <thead className="bg-brand-mint/50 text-left text-slate-500">
          <tr>
            <th className="px-4 py-3 font-semibold">Rank</th>
            <th className="px-4 py-3 font-semibold">User</th>
            <th className="px-4 py-3 font-semibold">Level</th>
            <th className="px-4 py-3 font-semibold">Score</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row) => (
            <tr key={`${row.user_id}-${row.rank}`}>
              <td className="px-4 py-3 font-semibold text-brand-ink">#{row.rank}</td>
              <td className="px-4 py-3">{row.username}</td>
              <td className="px-4 py-3">{row.level}</td>
              <td className="px-4 py-3 font-semibold text-brand-lagoon">{row[scoreKey]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
