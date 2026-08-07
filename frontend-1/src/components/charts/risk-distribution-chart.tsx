import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

export const RiskDistributionChart = React.memo(function RiskDistributionChart({
  data,
}: {
  data: { name: string; value: number; color: string }[];
}) {
  return (
    <>
      <div className="mt-4 h-64">
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={90}
              paddingAngle={3}
            >
              {data.map((r, i) => (
                <Cell key={i} fill={r.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                borderRadius: 10,
                border: "1px solid var(--color-border)",
                background: "white",
                fontSize: 12,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 grid grid-cols-4 gap-2 text-center text-xs">
        {data.map((r) => (
          <div key={r.name}>
            <div className="flex items-center justify-center gap-1.5">
              <span className="h-2 w-2 rounded-full" style={{ background: r.color }} />
              <span className="text-muted-foreground">{r.name}</span>
            </div>
            <div className="mt-0.5 font-semibold">{r.value}</div>
          </div>
        ))}
      </div>
    </>
  );
});
