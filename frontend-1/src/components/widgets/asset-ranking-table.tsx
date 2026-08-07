import { useState, useMemo } from "react";
import { Link } from "@tanstack/react-router";
import { Input } from "../ui/input";
import { Badge } from "../ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { ArrowUpDown, Search } from "lucide-react";
import { RiskBadge } from "../risk-badge";
import { CryptoAsset, riskColor, RiskLevel } from "../../lib/types";

type SortKey = "risk" | "priority" | "migrationDays" | "riskReduction";

export function AssetRankingTable({ assets }: { assets: CryptoAsset[] }) {
  const [q, setQ] = useState("");
  const [risk, setRisk] = useState<string>("all");
  const [dept, setDept] = useState<string>("all");
  const [sort, setSort] = useState<SortKey>("risk");
  const [dir, setDir] = useState<"asc" | "desc">("desc");

  const rows = useMemo(() => {
    let r = assets.slice();
    if (q)
      r = r.filter(
        (a) =>
          a.name.toLowerCase().includes(q.toLowerCase()) ||
          a.algorithm.toLowerCase().includes(q.toLowerCase()),
      );
    if (risk !== "all") r = r.filter((a) => a.risk === risk);
    if (dept !== "all") r = r.filter((a) => a.department === dept);
    r.sort((a, b) => {
      const va = sort === "risk" ? a.riskScore : ((a as Record<string, unknown>)[sort] as number);
      const vb = sort === "risk" ? b.riskScore : ((b as Record<string, unknown>)[sort] as number);
      return dir === "asc" ? va - vb : vb - va;
    });
    return r;
  }, [assets, q, risk, dept, sort, dir]);

  const depts = Array.from(new Set(assets.map((a) => a.department)));

  const toggle = (k: SortKey) => {
    if (sort === k) setDir(dir === "asc" ? "desc" : "asc");
    else {
      setSort(k);
      setDir("desc");
    }
  };

  return (
    <div className="space-y-4">
      <div className="rounded-xl border bg-card p-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[240px] flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search assets or algorithms…"
              className="pl-9"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
          <Select value={risk} onValueChange={setRisk}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Risk" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Risk</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>
          <Select value={dept} onValueChange={setDept}>
            <SelectTrigger className="w-44">
              <SelectValue placeholder="Department" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Departments</SelectItem>
              {depts.map((d) => (
                <SelectItem key={d} value={d}>
                  {d}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="rounded-xl border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/30 text-xs text-muted-foreground">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Asset</th>
                <Th onClick={() => toggle("risk")}>Risk</Th>
                <Th onClick={() => toggle("priority")}>Priority</Th>
                <th className="px-4 py-3 text-left font-medium">Current</th>
                <th className="px-4 py-3 text-left font-medium">Recommended</th>
                <Th onClick={() => toggle("migrationDays")}>Est. Migration</Th>
                <Th onClick={() => toggle("riskReduction")}>Risk Reduction</Th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {rows.map((a) => (
                <tr key={a.id} className="group cursor-pointer transition-colors hover:bg-muted/25">
                  <td className="px-4 py-3">
                    <Link to="/assets/$id" params={{ id: a.id }} className="block">
                      <div className="font-medium group-hover:text-primary">{a.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {a.id} · {a.department}
                      </div>
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${a.riskScore}%`, background: riskColor[a.risk] }}
                        />
                      </div>
                      <span className="text-xs font-semibold tabular-nums">{a.riskScore}</span>
                      <RiskBadge risk={a.risk as RiskLevel} />
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-0.5">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <span
                          key={i}
                          className={`h-3 w-1.5 rounded ${i < a.priority ? "bg-primary" : "bg-muted"}`}
                        />
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant="outline" className="font-mono text-[11px]">
                      {a.algorithm}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge className="font-mono text-[11px] bg-primary/10 text-primary hover:bg-primary/10">
                      {a.recommended}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{a.migrationDays}d</td>
                  <td className="px-4 py-3 text-success font-medium">−{a.riskReduction}%</td>
                  <td className="px-4 py-3">
                    <StatusChip status={a.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {rows.length === 0 && (
          <div className="p-12 text-center">
            <div className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-muted">
              <Search className="h-5 w-5 text-muted-foreground" />
            </div>
            <p className="mt-4 text-sm font-medium">No matching assets</p>
            <p className="text-xs text-muted-foreground">Try adjusting your filters</p>
          </div>
        )}
      </div>
    </div>
  );
}

function Th({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <th className="px-4 py-3 text-left font-medium">
      <button className="inline-flex items-center gap-1 hover:text-foreground" onClick={onClick}>
        {children}
        <ArrowUpDown className="h-3 w-3" />
      </button>
    </th>
  );
}

function StatusChip({ status }: { status: string }) {
  const map: Record<string, string> = {
    "not-started": "bg-muted text-muted-foreground",
    planned: "bg-primary/10 text-primary",
    "in-progress": "bg-warning/10 text-warning",
    completed: "bg-success/10 text-success",
  };
  const label: Record<string, string> = {
    "not-started": "Not started",
    planned: "Planned",
    "in-progress": "In progress",
    completed: "Completed",
  };
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${map[status]}`}>
      {label[status]}
    </span>
  );
}
