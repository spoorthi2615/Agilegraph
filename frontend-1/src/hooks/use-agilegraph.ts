import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { DashboardSummary } from "../lib/types";
import * as mock from "../lib/mock-data";
import { demoStore } from "../lib/demo-store";

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Race an async fn against a timeout; on error/timeout return fallback */
async function withFallback<T>(id: string, fn: () => Promise<T>, fallback: T, ms = 5000): Promise<T> {
  try {
    const result = await Promise.race([
      fn(),
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error("API timeout")), ms)
      ),
    ]);
    demoStore.setFallback(id, false);
    return result;
  } catch {
    demoStore.setFallback(id, true);
    return fallback;
  }
}

// ─── Mock data constants ─────────────────────────────────────────────────────

const MOCK_DASHBOARD: DashboardSummary = {
  kpis: mock.kpis,
  riskDistribution: mock.riskDistribution,
  algorithmUsage: mock.algorithmUsage,
  departmentUsage: mock.departmentUsage,
  migrationTrend: mock.migrationTrend,
  recentScans: mock.recentScans,
  activity: mock.activity,
  criticalAlerts: mock.criticalAlerts,
};

const MOCK_GRAPH = { nodes: mock.graphNodes, edges: mock.graphEdges };

// ─── Mutations ───────────────────────────────────────────────────────────────

export function useUploadProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => api.uploadProject(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useGitHubImport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ url, branch, token }: { url: string; branch?: string; token?: string }) =>
      api.importGitHubRepository(url, branch, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDomainScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ domain, ports }: { domain: string; ports: number[] }) =>
      api.scanDomain(domain, ports),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useCertificateScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => api.uploadCertificate(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: async (): Promise<DashboardSummary> => {
      const data = await withFallback("dashboardSummary", api.getDashboardSummary, MOCK_DASHBOARD);
      return data;
    },
    retry: false,
    staleTime: 1000 * 60,
  });
}

// ─── Graph ───────────────────────────────────────────────────────────────────

export function useCryptoGraph() {
  return useQuery({
    queryKey: ["graph"],
    queryFn: () => withFallback("cryptoGraph", api.getGraph, MOCK_GRAPH),
    retry: false,
    staleTime: 1000 * 60 * 5,
  });
}

// ─── Assets ──────────────────────────────────────────────────────────────────

export function useAssets() {
  return useQuery({
    queryKey: ["assets"],
    queryFn: async () => {
      const data = await withFallback("assets", api.getAssets, mock.assets as any[]);
      return data;
    },
    retry: false,
    staleTime: 1000 * 60 * 5,
  });
}

export function useAsset(id: string) {
  return useQuery({
    queryKey: ["assets", id],
    queryFn: async () => {
      if (!id) return null;
      // Try backend first, fall back to mock assets lookup
      const fallback = (mock.assets as any[]).find((a) => a.id === id) ?? null;
      return withFallback(`asset-${id}`, () => api.getAssetById(id), fallback);
    },
    enabled: !!id,
    retry: false,
    staleTime: 1000 * 60 * 5,
  });
}

// ─── Reports ─────────────────────────────────────────────────────────────────

export function useRiskReports() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: () => withFallback("riskReports", api.getRiskReports, mock.reports as any[]),
    retry: false,
    staleTime: 1000 * 60,
  });
}

// ─── Explainability ──────────────────────────────────────────────────────────

const MOCK_EXPLAIN = (assetId: string) => {
  const asset = (mock.assets as any[]).find((a) => a.id === assetId) ?? mock.assets[0];
  return {
    assetInformation: {
      assetId: asset.id,
      name: asset.name,
      algorithm: asset.algorithm,
      overallRisk: asset.riskScore,
    },
    naturalLanguageSummary: asset.description,
    gnnExplanation: {
      featureImportance: [
        { featureName: "Algorithm strength", contribution: 0.38, positiveInfluence: true },
        { featureName: "Graph centrality", contribution: 0.27, positiveInfluence: true },
        { featureName: "Key size adequacy", contribution: 0.20, positiveInfluence: true },
        { featureName: "Quantum vulnerability", contribution: 0.15, positiveInfluence: true },
      ],
    },
    heuristicExplanation: {
      breakdown: {
        riskFormulaBreakdown: `Algorithm ${asset.algorithm} is considered vulnerable to Shor's algorithm.`,
        penaltyBreakdown: "Graph centrality penalty applied based on number of direct dependents.",
      },
    },
    migrationRecommendation: {
      recommendedPqcAlgorithm: asset.recommended,
      migrationEffort: asset.migrationDays,
      estimatedRiskReduction: asset.riskReduction,
    },
    confidenceMetrics: { overallConfidence: 0.87 },
  };
};

export function useExplainability(id: string) {
  return useQuery({
    queryKey: ["explainability", id],
    queryFn: () => withFallback(`explainability-${id}`, () => api.getExplainability(id), MOCK_EXPLAIN(id)),
    enabled: !!id,
    retry: false,
    staleTime: 1000 * 60 * 5,
  });
}

// ─── Mosca ───────────────────────────────────────────────────────────────────

export function useMoscaReadiness(z: number) {
  return useQuery({
    queryKey: ["mosca", z],
    queryFn: () =>
      withFallback(
        `mosca-${z}`,
        async () => {
          const { apiClient } = await import("../services/api-client");
          return apiClient.get<any>(`/dashboard/mosca?z=${z}`);
        },
        { x: 10.0, y: 1.2, z, surplus: +(z - 11.2).toFixed(1), readiness_score: 74, has_data: true }
      ),
    retry: false,
    staleTime: 1000 * 30,
  });
}

// ─── Search ──────────────────────────────────────────────────────────────────

export function useSearch(query: string) {
  return useQuery({
    queryKey: ["search", query],
    queryFn: () => api.search(query),
    enabled: query.length >= 2,
    staleTime: 1000 * 30,
  });
}

// ─── Notifications & Workspaces ───────────────────────────────────────────────

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: () => withFallback("notifications", api.getNotifications, []),
    retry: false,
    staleTime: 1000 * 60,
  });
}

export function useWorkspaces() {
  return useQuery({
    queryKey: ["workspaces"],
    queryFn: () => withFallback("workspaces", api.getWorkspaces, []),
    retry: false,
    staleTime: 1000 * 60 * 60,
  });
}
