import React from "react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export const MigrationTrendChart = React.memo(function MigrationTrendChart({ data }: { data: { month: string; migrated: number; planned: number }[] }) {
  return (
    <div className="mt-4 h-64">
      <ResponsiveContainer>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="mig" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="pl" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--color-chart-5)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="var(--color-chart-5)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke="var(--color-border)" />
          <XAxis dataKey="month" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis fontSize={11} tickLine={false} axisLine={false} />
          <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--color-border)", background: "white", fontSize: 12 }} />
          <Area type="monotone" dataKey="planned" stroke="var(--color-chart-5)" fill="url(#pl)" strokeWidth={2} />
          <Area type="monotone" dataKey="migrated" stroke="var(--color-primary)" fill="url(#mig)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
});
