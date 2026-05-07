import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const colors = ["#1C6E72", "#E76F51", "#D8A31A", "#84A59D", "#6B7280", "#132A2E"];

export default function CategoryBreakdownChart({ data }) {
  return (
    <div className="panel h-[320px] p-5">
      <h3 className="panel-title">Category Breakdown</h3>
      <div className="mt-4 h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="count" nameKey="category" outerRadius={90}>
              {data.map((entry, index) => (
                <Cell key={entry.category} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
