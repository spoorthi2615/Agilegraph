import { createFileRoute } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { Slider } from "@/components/ui/slider";
import { useState } from "react";
import { Info, ShieldCheck } from "lucide-react";
import { useMoscaReadiness } from "@/hooks/use-agilegraph";

export const Route = createFileRoute("/_app/mosca")({
  component: Mosca,
  head: () => ({
    meta: [
      { title: "Mosca Readiness — AgileGraph" },
      { name: "description", content: "Assess PQC readiness using Mosca's inequality across your critical assets." },
    ],
  }),
});

function Mosca() {
  const [z, setZ] = useState(8);

  const { data: moscaData, isLoading } = useMoscaReadiness(z);

  const x = moscaData?.x ?? 0;
  const y = moscaData?.y ?? 0;
  const surplus = moscaData?.surplus ?? 0;
  const readiness = moscaData?.readiness_score ?? 100;
  const hasData = moscaData?.has_data ?? false;

  const status =
    surplus < 0 ? { label: "At risk — migrate now", color: "var(--color-critical)" } :
    surplus < 2 ? { label: "Tight — start immediately", color: "var(--color-warning)" } :
    { label: "On track", color: "var(--color-success)" };

  return (
    <>
      <AppTopbar title="Mosca Readiness" subtitle="Assess your quantum migration timeline" />
      <main className="p-4 md:p-6 space-y-6">
        {isLoading ? (
          <div className="flex h-[400px] flex-col items-center justify-center rounded-xl border text-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            <h3 className="mt-4 text-sm font-medium text-muted-foreground">Computing readiness...</h3>
          </div>
        ) : !hasData ? (
          <div className="flex h-[400px] flex-col items-center justify-center rounded-xl border border-dashed text-center">
            <ShieldCheck className="mx-auto mb-2 h-10 w-10 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No data available</h3>
            <p className="mt-2 text-sm text-muted-foreground">Upload and scan a repository to compute your Mosca readiness score.</p>
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[1fr_400px]">
            <div className="space-y-4">
              <div className="rounded-xl border bg-card p-6">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  Mosca's Inequality
                  <span className="rounded-md bg-muted px-2 py-0.5 font-mono text-xs text-muted-foreground">X + Y &gt; Z</span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  If confidentiality lifetime (X) plus migration duration (Y) exceeds quantum horizon (Z), your data is at risk.
                </p>

                <div className="mt-8 space-y-8">
                  <SliderInput label="Quantum Horizon (Z)" hint="Estimated years until a CRQC exists" value={z} onChange={setZ} max={30} suffix="years" tint="var(--color-warning)" />
                  
                  <div className="rounded-md border p-4 bg-muted/20">
                    <div className="text-sm font-medium">Computed Baseline Values</div>
                    <div className="mt-2 text-xs text-muted-foreground">Derived from actual repository analysis in Neo4j.</div>
                    <div className="mt-4 grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-xs font-semibold">Data Confidentiality Lifetime (X)</div>
                        <div className="text-lg font-mono">{x} yrs</div>
                      </div>
                      <div>
                        <div className="text-xs font-semibold">Migration Duration (Y)</div>
                        <div className="text-lg font-mono">{y} yrs</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-8 rounded-lg border bg-muted/30 p-5">
                  <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Formula</div>
                  <div className="mt-2 flex flex-wrap items-baseline gap-3 font-mono text-lg">
                    <span>X ({x})</span><span className="text-muted-foreground">+</span>
                    <span>Y ({y})</span><span className="text-muted-foreground">=</span>
                    <span className="font-semibold">{x + y}</span>
                    <span className="text-muted-foreground">vs</span>
                    <span>Z ({z})</span>
                  </div>
                  <div className="mt-3 text-sm">
                    Surplus: <span className="font-semibold" style={{ color: status.color }}>{surplus > 0 ? `+${surplus}` : surplus} years</span> · <span style={{ color: status.color }}>{status.label}</span>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border bg-card p-6">
                <div className="flex items-center gap-2 text-sm font-semibold"><ShieldCheck className="h-4 w-4 text-primary" /> Recommendations</div>
                <ul className="mt-4 space-y-3 text-sm">
                  {[
                    "Prioritize hybrid cipher deployment on public-facing TLS endpoints",
                    "Freeze new usage of RSA-2048 and ECC-P256 in greenfield services",
                    "Establish PQC-ready key management (ML-KEM-768, ML-DSA-65)",
                    "Publish executive risk briefing quarterly to the board",
                    "Pilot post-quantum VPN concentrator in Q2",
                  ].map((r) => (
                    <li key={r} className="flex items-start gap-3 rounded-lg border p-3">
                      <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-semibold text-primary">✓</span>
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <aside className="space-y-4">
              <div className="rounded-xl border bg-card p-6 text-center">
                <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Readiness Score</div>
                <div className="mt-4 grid place-items-center">
                  <Gauge value={readiness} color={status.color} />
                </div>
                <div className="mt-2 text-sm font-medium" style={{ color: status.color }}>{status.label}</div>
              </div>

              <div className="rounded-xl border bg-card p-6">
                <div className="text-sm font-semibold">Timeline</div>
                <div className="mt-4 space-y-3">
                  <Bar label="Data must stay secret" years={x} color="var(--color-primary)" max={Math.max(x + y, z, 15)} />
                  <Bar label="Migration duration" years={y} color="var(--color-chart-5)" max={Math.max(x + y, z, 15)} />
                  <div className="border-t pt-3">
                    <Bar label="Quantum horizon (Z)" years={z} color="var(--color-warning)" max={Math.max(x + y, z, 15)} />
                  </div>
                </div>
                <p className="mt-4 flex items-start gap-2 text-xs text-muted-foreground">
                  <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                  Based on Michele Mosca's inequality (2015). Adjust inputs to model different scenarios.
                </p>
              </div>
            </aside>
          </div>
        )}
      </main>
    </>
  );
}

function SliderInput({ label, hint, value, onChange, max, suffix, tint }: {
  label: string; hint: string; value: number; onChange: (v: number) => void; max: number; suffix: string; tint: string;
}) {
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <div>
          <div className="text-sm font-medium">{label}</div>
          <div className="text-xs text-muted-foreground">{hint}</div>
        </div>
        <div className="text-2xl font-semibold tabular-nums" style={{ color: tint }}>{value} <span className="text-xs text-muted-foreground">{suffix}</span></div>
      </div>
      <Slider value={[value]} min={0} max={max} step={1} onValueChange={(v) => onChange(v[0])} className="mt-3" />
    </div>
  );
}

function Gauge({ value, color }: { value: number; color: string }) {
  const r = 80;
  const c = 2 * Math.PI * r;
  const off = c - (value / 100) * c;
  return (
    <svg viewBox="0 0 200 200" className="h-48 w-48 -rotate-90">
      <circle cx="100" cy="100" r={r} stroke="var(--color-muted)" strokeWidth="16" fill="none" />
      <circle cx="100" cy="100" r={r} stroke={color} strokeWidth="16" strokeLinecap="round" fill="none" strokeDasharray={c} strokeDashoffset={off} style={{ transition: "stroke-dashoffset 700ms cubic-bezier(0.4,0,0.2,1)" }} />
      <text x="100" y="102" textAnchor="middle" fontSize="42" fontWeight="600" fill="var(--color-foreground)" transform="rotate(90 100 100)">{value}</text>
      <text x="100" y="128" textAnchor="middle" fontSize="12" fill="var(--color-muted-foreground)" transform="rotate(90 100 100)">/ 100</text>
    </svg>
  );
}

function Bar({ label, years, color, max }: { label: string; years: number; color: string; max: number }) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs"><span className="text-muted-foreground">{label}</span><span className="font-medium">{years}y</span></div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${(years / max) * 100}%`, background: color }} />
      </div>
    </div>
  );
}
