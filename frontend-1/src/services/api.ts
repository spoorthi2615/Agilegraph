import { DashboardSummary, CryptoAsset, GraphNode, GraphEdge, ReportRecord } from "../lib/types";
import { apiClient } from "./api-client";

export const api = {
  uploadProject: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<any>("/upload", {
      body: formData,
    });
  },

  importGitHubRepository: async (url: string, branch?: string, token?: string) => {
    return apiClient.post<any>("/github", {
      body: { repository_url: url, branch, token },
    });
  },

  getDashboardSummary: async (): Promise<DashboardSummary> => {
    return apiClient.get<DashboardSummary>("/dashboard/summary");
  },

  getGraph: async (): Promise<{ nodes: GraphNode[], edges: GraphEdge[] }> => {
    return apiClient.get<{ nodes: GraphNode[], edges: GraphEdge[] }>("/graph");
  },

  getAssets: async (): Promise<CryptoAsset[]> => {
    return apiClient.get<any>("/analysis/assets").then(res => res.items || []);
  },
  
  getAssetById: async (id: string): Promise<CryptoAsset> => {
    return apiClient.get<CryptoAsset>(`/analysis/assets/${id}`);
  },

  getRiskReports: async (): Promise<ReportRecord[]> => {
    return apiClient.get<any>("/reports").then(res => res.items || []);
  },

  getExplainability: async (id: string): Promise<any> => {
    return apiClient.get<any>(`/explainability/${id}`);
  }
};
