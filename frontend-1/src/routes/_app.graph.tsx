import { createFileRoute, Link } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { useMemo, useState } from "react";
import { graphNodes, graphEdges, assets, riskColor, type RiskLevel } from "@/lib/mock-data";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RiskBadge } from "@/components/risk-badge";
import { Search, ZoomIn, ZoomOut, Maximize2, Filter, ArrowRight } from "lucide-react";

export const Route = createFileRoute("/_app/graph")({
  component: GraphView,
  head: () => ({
    meta: [
      { title: "Graph View — AgileGraph" },
      { name: "description", content: "Interactive dependency graph of cryptographic assets and their blast radius." },
    ],
  }),
});

const TYPES = ["service", "certificate", "library", "code", "data", "application", "server"];

function GraphView() {
  const [selected, setSelected] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [types, setTypes] = useState<string[]>(TYPES);
  const [q, setQ] = useState("");

  const visible = useMemo(() => graphNodes.filter((n) => types.includes(n.type) && (!q || n.label.toLowerCase().includes(q.toLowerCase()))), [types, q]);
  const visibleIds = new Set(visible.map((n) => n.id));
  const edges = graphEdges.filter((e) => visibleIds.has(e.source) && visibleIds.has(e.target));
  const selectedAsset = selected ? assets.find((a) => a.id === selected) : null;

  const toggle = (t: string) => setTypes((prev) => prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]);

  return (
    <>
      <AppTopbar title="Graph View" subtitle="Interactive cryptographic dependency graph" />
      <main className="p-4 md:p-6">
        <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
          <aside className="space-y-4">
            <div className="rounded-xl border bg-card p-4">
              <div className="flex items-center gap-2 text-sm font-semibold"><Filter className="h-4 w-4" /> Filters</div>
              <div className="relative mt-3">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input placeholder="Search nodes…" className="pl-9" value={q} onChange={(e) => setQ(e.target.value)} />
              </div>
              <div className="mt-4">
                <div className="mb-2 text-xs font-medium text-muted-foreground">Node types</div>
                <div className="space-y-1.5">
                  {TYPES.map((t) => (
                    <label key={t} className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-muted/50">
                      <input type="checkbox" checked={types.includes(t)} onChange={() => toggle(t)} className="h-3.5 w-3.5 accent-[var(--color-primary)]" />
                      <span className="capitalize">{t}</span>
                      <span className="ml-auto text-xs text-muted-foreground">{graphNodes.filter((n) => n.type === t).length}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="mt-4 border-t pt-4">
                <div className="mb-2 text-xs font-medium text-muted-foreground">Risk legend</div>
                <div className="space-y-1.5 text-sm">
                  {(["critical","high","medium","low"] as RiskLevel[]).map((r) => (
                    <div key={r} className="flex items-center gap-2">
                      <span className="h-3 w-3 rounded-full" style={{ background: riskColor[r] }} />
                      <span className="capitalize">{r}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          <div className="relative overflow-hidden rounded-xl border bg-card">
            <div className="absolute right-4 top-4 z-10 flex flex-col gap-1 rounded-lg border bg-background/90 p-1 shadow-[var(--shadow-soft)] backdrop-blur">
              <Button variant="ghost" size="icon" onClick={() => setZoom((z) => Math.min(2, z + 0.15))}><ZoomIn className="h-4 w-4" /></Button>
              <Button variant="ghost" size="icon" onClick={() => setZoom((z) => Math.max(0.5, z - 0.15))}><ZoomOut className="h-4 w-4" /></Button>
              <Button variant="ghost" size="icon" onClick={() => setZoom(1)}><Maximize2 className="h-4 w-4" /></Button>
            </div>

            <div className="absolute left-4 top-4 z-10 rounded-lg border bg-background/90 px-3 py-2 text-xs shadow-[var(--shadow-soft)] backdrop-blur">
              <span className="font-medium">{visible.length}</span> nodes · <span className="font-medium">{edges.length}</span> edges
            </div>

            <div className="grid-bg h-[600px] w-full">
              <svg viewBox="0 0 1000 640" className="h-full w-full" style={{ transform: `scale(${zoom})`, transformOrigin: "center" }}>
                {edges.map((e, i) => {
                  const s = graphNodes.find((n) => n.id === e.source)!;
                  const t = graphNodes.find((n) => n.id === e.target)!;
                  return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="oklch(0.88 0.01 260)" strokeWidth="1" />;
                })}
                {visible.map((n) => {
                  const size = n.risk === "critical" ? 20 : n.risk === "high" ? 17 : n.risk === "medium" ? 14 : 12;
                  const isSel = selected === n.id;
                  return (
                    <g key={n.id} className="cursor-pointer" onClick={() => setSelected(n.id)}>
                      {isSel && <circle cx={n.x} cy={n.y} r={size + 8} fill="none" stroke="var(--color-primary)" strokeWidth="2" opacity="0.6" />}
                      <circle cx={n.x} cy={n.y} r={size} fill="white" stroke={riskColor[n.risk]} strokeWidth="3" />
                      <circle cx={n.x} cy={n.y} r={size / 3} fill={riskColor[n.risk]} />
                      <text x={n.x} y={n.y + size + 12} textAnchor="middle" fontSize="10" fill="var(--color-muted-foreground)" style={{ pointerEvents: "none" }}>
                        {n.label.length > 22 ? n.label.slice(0, 20) + "…" : n.label}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>
        </div>
      </main>

      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent className="w-full sm:max-w-md overflow-y-auto">
          {selectedAsset && (
            <>
              <SheetHeader>
                <div className="flex items-center gap-3">
                  <div className="grid h-10 w-10 place-items-center rounded-lg" style={{ background: `color-mix(in oklab, ${riskColor[selectedAsset.risk]} 15%, transparent)`, color: riskColor[selectedAsset.risk] }}>
                    <span className="text-sm font-bold">{selectedAsset.type[0].toUpperCase()}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <SheetTitle className="truncate text-left">{selectedAsset.name}</SheetTitle>
                    <SheetDescription className="text-left">{selectedAsset.id} · {selectedAsset.location}</SheetDescription>
                  </div>
                </div>
              </SheetHeader>

              <div className="mt-6 space-y-5 px-4">
                <div className="rounded-lg border p-4">
                  <div className="text-xs text-muted-foreground">Risk Score</div>
                  <div className="mt-2 flex items-end gap-3">
                    <div className="text-4xl font-semibold tracking-tight" style={{ color: riskColor[selectedAsset.risk] }}>{selectedAsset.riskScore}</div>
                    <RiskBadge risk={selectedAsset.risk} className="mb-1" />
                  </div>
                  <div className="mt-3 h-1.5 rounded-full bg-muted overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${selectedAsset.riskScore}%`, background: riskColor[selectedAsset.risk] }} />
                  </div>
                </div>

                <Row label="Current Algorithm" value={<Badge variant="outline" className="font-mono">{selectedAsset.algorithm}</Badge>} />
                <Row label="Recommended PQC" value={<Badge className="font-mono bg-primary/10 text-primary hover:bg-primary/10">{selectedAsset.recommended}</Badge>} />
                <Row label="Department" value={<span>{selectedAsset.department}</span>} />
                <Row label="Migration Priority" value={
                  <div className="flex gap-0.5">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <span key={i} className={`h-3 w-1.5 rounded ${i < selectedAsset.priority ? "bg-primary" : "bg-muted"}`} />
                    ))}
                  </div>
                } />
                <Row label="Estimated Effort" value={<span>{selectedAsset.migrationDays} days</span>} />

                <div>
                  <div className="mb-2 text-xs text-muted-foreground">Connected Assets ({selectedAsset.connections.length})</div>
                  <ul className="space-y-1.5">
                    {selectedAsset.connections.map((c) => {
                      const asset = assets.find((a) => a.id === c);
                      if (!asset) return null;
                      return (
                        <li key={c}>
                          <button onClick={() => setSelected(c)} className="flex w-full items-center gap-2 rounded-md border px-3 py-2 text-left text-sm hover:bg-muted/40">
                            <span className="h-2 w-2 rounded-full" style={{ background: riskColor[asset.risk] }} />
                            <span className="truncate">{asset.name}</span>
                            <ArrowRight className="ml-auto h-3.5 w-3.5 text-muted-foreground" />
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>

                <Button asChild className="w-full">
                  <Link to="/assets/$id" params={{ id: selectedAsset.id }}>View full details <ArrowRight className="h-4 w-4" /></Link>
                </Button>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b pb-3">
      <span className="text-xs text-muted-foreground">{label}</span>
      <div>{value}</div>
    </div>
  );
}
