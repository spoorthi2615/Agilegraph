export type RiskLevel = "critical" | "high" | "medium" | "low";
export type AssetType = "service" | "certificate" | "library" | "code" | "data" | "application" | "server";
export type MigrationStatus = "not-started" | "planned" | "in-progress" | "completed";

export interface CryptoAsset {
  id: string;
  name: string;
  type: AssetType;
  department: string;
  algorithm: string;
  keySize: string;
  riskScore: number; // 0-100
  risk: RiskLevel;
  recommended: string;
  migrationDays: number;
  riskReduction: number; // %
  status: MigrationStatus;
  priority: number; // 1-5
  discoveredAt: string;
  location: string;
  connections: string[]; // ids
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

const riskFromScore = (s: number): RiskLevel =>
  s >= 80 ? "critical" : s >= 60 ? "high" : s >= 35 ? "medium" : "low";

const DEPTS = ["Payments", "Identity", "Core Banking", "Infrastructure", "Data Platform", "Customer Portal", "Mobile", "APIs"];
const ALGOS = ["RSA-2048", "RSA-4096", "ECC-P256", "ECC-P384", "ECDSA-P256", "DH-2048", "SHA-1", "3DES", "AES-128-CBC", "Ed25519"];
const PQC = ["ML-KEM-768", "ML-KEM-1024", "ML-DSA-65", "ML-DSA-87", "SLH-DSA-SHA2-128s", "Falcon-512"];
const TYPES: AssetType[] = ["service", "certificate", "library", "code", "data", "application", "server"];

const NAMES: Array<{ name: string; type: AssetType; loc: string }> = [
  { name: "auth-service.java", type: "code", loc: "/services/auth/src/main/java" },
  { name: "payment-api", type: "service", loc: "cluster://payments/prod" },
  { name: "*.agilegraph.io TLS Certificate", type: "certificate", loc: "edge-lb-01" },
  { name: "customer-vault-db", type: "data", loc: "vault-cluster-eu" },
  { name: "mobile-banking-app", type: "application", loc: "iOS 17 / Android 14" },
  { name: "openssl-1.0.2", type: "library", loc: "/opt/lib/openssl" },
  { name: "identity-gateway", type: "server", loc: "az-eastus-1" },
  { name: "kyc-verification.py", type: "code", loc: "/apps/kyc/src" },
  { name: "internal-ca.pem", type: "certificate", loc: "pki-root" },
  { name: "transaction-signer", type: "service", loc: "cluster://core/prod" },
  { name: "session-token-service", type: "service", loc: "cluster://identity/prod" },
  { name: "fraud-detection.jar", type: "code", loc: "/apps/fraud" },
  { name: "wire-transfer-api", type: "service", loc: "cluster://payments/prod" },
  { name: "legacy-swift-adapter", type: "service", loc: "vm-legacy-04" },
  { name: "customer-portal-web", type: "application", loc: "cdn://portal" },
  { name: "hsm-signing-cluster", type: "server", loc: "on-prem-dc-1" },
  { name: "loan-origination.go", type: "code", loc: "/services/loans" },
  { name: "partner-api-gateway", type: "service", loc: "edge-gw-02" },
  { name: "backup-encryption-key", type: "data", loc: "kms://backups" },
  { name: "libcrypto.so.1.1", type: "library", loc: "/usr/lib" },
  { name: "*.internal.bank TLS", type: "certificate", loc: "internal-ca" },
  { name: "atm-network-gateway", type: "server", loc: "dc-north-2" },
  { name: "notification-service", type: "service", loc: "cluster://comms" },
  { name: "reports-generator.node", type: "code", loc: "/services/reports" },
  { name: "citizen-registry-db", type: "data", loc: "gov-cluster-1" },
  { name: "analytics-warehouse", type: "server", loc: "az-westus-3" },
  { name: "bouncycastle-1.68.jar", type: "library", loc: "/lib/security" },
  { name: "vpn-concentrator", type: "server", loc: "edge-vpn-01" },
  { name: "audit-log-signer", type: "service", loc: "cluster://compliance" },
  { name: "device-attestation", type: "service", loc: "cluster://mobile" },
  { name: "email-gateway.crt", type: "certificate", loc: "smtp-01" },
  { name: "settlement-engine", type: "application", loc: "core-cluster" },
  { name: "openjdk-8-crypto", type: "library", loc: "/usr/java/jre" },
  { name: "customer-support-portal", type: "application", loc: "cdn://support" },
  { name: "medical-records-api", type: "service", loc: "cluster://health" },
  { name: "prescription-signer", type: "service", loc: "cluster://health" },
  { name: "telco-billing-adapter", type: "service", loc: "vm-billing" },
  { name: "iot-device-registry", type: "data", loc: "iot-cluster" },
  { name: "root-ca-2015.pem", type: "certificate", loc: "pki-root" },
  { name: "checkout-service.ts", type: "code", loc: "/services/checkout" },
];

// Deterministic pseudo-random
function seed(i: number) {
  const x = Math.sin(i * 9301 + 49297) * 233280;
  return x - Math.floor(x);
}

export const assets: CryptoAsset[] = NAMES.map((n, i) => {
  const score = Math.floor(seed(i) * 100);
  const risk = riskFromScore(score);
  const algo = ALGOS[Math.floor(seed(i + 100) * ALGOS.length)];
  const rec = PQC[Math.floor(seed(i + 200) * PQC.length)];
  const dept = DEPTS[Math.floor(seed(i + 300) * DEPTS.length)];
  const statusRoll = seed(i + 400);
  const status: MigrationStatus =
    statusRoll < 0.55 ? "not-started" : statusRoll < 0.8 ? "planned" : statusRoll < 0.95 ? "in-progress" : "completed";
  return {
    id: `AST-${String(i + 1).padStart(4, "0")}`,
    name: n.name,
    type: n.type,
    department: dept,
    algorithm: algo,
    keySize: algo.includes("RSA") ? algo.split("-")[1] : algo.includes("ECC") || algo.includes("ECDSA") ? "256" : "—",
    riskScore: score,
    risk,
    recommended: rec,
    migrationDays: Math.floor(seed(i + 500) * 90) + 7,
    riskReduction: Math.floor(seed(i + 600) * 40) + 55,
    status,
    priority: Math.min(5, Math.max(1, Math.ceil(score / 20))),
    discoveredAt: new Date(Date.now() - Math.floor(seed(i + 700) * 30) * 86400000).toISOString(),
    location: n.loc,
    connections: [],
    description: `${n.name} uses ${algo} for cryptographic operations. Recommended migration to ${rec} based on NIST PQC standards.`,
  };
});

// wire up connections deterministically
assets.forEach((a, i) => {
  const conns: string[] = [];
  const count = Math.floor(seed(i + 800) * 4) + 1;
  for (let k = 0; k < count; k++) {
    const idx = Math.floor(seed(i * 7 + k + 900) * assets.length);
    if (idx !== i && !conns.includes(assets[idx].id)) conns.push(assets[idx].id);
  }
  a.connections = conns;
});

// Graph
export const graphNodes: GraphNode[] = assets.slice(0, 22).map((a, i) => {
  const angle = (i / 22) * Math.PI * 2;
  const ring = i % 3;
  const r = 140 + ring * 110;
  return {
    id: a.id,
    label: a.name,
    type: a.type,
    risk: a.risk,
    x: 500 + Math.cos(angle) * r + (seed(i + 1000) - 0.5) * 40,
    y: 320 + Math.sin(angle) * r + (seed(i + 1100) - 0.5) * 40,
  };
});
export const graphEdges: GraphEdge[] = [];
graphNodes.forEach((n, i) => {
  const asset = assets.find((a) => a.id === n.id)!;
  asset.connections.forEach((c) => {
    if (graphNodes.find((g) => g.id === c)) graphEdges.push({ source: n.id, target: c });
  });
});

export const kpis = {
  totalAssets: assets.length,
  critical: assets.filter((a) => a.risk === "critical").length,
  high: assets.filter((a) => a.risk === "high").length,
  medium: assets.filter((a) => a.risk === "medium").length,
  low: assets.filter((a) => a.risk === "low").length,
  migrationProgress: Math.round(
    (assets.filter((a) => a.status === "completed").length / assets.length) * 100 +
    (assets.filter((a) => a.status === "in-progress").length / assets.length) * 40,
  ),
  pqcReadiness: 42,
  lastScan: "2h ago",
};

export const riskDistribution = [
  { name: "Critical", value: kpis.critical, color: "var(--color-critical)" },
  { name: "High", value: kpis.high, color: "var(--color-warning)" },
  { name: "Medium", value: kpis.medium, color: "var(--color-chart-5)" },
  { name: "Low", value: kpis.low, color: "var(--color-success)" },
];

export const algorithmUsage = ALGOS.map((a) => ({
  algorithm: a,
  count: assets.filter((x) => x.algorithm === a).length,
})).filter((x) => x.count > 0).sort((a, b) => b.count - a.count);

export const departmentUsage = DEPTS.map((d) => ({
  department: d,
  assets: assets.filter((x) => x.department === d).length,
  critical: assets.filter((x) => x.department === d && x.risk === "critical").length,
}));

export const migrationTrend = Array.from({ length: 12 }).map((_, i) => ({
  month: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][i],
  migrated: Math.round(2 + seed(i + 10) * 8 + i * 1.4),
  planned: Math.round(4 + seed(i + 20) * 6 + i * 0.8),
}));

