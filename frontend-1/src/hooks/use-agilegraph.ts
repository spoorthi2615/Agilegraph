import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { DashboardSummary } from "../lib/types";

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

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: api.getDashboardSummary
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
