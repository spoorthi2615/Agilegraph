import { createFileRoute } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useRiskReports } from "@/hooks/use-agilegraph";
import { api } from "@/services/api";
import { toast } from "sonner";
import { FileText, FileBarChart, Route as RouteIcon, ShieldAlert, Download, Printer, Table2 } from "lucide-react";

export const Route = createFileRoute("/_app/reports")({
  component: Reports,
  head: () => ({
    meta: [
      { title: "Reports — AgileGraph" },
      { name: "description", content: "Generate executive, technical, migration, and risk reports." },
    ],
  }),
});

const generators = [
  { key: "exec", title: "Executive Report", body: "Board-ready summary with KPIs and migration progress.", icon: FileBarChart, tint: "from-primary/15 to-primary/5" },
  { key: "tech", title: "Technical Report", body: "Full inventory with algorithms, dependencies, and remediation.", icon: FileText, tint: "from-[oklch(0.7_0.18_300)]/15 to-transparent" },
  { key: "mig", title: "Migration Plan", body: "Sequenced roadmap with owners, effort, and PQC recommendations.", icon: RouteIcon, tint: "from-success/15 to-transparent" },
  { key: "risk", title: "Risk Summary", body: "Prioritized critical exposures and Mosca readiness posture.", icon: ShieldAlert, tint: "from-critical/15 to-transparent" },
];

function Reports() {
  const { data: reports = [], refetch } = useRiskReports();

  const handleDownload = async (type: string, format: string) => {
    toast.info(`Generating ${format.toUpperCase()} report...`);
    try {
      // Connect to the backend using api client to ensure JWT Authorization headers are sent
      const response = await api.client.get(`/reports/latest/download?format=${format}&type=${encodeURIComponent(type)}`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `AgileGraph_${type.replace(/\s+/g, '_')}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success(`${type} downloaded successfully`);
      
      // Give backend time to record the generation, then refresh table
      setTimeout(() => {
        refetch();
      }, 1000);
    } catch (error) {
      toast.error(`Failed to download ${type}`);
    }
  };

  return (
    <>
      <AppTopbar title="Reports" subtitle="Generate and share compliance-ready reports" />
      <main className="p-4 md:p-6 space-y-6">
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {generators.map((g) => (
            <div key={g.key} className={`card-hover animate-fade-up rounded-2xl border bg-gradient-to-br ${g.tint} bg-card p-5`}>
              <div className="grid h-10 w-10 place-items-center rounded-lg bg-white shadow-[var(--shadow-soft)] text-primary">
                <g.icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-base font-semibold">{g.title}</h3>
              <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{g.body}</p>
              <div className="mt-4 flex flex-wrap gap-1.5">
                <Button size="sm" variant="outline" onClick={() => handleDownload(g.title, "pdf")}><Download className="h-3.5 w-3.5" />PDF</Button>
                <Button size="sm" variant="outline" onClick={() => handleDownload(g.title, "csv")}><Table2 className="h-3.5 w-3.5" />CSV</Button>
                <Button size="sm" variant="ghost" onClick={() => { window.print(); toast.success(`Printing ${g.title}`); }}><Printer className="h-3.5 w-3.5" />Print</Button>
              </div>
            </div>
          ))}
        </section>

        <section className="rounded-xl border bg-card">
          <div className="flex items-center justify-between border-b p-5">
            <div>
              <h3 className="text-sm font-semibold">Recent Reports</h3>
              <p className="text-xs text-muted-foreground">Generated in the last 90 days</p>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/30 text-xs text-muted-foreground">
                <tr>{["Title", "Type", "Created", "Size", "Author", ""].map((h) => <th key={h} className="px-5 py-3 text-left font-medium">{h}</th>)}</tr>
              </thead>
              <tbody className="divide-y">
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-muted/25">
                    <td className="px-5 py-3">
                      <div className="font-medium">{r.title}</div>
                      <div className="text-xs text-muted-foreground">{r.id}</div>
                    </td>
                    <td className="px-5 py-3"><Badge variant="secondary">{r.type}</Badge></td>
                    <td className="px-5 py-3 text-muted-foreground">{r.createdAt}</td>
                    <td className="px-5 py-3 text-muted-foreground">{r.size}</td>
                    <td className="px-5 py-3">{r.author}</td>
                    <td className="px-5 py-3 text-right">
                      <Button size="sm" variant="ghost" onClick={() => handleDownload(r.title, "pdf")}><Download className="h-4 w-4" /></Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </>
  );
}
