export type RiskLevel = "critical" | "high" | "medium" | "low";
export type AssetType = "service" | "certificate" | "crypto_asset" | "library" | "code" | "data" | "application" | "server" | string;
export type MigrationStatus = "not-started" | "planned" | "in-progress" | "completed";

export interface CryptoAsset {
  id: string;
  name: string;
  type: AssetType;
  department: string;
  algorithm: string;
  keySize: string;
  riskScore: number;
  risk: RiskLevel;
  recommended: string;
  migrationDays: number;
  riskReduction: number;
  status: MigrationStatus;
  priority: number;
  discoveredAt: string;
  location: string;
  connections: string[];
  description: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: AssetType;
  risk: RiskLevel;
  x: number;
  y: number;
}
export interface GraphEdge { source: string; target: string; }

export interface ScanRecord {
  id: string;
  name: string;
  source: "GitHub" | "ZIP Upload" | "Domain" | "Certificate";
  startedAt: string;
  duration: string;
  assets: number;
  criticalFindings: number;
  status: "completed" | "running" | "failed";
}

export interface ActivityItem {
  id: string;
  actor: string;
  action: string;
  target: string;
  time: string;
  kind: "scan" | "migration" | "alert" | "report";
}

export interface ReportRecord {
  id: string;
  title: string;
  type: "Executive" | "Technical" | "Migration" | "Risk";
  createdAt: string;
  size: string;
  author: string;
}

export interface DashboardSummary {
  kpis: {
    totalAssets: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    migrationProgress: number;
    pqcReadiness: number;
    lastScan: string;
  };
  riskDistribution: Array<{ name: string; value: number; color: string }>;
  algorithmUsage: Array<{ algorithm: string; count: number }>;
  departmentUsage: Array<{ department: string; assets: number; critical: number }>;
  migrationTrend: Array<{ month: string; migrated: number; planned: number }>;
  recentScans: ScanRecord[];
  activity: ActivityItem[];
  criticalAlerts: Array<{ id: string; title: string; reason: string; score: number }>;
}

export const riskColor: Record<RiskLevel, string> = {
  critical: "var(--color-critical)",
  high: "var(--color-warning)",
  medium: "var(--color-chart-5)",
  low: "var(--color-success)",
};

export const riskLabel: Record<RiskLevel, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};
