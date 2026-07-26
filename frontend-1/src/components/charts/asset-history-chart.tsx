import React from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";

export const AssetHistoryChart = React.memo(function AssetHistoryChart({ data }: { data: { m: number; v: number }[] }) {
  return (
    <div className="mt-3 h-32">
      <ResponsiveContainer>
        <LineChart data={data}>
          <YAxis hide domain={[0, 100]} />
          <XAxis hide dataKey="m" />
          <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--color-border)", background: "white", fontSize: 12 }} />
          <Line type="monotone" dataKey="v" stroke="var(--color-primary)" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
});
