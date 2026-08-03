import { createFileRoute } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { useAssets } from "@/hooks/use-agilegraph";
import { riskColor } from "@/lib/types";
import { RiskBadge } from "@/components/risk-badge";
import { RiskGauge } from "@/components/widgets/risk-gauge";
import { Sparkles, GitBranch, ShieldAlert, Layers, CheckCircle2, AlertCircle } from "lucide-react";
import { useExplainability } from "@/hooks/use-agilegraph";

export const Route = createFileRoute("/_app/explainability")({
  component: Explainability,
  head: () => ({
    meta: [
      { title: "Explainability — AgileGraph" },
      { name: "description", content: "Explainable AI rationale for cryptographic risk scores and PQC recommendations." },
    ],
  }),
});

function Explainability() {
  const { data: assets = [] } = useAssets();
  const asset = assets.filter((a) => a.risk === "critical")[0] ?? assets[0];
  const { data: explainData, isLoading, error } = useExplainability(asset?.id || "");

  if (isLoading || !assets.length || !explainData) return <div className="p-8 text-center text-muted-foreground">Loading explainability data...</div>;

  const { assetInformation: info, gnnExplanation: gnn, heuristicExplanation: heur, migrationRecommendation: mig, naturalLanguageSummary } = explainData;
  const factors = gnn?.featureImportance?.map((f: any) => ({
    label: f.featureName,
    weight: Math.round(f.contribution * 100),
    note: f.positiveInfluence ? "Increases risk" : "Decreases risk"
  })) || [];

  return (
    <>
      <AppTopbar title="Explainability" subtitle="Understand every risk score and recommendation" />
      <main className="p-4 md:p-6 space-y-6">
        <section className="grid gap-6 lg:grid-cols-[380px_1fr]">
          <div className="rounded-xl border bg-card p-6">
            <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Overall Risk Score</div>
            <div className="mt-4 grid place-items-center">
              <RiskGauge value={info?.overallRisk || 0} color={riskColor[(info?.overallRisk >= 80 ? "critical" : info?.overallRisk >= 60 ? "high" : "low") as any] || riskColor.low} />
            </div>
            <div className="mt-4 text-center">
              <div className="text-lg font-semibold">{info?.name}</div>
              <div className="text-xs text-muted-foreground">{info?.assetId} · {info?.algorithm}</div>
            </div>
          </div>

          <div className="rounded-xl border bg-card p-6">
            <div className="flex items-center gap-2"><Sparkles className="h-4 w-4 text-primary" /><h3 className="text-sm font-semibold">Why was this asset ranked high?</h3></div>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
              {naturalLanguageSummary || "AgileGraph's risk model combines intrinsic algorithmic weakness with graph-based exposure and business context to produce this score."}
            </p>
            <div className="mt-5 space-y-3">
              {factors.map((f) => (
                <div key={f.label}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span>{f.label}</span>
                    <span className="text-xs font-semibold tabular-nums text-muted-foreground">+{f.weight}</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-primary to-critical" style={{ width: `${f.weight * 2.5}%` }} />
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">{f.note}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-xl border bg-card p-6">
            <div className="flex items-center gap-2"><Layers className="h-4 w-4 text-primary" /><h3 className="text-sm font-semibold">Graph Influence</h3></div>
            <p className="mt-2 text-xs text-muted-foreground">Direct + transitive downstream dependents.</p>
            <div className="mt-4 grid place-items-center">
              <svg viewBox="0 0 260 180" className="w-full">
                <line x1="130" y1="90" x2="60" y2="40" stroke="var(--color-border)" />
                <line x1="130" y1="90" x2="200" y2="40" stroke="var(--color-border)" />
                <line x1="130" y1="90" x2="40" y2="140" stroke="var(--color-border)" />
                <line x1="130" y1="90" x2="130" y2="160" stroke="var(--color-border)" />
                <line x1="130" y1="90" x2="220" y2="140" stroke="var(--color-border)" />
                {[[60,40,"var(--color-warning)"],[200,40,"var(--color-warning)"],[40,140,"var(--color-chart-5)"],[130,160,"var(--color-success)"],[220,140,"var(--color-warning)"]].map((c, i) => (
                  <circle key={i} cx={c[0] as number} cy={c[1] as number} r={10} fill="white" stroke={c[2] as string} strokeWidth="2.5" />
                ))}
                <circle cx="130" cy="90" r="18" fill="white" stroke="var(--color-critical)" strokeWidth="3" />
                <circle cx="130" cy="90" r="6" fill="var(--color-critical)" />
              </svg>
            </div>
            <div className="mt-2 grid grid-cols-3 gap-2 text-center text-xs">
              <div><div className="text-lg font-semibold">12</div><div className="text-muted-foreground">Direct</div></div>
              <div><div className="text-lg font-semibold">38</div><div className="text-muted-foreground">Transitive</div></div>
              <div><div className="text-lg font-semibold">4</div><div className="text-muted-foreground">Public</div></div>
            </div>
          </div>

          <div className="rounded-xl border bg-card p-6 lg:col-span-2">
            <div className="flex items-center gap-2"><ShieldAlert className="h-4 w-4 text-primary" /><h3 className="text-sm font-semibold">AI Explanation</h3></div>
            <div className="mt-4 space-y-4 text-sm">
              <div className="rounded-lg border-l-4 border-primary bg-primary/5 p-4">
                <div className="text-xs font-semibold uppercase tracking-widest text-primary">Model Confidence: {Math.round((explainData?.confidenceMetrics?.overallConfidence || 0) * 100)}%</div>
                <p className="mt-2 leading-relaxed">
                  Migrate to <span className="font-mono font-semibold">{mig?.recommendedPqcAlgorithm || "Unknown"}</span>.
                  Estimated effort: {mig?.migrationEffort || 0} days. Risk reduction: {mig?.estimatedRiskReduction || 0}%.
                </p>
              </div>
              <div className="rounded-lg border p-4">
                <div className="text-sm font-medium">Reasoning steps</div>
                <ol className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li><span className="mr-2 font-mono text-primary">1.</span> {heur?.breakdown?.riskFormulaBreakdown || "Heuristics computed."}</li>
                  <li><span className="mr-2 font-mono text-primary">2.</span> {heur?.breakdown?.penaltyBreakdown || "Penalties applied."}</li>
                </ol>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-xl border bg-card p-6">
          <div className="flex items-center gap-2"><GitBranch className="h-4 w-4 text-primary" /><h3 className="text-sm font-semibold">Timeline of Reasoning</h3></div>
          <ol className="mt-6 grid gap-6 md:grid-cols-4">
            {[
              { t: "Discovery", d: "Asset detected during monorepo scan", ok: true },
              { t: "Graph analysis", d: "Blast radius computed across 3 tiers", ok: true },
              { t: "Risk scoring", d: "Multi-factor model produced score 92", ok: true },
              { t: "Recommendation", d: `PQC upgrade to ${asset.recommended}`, ok: true },
            ].map((s, i) => (
              <li key={i} className="relative rounded-lg border p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-success" />
                  <div className="text-sm font-semibold">{s.t}</div>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{s.d}</p>
              </li>
            ))}
          </ol>
        </section>
      </main>
    </>
  );
}

