import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function WeeklyReportChart({ data }) {
  return (
    <div className="panel h-[320px] p-5">
      <h3 className="panel-title">Daily XP</h3>
      <div className="mt-4 h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="xpFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#1C6E72" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#1C6E72" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="xp" stroke="#1C6E72" fill="url(#xpFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
