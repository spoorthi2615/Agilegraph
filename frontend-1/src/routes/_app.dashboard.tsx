import { createFileRoute, Link } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { KpiCard } from "@/components/kpi-card";
import { RiskBadge } from "@/components/risk-badge";
import {
  Boxes, ShieldAlert, ShieldCheck, Activity, TrendingUp, GaugeCircle, Clock,
  AlertTriangle, ArrowUpRight,
} from "lucide-react";
import {
  ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip,
  AreaChart, Area, CartesianGrid, Legend,
} from "recharts";
import {
  kpis, riskDistribution, algorithmUsage, departmentUsage, migrationTrend,
  activity, criticalAlerts,
} from "@/lib/mock-data";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_app/dashboard")({
  component: Dashboard,
  head: () => ({
    meta: [
      { title: "Dashboard — AgileGraph" },
      { name: "description", content: "Executive dashboard of cryptographic posture, risk distribution, and PQC migration progress." },
    ],
  }),
});

const chartColors = ["var(--color-chart-1)", "var(--color-chart-2)", "var(--color-chart-3)", "var(--color-chart-4)", "var(--color-chart-5)"];

function Dashboard() {
  return (
    <>
      <AppTopbar
        title="Dashboard"
        subtitle="Cryptographic posture — Acme Bank, Production"
        actions={<Button asChild size="sm"><Link to="/scan">New Scan</Link></Button>}
      />
      <main className="p-4 md:p-6 space-y-6">
        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4">
          <KpiCard label="Total Cryptographic Assets" value={kpis.totalAssets} icon={Boxes} tint="primary" delta={8} hint="+8% vs last scan" />
          <KpiCard label="High Risk Assets" value={kpis.critical + kpis.high} icon={ShieldAlert} tint="critical" delta={-4} hint={`${kpis.critical} critical · ${kpis.high} high`} />
          <KpiCard label="Migration Progress" value={kpis.migrationProgress} suffix="%" icon={TrendingUp} tint="success" delta={12} hint="On track for Q2 target" />
          <KpiCard label="PQC Readiness Score" value={kpis.pqcReadiness} suffix="/100" icon={GaugeCircle} tint="primary" delta={5} hint="NIST FIPS 203/204/205" />
        </section>

        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Medium Risk" value={kpis.medium} icon={ShieldCheck} tint="warning" />
          <KpiCard label="Low Risk" value={kpis.low} icon={ShieldCheck} tint="success" />
          <KpiCard label="Last Scan" value={2} suffix="h" icon={Clock} tint="muted" hint="core-banking-monorepo" />
          <KpiCard label="Active Migrations" value={9} icon={Activity} tint="primary" hint="3 completing this week" />
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border bg-card p-5">
            <SectionHead title="Risk Distribution" hint="Across all discovered assets" />
            <div className="mt-4 h-64">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={riskDistribution} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={3}>
                    {riskDistribution.map((r, i) => <Cell key={i} fill={r.color} />)}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--color-border)", background: "white", fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 grid grid-cols-4 gap-2 text-center text-xs">
              {riskDistribution.map((r) => (
                <div key={r.name}>
                  <div className="flex items-center justify-center gap-1.5">
                    <span className="h-2 w-2 rounded-full" style={{ background: r.color }} />
                    <span className="text-muted-foreground">{r.name}</span>
                  </div>
                  <div className="mt-0.5 font-semibold">{r.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border bg-card p-5 lg:col-span-2">
            <SectionHead title="Algorithm Usage" hint="Assets grouped by current algorithm" />
            <div className="mt-4 h-64">
              <ResponsiveContainer>
                <BarChart data={algorithmUsage} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid horizontal={false} stroke="var(--color-border)" />
                  <XAxis type="number" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis dataKey="algorithm" type="category" fontSize={11} tickLine={false} axisLine={false} width={90} />
                  <Tooltip cursor={{ fill: "var(--color-muted)" }} contentStyle={{ borderRadius: 10, border: "1px solid var(--color-border)", background: "white", fontSize: 12 }} />
                  <Bar dataKey="count" fill="var(--color-primary)" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border bg-card p-5">
            <SectionHead title="Assets by Department" hint="Total vs. critical exposure" />
            <div className="mt-4 h-64">
              <ResponsiveContainer>
                <BarChart data={departmentUsage}>
                  <CartesianGrid vertical={false} stroke="var(--color-border)" />
                  <XAxis dataKey="department" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--color-border)", background: "white", fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="assets" fill="var(--color-chart-1)" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="critical" fill="var(--color-critical)" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-xl border bg-card p-5">
            <SectionHead title="Migration Progress" hint="Migrated vs. planned assets per month" />
            <div className="mt-4 h-64">
              <ResponsiveContainer>
                <AreaChart data={migrationTrend}>
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
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border bg-card p-5 lg:col-span-2">
            <SectionHead title="Recent Activity" hint="Team and AI actions across your workspace" />
            <ul className="mt-4 divide-y">
              {activity.map((a) => (
                <li key={a.id} className="flex items-center gap-4 py-3">
                  <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                    {a.actor.split(" ").map((s) => s[0]).slice(0, 2).join("")}
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
                      <Link to="/assets/$id" params={{ id: a.id }} className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline">
                        View asset <ArrowUpRight className="h-3 w-3" />
                      </Link>
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

function SectionHead({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex items-start justify-between">
      <div>
        <h3 className="text-sm font-semibold">{title}</h3>
        {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
      </div>
    </div>
  );
}
