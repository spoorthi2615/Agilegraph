import { DashboardSummary, CryptoAsset, GraphNode, GraphEdge, ReportRecord } from "../lib/types";

// Base URL for the AgileGraph API
const API_BASE = "http://localhost:8000/api/v1"; 

export const api = {
  uploadProject: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },

  importGitHubRepository: async (url: string, branch?: string, token?: string) => {
    const res = await fetch(`${API_BASE}/github`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repository_url: url, branch, token }),
    });
    if (!res.ok) throw new Error("GitHub import failed");
    return res.json();
  },

  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (!res.ok) throw new Error("Failed to fetch dashboard summary");
    return res.json();
  },

  getGraph: async (): Promise<{ nodes: GraphNode[], edges: GraphEdge[] }> => {
    const res = await fetch(`${API_BASE}/dashboard/graph`);
    if (!res.ok) throw new Error("Failed to fetch graph");
    return res.json();
  },

  getAssets: async (): Promise<CryptoAsset[]> => {
    const res = await fetch(`${API_BASE}/analysis/assets`);
    if (!res.ok) throw new Error("Failed to fetch assets");
    return res.json();
  },
  
  getAssetById: async (id: string): Promise<CryptoAsset> => {
    const res = await fetch(`${API_BASE}/analysis/assets/${id}`);
    if (!res.ok) throw new Error("Failed to fetch asset");
    return res.json();
  },

  getRiskReports: async (): Promise<ReportRecord[]> => {
    const res = await fetch(`${API_BASE}/dashboard/reports`);
    if (!res.ok) throw new Error("Failed to fetch reports");
    return res.json();
  },

  getExplainability: async (): Promise<any[]> => {
    const res = await fetch(`${API_BASE}/dashboard/explanations`);
    if (!res.ok) throw new Error("Failed to fetch explanations");
    return res.json();
  }
};
