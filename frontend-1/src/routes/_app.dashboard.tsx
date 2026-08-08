import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { AppTopbar } from "@/components/app-topbar";
import { KpiCard } from "@/components/kpi-card";
import { RiskBadge } from "@/components/risk-badge";
import {
  Boxes,
  ShieldAlert,
  ShieldCheck,
  Activity,
  TrendingUp,
  GaugeCircle,
  Clock,
  AlertTriangle,
  ArrowUpRight,
} from "lucide-react";
import { RiskDistributionChart } from "@/components/charts/risk-distribution-chart";
import { AlgorithmUsageChart } from "@/components/charts/algorithm-usage-chart";
import { DepartmentUsageChart } from "@/components/charts/department-usage-chart";
import { MigrationTrendChart } from "@/components/charts/migration-trend-chart";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorBoundary } from "@/components/error-boundary";
import { useDashboardSummary } from "@/hooks/use-agilegraph";
import { SectionHead } from "@/components/ui/section-head";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_app/dashboard")({
  component: DashboardWithBoundary,
  head: () => ({
    meta: [
      { title: "Dashboard — AgileGraph" },
      {
        name: "description",
        content:
          "Executive dashboard of cryptographic posture, risk distribution, and PQC migration progress.",
      },
    ],
  }),
});

const chartColors = [
  "var(--color-chart-1)",
  "var(--color-chart-2)",
  "var(--color-chart-3)",
  "var(--color-chart-4)",
  "var(--color-chart-5)",
];

function DashboardWithBoundary() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  );
}

function Dashboard() {
  const { data, isLoading, error, refetch } = useDashboardSummary();
  const [showProgress, setShowProgress] = useState(true);
  const [defaultView, setDefaultView] = useState("exec");

  useEffect(() => {
    setShowProgress(localStorage.getItem("showProgress") !== "false");
    setDefaultView(localStorage.getItem("defaultView") || "exec");
  }, []);

  if (isLoading)
    return (
      <div className="p-4 md:p-6 space-y-6">
        <Skeleton className="h-10 w-64 mb-6" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4">
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <Skeleton className="h-80 w-full rounded-xl" />
          <Skeleton className="h-80 w-full rounded-xl lg:col-span-2" />
        </div>
      </div>
    );
  if (error || !data)
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center p-8 text-center">
        <div className="text-critical mb-4">Failed to load dashboard data.</div>
        <Button onClick={() => refetch()} variant="outline">
          Retry
        </Button>
      </div>
    );

  const {
    kpis,
    riskDistribution,
    algorithmUsage,
    departmentUsage,
    migrationTrend,
    activity,
    criticalAlerts,
  } = data;

  const viewTitle =
    defaultView === "eng"
      ? "Engineering View"
      : defaultView === "compliance"
        ? "Compliance View"
        : "Executive View";

  return (
    <>
      <AppTopbar
        title="Dashboard"
        subtitle={`${viewTitle} — Acme Bank, Production`}
        actions={
          <Button asChild size="sm">
            <Link to="/scan">New Scan</Link>
          </Button>
        }
      />
      <main className="p-4 md:p-6 space-y-6">
        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4">
          <KpiCard
            label="Total Cryptographic Assets"
            value={kpis.totalAssets}
            icon={Boxes}
            tint="primary"
            delta={8}
            hint="+8% vs last scan"
          />
          <KpiCard
            label="High Risk Assets"
            value={kpis.critical + kpis.high}
            icon={ShieldAlert}
            tint="critical"
            delta={-4}
            hint={`${kpis.critical} critical · ${kpis.high} high`}
          />
          {showProgress && (
            <KpiCard
              label="Migration Progress"
              value={kpis.migrationProgress}
              suffix="%"
              icon={TrendingUp}
              tint="success"
              delta={kpis.migrationProgress > 0 ? 12 : 0}
              hint={kpis.migrationProgress > 0 ? "On track for Q2 target" : "Awaiting scans"}
            />
          )}
          <KpiCard
            label="PQC Readiness Score"
            value={kpis.pqcReadiness}
            suffix="/100"
            icon={GaugeCircle}
            tint="primary"
            delta={kpis.pqcReadiness > 0 ? 5 : 0}
            hint={kpis.pqcReadiness > 0 ? "NIST FIPS 203/204/205" : "Awaiting scans"}
          />
        </section>

        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Medium Risk" value={kpis.medium} icon={ShieldCheck} tint="warning" />
          <KpiCard label="Low Risk" value={kpis.low} icon={ShieldCheck} tint="success" />
          <KpiCard
            label="Last Scan"
            value={kpis.lastScan === "No scans yet" ? "-" : kpis.lastScan}
            suffix=""
            icon={Clock}
            tint="muted"
            hint={kpis.lastScan === "No scans yet" ? "Awaiting first scan" : "core-banking-monorepo"}
          />
          <KpiCard
            label="Active Migrations"
            value={kpis.activeMigrations || 0}
            icon={Activity}
            tint="primary"
            hint={kpis.activeMigrations > 0 ? "3 completing this week" : "None active"}
          />
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border bg-card p-5">
            <SectionHead title="Risk Distribution" hint="Across all discovered assets" />
            <RiskDistributionChart data={riskDistribution} />
          </div>

          <div className="rounded-xl border bg-card p-5 lg:col-span-2">
            <SectionHead title="Algorithm Usage" hint="Assets grouped by current algorithm" />
            <AlgorithmUsageChart data={algorithmUsage} />
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border bg-card p-5">
            <SectionHead title="Assets by Department" hint="Total vs. critical exposure" />
            <DepartmentUsageChart data={departmentUsage} />
          </div>

          {showProgress && (
            <div className="rounded-xl border bg-card p-5">
              <SectionHead
                title="Migration Progress"
                hint="Migrated vs. planned assets per month"
              />
              <MigrationTrendChart data={migrationTrend} />
            </div>
          )}
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border bg-card p-5 lg:col-span-2">
            <SectionHead title="Recent Activity" hint="Team and AI actions across your workspace" />
            <ul className="mt-4 divide-y">
              {activity.map((a) => (
                <li key={a.id} className="flex items-center gap-4 py-3">
                  <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                    {a.actor
                      .split(" ")
                      .map((s) => s[0])
                      .slice(0, 2)
                      .join("")}
                  </div>
                  <div className="min-w-0 flex-1 text-sm">
                    <span className="font-medium">{a.actor}</span>{" "}
                    <span className="text-muted-foreground">{a.action}</span>{" "}
                    <span className="font-medium">{a.target}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{a.time}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-xl border bg-card p-5">
            <SectionHead title="Critical Alerts" hint="Requires attention" />
            <ul className="mt-4 space-y-3">
              {criticalAlerts.map((a) => (
                <li key={a.id} className="rounded-lg border bg-critical/5 p-3">
                  <div className="flex items-start gap-3">
                    <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-critical/10 text-critical">
                      <AlertTriangle className="h-4 w-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <div className="truncate text-sm font-medium">{a.title}</div>
                        <RiskBadge risk="critical" />
                      </div>
                      <div className="mt-0.5 text-xs text-muted-foreground">{a.reason}</div>
                      <div className="flex items-center justify-between gap-2 mt-2">
                        <Link
                          to="/assets/$id"
                          params={{ id: a.id }}
                          className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
                        >
                          View asset <ArrowUpRight className="h-3 w-3" />
                        </Link>
                        {a.ownerEmail && (
                          <div className="text-[10px] text-muted-foreground bg-muted/30 px-1.5 py-0.5 rounded border">
                            {a.ownerEmail}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
    </>
  );
}
