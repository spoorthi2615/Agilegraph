import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { DashboardSummary } from "../lib/types";
import * as mock from "../lib/mock-data";

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

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: async (): Promise<DashboardSummary> => {
      try {
        const data = await Promise.race([
          api.getDashboardSummary(),
          new Promise<never>((_, reject) =>
            setTimeout(() => reject(new Error("API timeout")), 5000)
          ),
        ]);
        // If the API returned all-zeros (Neo4j not connected), fall back to mock
        if (data && data.kpis && data.kpis.totalAssets === 0 && data.activity.length === 0) {
          return MOCK_DASHBOARD;
        }
        return data;
      } catch {
        return MOCK_DASHBOARD;
      }
    },
    retry: false,
    staleTime: 1000 * 60, // 1 minute
  });
}

export function useCryptoGraph() {
  return useQuery({
    queryKey: ["graph"],
    queryFn: api.getGraph
  });
}

export function useAssets() {
  return useQuery({
    queryKey: ["assets"],
    queryFn: api.getAssets
  });
}

export function useAsset(id: string) {
  return useQuery({
    queryKey: ["assets", id],
    queryFn: () => api.getAssetById(id),
    enabled: !!id
  });
}

export function useRiskReports() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: api.getRiskReports
  });
}

export function useExplainability(id: string) {
  return useQuery({
    queryKey: ["explainability", id],
    queryFn: () => api.getExplainability(id),
    enabled: !!id
  });
}

export function useSearch(query: string) {
  return useQuery({
    queryKey: ["search", query],
    queryFn: () => api.search(query),
    enabled: query.length >= 2,
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: api.getNotifications,
    staleTime: 1000 * 60, // 1 minute
  });
}

export function useWorkspaces() {
  return useQuery({
    queryKey: ["workspaces"],
    queryFn: api.getWorkspaces,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}
