import {
  DashboardSummary,
  CryptoAsset,
  GraphNode,
  GraphEdge,
  ReportRecord,
  Workspace,
  Notification,
  SearchResult,
  ExplainabilityData,
  ScanStatusResponse,
} from "../lib/types";
import { apiClient } from "./api-client";

export const api = {
  uploadProject: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<ScanStatusResponse>("/upload", {
      body: formData,
    });
  },

  importGitHubRepository: async (url: string, branch?: string, token?: string) => {
    return apiClient.post<ScanStatusResponse>("/github", {
      body: { repository_url: url, branch, access_token: token },
    });
  },

  scanDomain: async (domain: string, ports: number[]) => {
    return apiClient.post<ScanStatusResponse>("/domain", {
      body: { domain, ports },
    });
  },

  uploadCertificate: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<ScanStatusResponse>("/certificate", {
      body: formData,
    });
  },

  getDashboardSummary: async (): Promise<DashboardSummary> => {
    return apiClient.get<DashboardSummary>("/dashboard/summary");
  },

  getScanStatus: async (projectId: string): Promise<ScanStatusResponse> => {
    return apiClient.get<ScanStatusResponse>(`/scan/status/${projectId}`);
  },

  getGraph: async (): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> => {
    return apiClient.get<{ nodes: GraphNode[]; edges: GraphEdge[] }>("/graph");
  },

  getAssets: async (): Promise<CryptoAsset[]> => {
    return apiClient
      .get<{ items: CryptoAsset[] }>("/analysis/assets")
      .then((res) => res.items || []);
  },

  getAssetById: async (id: string): Promise<CryptoAsset> => {
    return apiClient.get<CryptoAsset>(`/analysis/assets/${id}`);
  },

  getRiskReports: async (): Promise<ReportRecord[]> => {
    return apiClient.get<ReportRecord[]>("/dashboard/reports");
  },

  getExplainability: async (id: string): Promise<ExplainabilityData> => {
    return apiClient.get<ExplainabilityData>(`/explainability/${id}`);
  },

  search: async (query: string): Promise<SearchResult[]> => {
    if (!query || query.length < 2) return [];
    return apiClient.get<SearchResult[]>(`/search/all?q=${encodeURIComponent(query)}`);
  },

  getNotifications: async (): Promise<Notification[]> => {
    return apiClient.get<Notification[]>("/notifications/all");
  },

  getWorkspaces: async (): Promise<Workspace[]> => {
    return apiClient.get<Workspace[]>("/workspaces/all");
  },
};
