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

export function useDashboardSummary(mockFallback?: DashboardSummary) {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: api.getDashboardSummary,
    // Providing initialData so the UI doesn't break if the backend isn't running yet.
    // In a real prod scenario without mock fallbacks, we would handle the loading/error state in the UI.
    ...(mockFallback ? { initialData: mockFallback } : {})
  });
}

export function useCryptoGraph(mockFallback?: any) {
  return useQuery({
    queryKey: ["graph"],
    queryFn: api.getGraph,
    ...(mockFallback ? { initialData: mockFallback } : {})
  });
}

export function useAssets(mockFallback?: any) {
  return useQuery({
    queryKey: ["assets"],
    queryFn: api.getAssets,
    ...(mockFallback ? { initialData: mockFallback } : {})
  });
}

export function useAsset(id: string, mockFallback?: any) {
  return useQuery({
    queryKey: ["assets", id],
    queryFn: () => api.getAssetById(id),
    enabled: !!id,
    ...(mockFallback ? { initialData: mockFallback } : {})
  });
}

export function useRiskReports(mockFallback?: any) {
  return useQuery({
    queryKey: ["reports"],
    queryFn: api.getRiskReports,
    ...(mockFallback ? { initialData: mockFallback } : {})
  });
}

export function useExplainability(mockFallback?: any) {
  return useQuery({
    queryKey: ["explainability"],
    queryFn: api.getExplainability,
    ...(mockFallback ? { initialData: mockFallback } : {})
  });
}