export const recentScans: ScanRecord[] = [
  { id: "SCN-2041", name: "core-banking-monorepo", source: "GitHub", startedAt: "2h ago", duration: "4m 12s", assets: 128, criticalFindings: 7, status: "completed" },
  { id: "SCN-2040", name: "payment-services.zip", source: "ZIP Upload", startedAt: "Yesterday", duration: "2m 45s", assets: 64, criticalFindings: 3, status: "completed" },
  { id: "SCN-2039", name: "api.agilegraph.io", source: "Domain", startedAt: "2 days ago", duration: "58s", assets: 22, criticalFindings: 1, status: "completed" },
  { id: "SCN-2038", name: "internal-ca-bundle.pem", source: "Certificate", startedAt: "3 days ago", duration: "12s", assets: 8, criticalFindings: 0, status: "completed" },
  { id: "SCN-2037", name: "mobile-banking-app", source: "GitHub", startedAt: "5 days ago", duration: "6m 08s", assets: 214, criticalFindings: 12, status: "completed" },
];

export const activity: ActivityItem[] = [
  { id: "1", actor: "Sarah Chen", action: "completed scan", target: "core-banking-monorepo", time: "12 min ago", kind: "scan" },
  { id: "2", actor: "AgileGraph AI", action: "flagged critical risk on", target: "hsm-signing-cluster", time: "1h ago", kind: "alert" },
  { id: "3", actor: "Marcus Weber", action: "migrated", target: "session-token-service to ML-KEM-768", time: "3h ago", kind: "migration" },
  { id: "4", actor: "Priya Raman", action: "exported", target: "Q4 Executive Report", time: "5h ago", kind: "report" },
  { id: "5", actor: "AgileGraph AI", action: "recommended PQC upgrade for", target: "12 payment assets", time: "8h ago", kind: "alert" },
  { id: "6", actor: "David Osei", action: "started migration for", target: "identity-gateway", time: "1 day ago", kind: "migration" },
];

export const criticalAlerts = assets
  .filter((a) => a.risk === "critical")
  .slice(0, 5)
  .map((a) => ({ id: a.id, title: a.name, reason: `${a.algorithm} vulnerable to Shor's algorithm`, score: a.riskScore }));

export const reports: ReportRecord[] = [
  { id: "RPT-118", title: "Q4 2025 Executive Summary", type: "Executive", createdAt: "Nov 12, 2025", size: "1.8 MB", author: "Sarah Chen" },
  { id: "RPT-117", title: "Payment Systems Migration Plan", type: "Migration", createdAt: "Nov 08, 2025", size: "3.4 MB", author: "Marcus Weber" },
  { id: "RPT-116", title: "Cryptographic Risk Deep-Dive", type: "Technical", createdAt: "Nov 04, 2025", size: "5.2 MB", author: "Priya Raman" },
  { id: "RPT-115", title: "Board Risk Briefing", type: "Risk", createdAt: "Oct 28, 2025", size: "980 KB", author: "David Osei" },
  { id: "RPT-114", title: "Identity Platform Assessment", type: "Technical", createdAt: "Oct 21, 2025", size: "2.7 MB", author: "Sarah Chen" },
];

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
