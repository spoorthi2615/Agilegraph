import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { assets, riskColor } from "@/lib/mock-data";
import { RiskBadge } from "@/components/risk-badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, Share2, GitBranch } from "lucide-react";
import { ResponsiveContainer, LineChart, Line, YAxis, XAxis, Tooltip } from "recharts";

export const Route = createFileRoute("/_app/assets/$id")({
  loader: ({ params }) => {
    const asset = assets.find((a) => a.id === params.id);
    if (!asset) throw notFound();
    return { asset };
  },
  component: AssetDetail,
  head: ({ loaderData }) => ({
    meta: [
      { title: loaderData ? `${loaderData.asset.name} — AgileGraph` : "Asset — AgileGraph" },
      { name: "description", content: loaderData ? `Risk breakdown, dependencies, and PQC migration plan for ${loaderData.asset.name}.` : "Asset details" },
    ],
  }),
  notFoundComponent: () => (
    <div className="p-10 text-center text-muted-foreground">Asset not found. <Link to="/rankings" className="text-primary hover:underline">Back to rankings</Link></div>
  ),
});

function AssetDetail() {
  const data = Route.useLoaderData() as { asset: import("@/lib/mock-data").CryptoAsset };
  const asset = data.asset;
  const trend = Array.from({ length: 12 }).map((_, i) => ({ m: i, v: Math.max(20, asset.riskScore - Math.sin(i / 2) * 10 - i * 0.6) }));

  return (
    <>
      <AppTopbar title={asset.name} subtitle={`${asset.id} · ${asset.location}`}
        actions={<>
          <Button variant="outline" size="sm"><Share2 className="h-4 w-4" />Share</Button>
          <Button size="sm"><Download className="h-4 w-4" />Export</Button>
        </>} />
      <main className="p-4 md:p-6 space-y-6">
        <Link to="/rankings" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"><ArrowLeft className="h-3.5 w-3.5" /> Back to rankings</Link>

        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <div className="space-y-6">
            <div className="rounded-xl border bg-card p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Badge variant="secondary" className="capitalize">{asset.type}</Badge>
                    <span>·</span><span>{asset.department}</span>
                  </div>
                  <h2 className="mt-2 text-2xl font-semibold tracking-tight">{asset.name}</h2>
                  <p className="mt-2 max-w-xl text-sm text-muted-foreground">{asset.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-xs text-muted-foreground">Risk Score</div>
                  <div className="mt-1 text-4xl font-semibold tracking-tight" style={{ color: riskColor[asset.risk] }}>{asset.riskScore}</div>
                  <RiskBadge risk={asset.risk} className="mt-2" />
                </div>
              </div>
            </div>

            <Tabs defaultValue="overview">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="technical">Technical</TabsTrigger>
                <TabsTrigger value="dependencies">Dependencies</TabsTrigger>
                <TabsTrigger value="connected">Connected</TabsTrigger>
                <TabsTrigger value="risk">Risk</TabsTrigger>
                <TabsTrigger value="migration">Migration</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="mt-4 rounded-xl border bg-card p-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <Info label="Current Algorithm" value={<code className="rounded bg-muted px-1.5 py-0.5">{asset.algorithm}</code>} />
                  <Info label="Recommended PQC" value={<code className="rounded bg-primary/10 px-1.5 py-0.5 text-primary">{asset.recommended}</code>} />
                  <Info label="Key Size" value={asset.keySize} />
                  <Info label="Discovered" value={new Date(asset.discoveredAt).toLocaleDateString()} />
                  <Info label="Location" value={<code className="text-xs">{asset.location}</code>} />
                  <Info label="Migration Effort" value={`${asset.migrationDays} days`} />
                </div>
              </TabsContent>

              <TabsContent value="technical" className="mt-4 rounded-xl border bg-card p-6 space-y-4">
                <div className="rounded-lg bg-[oklch(0.98_0.006_260)] p-4 font-mono text-xs">
                  <div className="text-muted-foreground">// Detected usage</div>
                  <div>{asset.algorithm} → {asset.recommended}</div>
                  <div className="mt-2 text-muted-foreground">// Cryptographic operations</div>
                  <div>- Key exchange: 42 call sites</div>
                  <div>- Signature verification: 18 call sites</div>
                  <div>- Bulk encryption: fallback to AES-256-GCM</div>
                </div>
                <p className="text-sm text-muted-foreground">Algorithm strength is currently classified as <span className="font-medium text-foreground">quantum-vulnerable</span> under CNSA 2.0. Migration is recommended before {new Date(Date.now() + asset.migrationDays * 86400000).toLocaleDateString()}.</p>
              </TabsContent>

              <TabsContent value="dependencies" className="mt-4 rounded-xl border bg-card p-6">
                <ul className="divide-y">
                  {["openssl-1.0.2", "bouncycastle-1.68", "libcrypto.so.1.1", "openjdk-8-crypto"].map((d) => (
                    <li key={d} className="flex items-center justify-between py-3 text-sm">
                      <div className="flex items-center gap-2"><GitBranch className="h-3.5 w-3.5 text-muted-foreground" />{d}</div>
                      <Badge variant="outline">Transitive</Badge>
                    </li>
                  ))}
                </ul>
              </TabsContent>

              <TabsContent value="connected" className="mt-4 rounded-xl border bg-card p-6">
                <ul className="space-y-2">
                  {asset.connections.map((c: string) => {
                    const a = assets.find((x) => x.id === c);
                    if (!a) return null;
                    return (
                      <li key={c}>
                        <Link to="/assets/$id" params={{ id: c }} className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/30">
                          <span className="h-2 w-2 rounded-full" style={{ background: riskColor[a.risk] }} />
                          <div className="min-w-0 flex-1">
                            <div className="truncate text-sm font-medium">{a.name}</div>
                            <div className="text-xs text-muted-foreground">{a.algorithm}</div>
                          </div>
                          <RiskBadge risk={a.risk} />
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </TabsContent>

              <TabsContent value="risk" className="mt-4 rounded-xl border bg-card p-6 space-y-4">
                {[
                  ["Algorithm vulnerability", 90, "Shor's algorithm breaks RSA/ECC in polynomial time on a CRQC."],
                  ["Exposure surface", 72, "Reachable from public API gateway with default cipher suite."],
                  ["Business criticality", 85, "Processes payment authorizations for Tier-1 systems."],
                  ["Data lifetime", 68, "Signed artifacts must remain verifiable for 10+ years."],
                ].map(([l, v, hint]) => (
                  <div key={l as string}>
                    <div className="mb-1 flex items-center justify-between text-sm"><span>{l}</span><span className="font-semibold">{v}</span></div>
                    <div className="h-2 rounded-full bg-muted"><div className="h-full rounded-full bg-gradient-to-r from-primary to-critical" style={{ width: `${v}%` }} /></div>
                    <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="migration" className="mt-4 rounded-xl border bg-card p-6 space-y-4">
                <div className="rounded-lg border bg-primary/5 p-4">
                  <div className="text-xs font-semibold uppercase tracking-widest text-primary">Recommendation</div>
                  <div className="mt-2 text-lg font-semibold">Migrate to {asset.recommended}</div>
                  <p className="mt-1 text-sm text-muted-foreground">Estimated effort: {asset.migrationDays} days · Risk reduction: −{asset.riskReduction}%</p>
                </div>
                <ol className="space-y-3">
                  {["Inventory current call sites", "Add hybrid cipher suite (classical + PQC)", "Roll out to staging", "Canary in production", "Deprecate classical path"].map((s, i) => (
                    <li key={s} className="flex items-start gap-3 rounded-lg border p-3 text-sm">
                      <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">{i + 1}</span>
                      {s}
                    </li>
                  ))}
                </ol>
              </TabsContent>
            </Tabs>
          </div>

          <aside className="space-y-4">
            <div className="rounded-xl border bg-card p-5">
              <div className="text-sm font-semibold">Risk Trend</div>
              <div className="mt-3 h-32">
                <ResponsiveContainer>
                  <LineChart data={trend}>
                    <YAxis hide domain={[0, 100]} />
                    <XAxis hide dataKey="m" />
                    <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--color-border)", background: "white", fontSize: 12 }} />
                    <Line type="monotone" dataKey="v" stroke="var(--color-primary)" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-muted-foreground">Projected 12-week risk if migration proceeds on schedule.</p>
            </div>

            <div className="rounded-xl border bg-card p-5">
              <div className="text-sm font-semibold">Timeline</div>
              <ol className="mt-4 space-y-4">
                {[
                  { d: "Today", t: "Asset discovered" },
                  { d: "+2d", t: "Migration plan approved" },
                  { d: "+7d", t: "Hybrid rollout to staging" },
                  { d: `+${asset.migrationDays}d`, t: "PQC fully deployed" },
                ].map((e, i) => (
                  <li key={i} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <span className="h-2 w-2 rounded-full bg-primary" />
                      {i < 3 && <span className="mt-1 h-full w-px bg-border" />}
                    </div>
                    <div className="pb-2">
                      <div className="text-xs font-medium text-muted-foreground">{e.d}</div>
                      <div className="text-sm">{e.t}</div>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          </aside>
        </div>
      </main>
    </>
  );
}

function Info({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm font-medium">{value}</div>
    </div>
  );
}
