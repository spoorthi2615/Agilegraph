import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export const AlgorithmUsageChart = React.memo(function AlgorithmUsageChart({ data }: { data: { algorithm: string; count: number }[] }) {
  return (
    <div className="mt-4 h-64">
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid horizontal={false} stroke="var(--color-border)" />
          <XAxis type="number" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis dataKey="algorithm" type="category" fontSize={11} tickLine={false} axisLine={false} width={90} />
          <Tooltip cursor={{ fill: "var(--color-muted)" }} contentStyle={{ borderRadius: 10, border: "1px solid var(--color-border)", background: "white", fontSize: 12 }} />
          <Bar dataKey="count" fill="var(--color-primary)" radius={[0, 6, 6, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
});
