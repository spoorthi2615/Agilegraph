import { createFileRoute } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { UploadCloud, Github, Globe, FileKey2, Play, X, CheckCircle2, Loader2, ArrowRight } from "lucide-react";
import { recentScans } from "@/lib/mock-data";
import { toast } from "sonner";

export const Route = createFileRoute("/_app/scan")({
  component: ScanPage,
  head: () => ({
    meta: [
      { title: "Scan Project — AgileGraph" },
      { name: "description", content: "Discover cryptographic assets across repos, uploads, domains, and certificates." },
    ],
  }),
});

function ScanPage() {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState("Idle");

  const start = () => {
    if (running) return;
    setRunning(true);
    setProgress(0);
    setPhase("Cloning repository");
    toast.success("Scan started", { description: "Discovering cryptographic assets…" });
    const phases = [
      "Cloning repository", "Parsing source files", "Detecting algorithms",
      "Building crypto graph", "Scoring risk", "Generating recommendations",
    ];
    let p = 0, i = 0;
    const t = setInterval(() => {
      p += 3 + Math.random() * 5;
      if (p >= 100) { p = 100; clearInterval(t); setRunning(false); setPhase("Completed"); toast.success("Scan complete"); }
      else if (p > (i + 1) * (100 / phases.length)) { i = Math.min(i + 1, phases.length - 1); setPhase(phases[i]); }
      setProgress(p);
    }, 350);
  };

  return (
    <>
      <AppTopbar title="Scan Project" subtitle="Discover cryptographic assets across your stack" />
      <main className="p-4 md:p-6 space-y-6">
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-xl border bg-card p-6">
            <Tabs defaultValue="zip">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="zip"><UploadCloud className="mr-2 h-4 w-4" />Upload</TabsTrigger>
                <TabsTrigger value="github"><Github className="mr-2 h-4 w-4" />GitHub</TabsTrigger>
                <TabsTrigger value="domain"><Globe className="mr-2 h-4 w-4" />Domain</TabsTrigger>
                <TabsTrigger value="cert"><FileKey2 className="mr-2 h-4 w-4" />Certificate</TabsTrigger>
              </TabsList>

              <TabsContent value="zip" className="mt-6">
                <Dropzone />
              </TabsContent>
              <TabsContent value="github" className="mt-6 space-y-4">
                <div className="space-y-2"><Label>Repository URL</Label><Input placeholder="https://github.com/org/repo" /></div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2"><Label>Branch</Label><Input placeholder="main" defaultValue="main" /></div>
                  <div className="space-y-2"><Label>Access Token (optional)</Label><Input placeholder="ghp_…" type="password" /></div>
                </div>
              </TabsContent>
              <TabsContent value="domain" className="mt-6 space-y-4">
                <div className="space-y-2"><Label>Domain or Host</Label><Input placeholder="api.example.com" /></div>
                <div className="space-y-2"><Label>Ports (comma separated)</Label><Input placeholder="443, 8443" defaultValue="443" /></div>
              </TabsContent>
              <TabsContent value="cert" className="mt-6"><Dropzone hint="Drop .pem, .crt, .p12, or .jks files" /></TabsContent>
            </Tabs>

            <div className="mt-6 rounded-lg border bg-muted/30 p-4">
              <div className="text-sm font-semibold">Scan Options</div>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                {[
                  ["Deep dependency graph", true],
                  ["Include transitive libraries", true],
                  ["Detect harvest-now-decrypt-later risk", true],
                  ["Suggest PQC alternatives", true],
                  ["Include TLS handshake fingerprinting", false],
                  ["Auto-generate migration plan", true],
                ].map(([k, v]) => (
                  <div key={k as string} className="flex items-center justify-between rounded-md border bg-background px-3 py-2">
                    <Label className="text-sm">{k}</Label>
                    <Switch defaultChecked={v as boolean} />
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <Button variant="outline" onClick={() => { setRunning(false); setProgress(0); setPhase("Idle"); }}><X className="h-4 w-4" />Cancel</Button>
              <Button onClick={start} disabled={running} className="shadow-[var(--shadow-glow)]">
                {running ? <><Loader2 className="h-4 w-4 animate-spin" />Scanning…</> : <><Play className="h-4 w-4" />Start Scan</>}
              </Button>
            </div>
          </div>

          <div className="rounded-xl border bg-card p-6">
            <div className="text-sm font-semibold">Scan Progress</div>
            <div className="mt-4 rounded-lg border bg-muted/30 p-4">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium">{phase}</span>
                <span className="text-muted-foreground">{Math.floor(progress)}%</span>
              </div>
              <Progress value={progress} className="mt-3" />
              <ul className="mt-4 space-y-2 text-xs">
                {["Cloning repository", "Parsing source files", "Detecting algorithms", "Building crypto graph", "Scoring risk", "Generating recommendations"].map((p, i) => {
                  const done = progress > ((i + 1) * (100 / 6)) - 1;
                  const active = phase === p;
                  return (
                    <li key={p} className="flex items-center gap-2">
                      {done ? <CheckCircle2 className="h-3.5 w-3.5 text-success" /> : active ? <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" /> : <span className="h-3.5 w-3.5 rounded-full border" />}
                      <span className={done ? "text-foreground" : active ? "text-foreground font-medium" : "text-muted-foreground"}>{p}</span>
                    </li>
                  );
                })}
              </ul>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-center">
              <div className="rounded-lg border p-3"><div className="text-xs text-muted-foreground">Assets found</div><div className="text-lg font-semibold">{Math.floor(progress * 1.28)}</div></div>
              <div className="rounded-lg border p-3"><div className="text-xs text-muted-foreground">Critical</div><div className="text-lg font-semibold text-critical">{Math.floor(progress / 15)}</div></div>
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-card">
          <div className="flex items-center justify-between border-b p-5">
            <div>
              <h3 className="text-sm font-semibold">Recent Scan History</h3>
              <p className="text-xs text-muted-foreground">Last 5 scans across your workspace</p>
            </div>
            <Button variant="outline" size="sm">View all <ArrowRight className="h-3.5 w-3.5" /></Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/30 text-xs text-muted-foreground">
                <tr>
                  {["Scan", "Source", "Started", "Duration", "Assets", "Critical", "Status"].map((h) => (
                    <th key={h} className="px-5 py-3 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y">
                {recentScans.map((s) => (
                  <tr key={s.id} className="hover:bg-muted/20">
                    <td className="px-5 py-3"><div className="font-medium">{s.name}</div><div className="text-xs text-muted-foreground">{s.id}</div></td>
                    <td className="px-5 py-3"><Badge variant="secondary">{s.source}</Badge></td>
                    <td className="px-5 py-3 text-muted-foreground">{s.startedAt}</td>
                    <td className="px-5 py-3 text-muted-foreground">{s.duration}</td>
                    <td className="px-5 py-3 font-medium">{s.assets}</td>
                    <td className="px-5 py-3"><span className="text-critical font-medium">{s.criticalFindings}</span></td>
                    <td className="px-5 py-3"><Badge className="bg-success/15 text-success hover:bg-success/15">Completed</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </>
  );
}

function Dropzone({ hint = "Drop your project ZIP file here, or click to browse" }: { hint?: string }) {
  const [drag, setDrag] = useState(false);
  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => { e.preventDefault(); setDrag(false); toast.success("File attached", { description: e.dataTransfer.files[0]?.name ?? "ready to scan" }); }}
      className={`grid place-items-center rounded-xl border-2 border-dashed p-12 text-center transition-colors ${drag ? "border-primary bg-primary/5" : "border-border bg-muted/20"}`}
    >
      <div className="grid h-14 w-14 place-items-center rounded-full bg-primary/10 text-primary">
        <UploadCloud className="h-7 w-7" />
      </div>
      <div className="mt-4 text-sm font-medium">{hint}</div>
      <div className="mt-1 text-xs text-muted-foreground">Supports .zip, .tar.gz up to 500 MB</div>
      <Button variant="outline" size="sm" className="mt-4">Choose file</Button>
    </div>
  );
}
