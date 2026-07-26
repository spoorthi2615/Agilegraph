import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/lib/types";

const styles: Record<RiskLevel, string> = {
  critical: "bg-critical/10 text-critical ring-critical/20",
  high: "bg-warning/10 text-warning ring-warning/20",
  medium: "bg-[color-mix(in_oklab,var(--color-chart-5)_12%,transparent)] text-[var(--color-chart-5)] ring-[color-mix(in_oklab,var(--color-chart-5)_25%,transparent)]",
  low: "bg-success/10 text-success ring-success/20",
};
const labels: Record<RiskLevel, string> = {
  critical: "Critical", high: "High", medium: "Medium", low: "Low",
};

export function RiskBadge({ risk, className }: { risk: RiskLevel; className?: string }) {
  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
      styles[risk], className,
    )}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {labels[risk]}
    </span>
  );
}
