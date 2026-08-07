import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

export const DepartmentUsageChart = React.memo(function DepartmentUsageChart({
  data,
}: {
  data: { department: string; assets: number; critical: number }[];
}) {
  return (
    <div className="mt-4 h-64">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid vertical={false} stroke="var(--color-border)" />
          <XAxis dataKey="department" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis fontSize={11} tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{
              borderRadius: 10,
              border: "1px solid var(--color-border)",
              background: "white",
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Bar dataKey="assets" fill="var(--color-chart-1)" radius={[6, 6, 0, 0]} />
          <Bar dataKey="critical" fill="var(--color-critical)" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
});
