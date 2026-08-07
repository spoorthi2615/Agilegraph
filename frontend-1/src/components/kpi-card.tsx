import type { LucideIcon } from "lucide-react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { AnimatedNumber } from "./animated-number";
import { cn } from "@/lib/utils";

export function KpiCard({
  label,
  value,
  suffix,
  delta,
  icon: Icon,
  tint = "primary",
  hint,
}: {
  label: string;
  value: number;
  suffix?: string;
  delta?: number;
  icon: LucideIcon;
  tint?: "primary" | "success" | "warning" | "critical" | "muted";
  hint?: string;
}) {
  const tints: Record<string, string> = {
    primary: "bg-primary/10 text-primary",
    success: "bg-success/10 text-success",
    warning: "bg-warning/10 text-warning",
    critical: "bg-critical/10 text-critical",
    muted: "bg-muted text-muted-foreground",
  };
  const positive = (delta ?? 0) >= 0;
  return (
    <div className="card-hover animate-fade-up rounded-xl border bg-card p-5 shadow-[var(--shadow-soft)]">
      <div className="flex items-start justify-between">
        <div className={cn("grid h-10 w-10 place-items-center rounded-lg", tints[tint])}>
          <Icon className="h-5 w-5" />
        </div>
        {typeof delta === "number" && (
          <span
            className={cn(
              "inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium",
              positive ? "bg-success/10 text-success" : "bg-critical/10 text-critical",
            )}
          >
            {positive ? (
              <ArrowUpRight className="h-3 w-3" />
            ) : (
              <ArrowDownRight className="h-3 w-3" />
            )}
            {Math.abs(delta)}%
          </span>
        )}
      </div>
      <div className="mt-4 text-sm text-muted-foreground">{label}</div>
      <div className="mt-1 text-3xl font-semibold tracking-tight text-foreground">
        <AnimatedNumber value={value} suffix={suffix} />
      </div>
      {hint && <div className="mt-1 text-xs text-muted-foreground">{hint}</div>}
    </div>
  );
}
