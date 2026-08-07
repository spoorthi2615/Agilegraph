export function RiskGauge({ value, color }: { value: number; color: string }) {
  const r = 70;
  const c = 2 * Math.PI * r;
  const off = c - (value / 100) * c;
  return (
    <svg
      viewBox="0 0 180 180"
      className="h-40 w-40 -rotate-90"
      role="img"
      aria-label={`Risk score: ${value} out of 100`}
    >
      <circle cx="90" cy="90" r={r} stroke="var(--color-muted)" strokeWidth="14" fill="none" />
      <circle
        cx="90"
        cy="90"
        r={r}
        stroke={color}
        strokeWidth="14"
        strokeLinecap="round"
        fill="none"
        strokeDasharray={c}
        strokeDashoffset={off}
        style={{ transition: "stroke-dashoffset 800ms cubic-bezier(0.4,0,0.2,1)" }}
      />
      <text
        x="90"
        y="95"
        textAnchor="middle"
        fontSize="34"
        fontWeight="600"
        fill="var(--color-foreground)"
        transform="rotate(90 90 90)"
      >
        {value}
      </text>
    </svg>
  );
}
