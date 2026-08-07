import { createFileRoute, Link } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { RiskBadge } from "@/components/risk-badge";
import { useMemo, useState } from "react";
import { useAssets } from "@/hooks/use-agilegraph";
import { riskColor, type RiskLevel } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { AssetRankingTable } from "@/components/widgets/asset-ranking-table";

export const Route = createFileRoute("/_app/rankings")({
  component: Rankings,
  head: () => ({
    meta: [
      { title: "Risk Rankings — AgileGraph" },
      {
        name: "description",
        content:
          "Sortable rankings of cryptographic assets by risk, priority, and migration effort.",
      },
    ],
  }),
});

type SortKey = "risk" | "priority" | "migrationDays" | "riskReduction";

function Rankings() {
  const { data: assets = [] } = useAssets();

  return (
    <>
      <AppTopbar
        title="Risk Rankings"
        subtitle={`${assets.length} assets`}
        actions={
          <Button size="sm" variant="outline">
            <Download className="h-4 w-4" />
            Export
          </Button>
        }
      />
      <main className="p-4 md:p-6 space-y-4">
        <AssetRankingTable assets={assets} />
      </main>
    </>
  );
}
