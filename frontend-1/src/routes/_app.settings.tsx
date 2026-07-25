import { createFileRoute } from "@tanstack/react-router";
import { AppTopbar } from "@/components/app-topbar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { ShieldCheck } from "lucide-react";

export const Route = createFileRoute("/_app/settings")({
  component: Settings,
  head: () => ({
    meta: [
      { title: "Settings — AgileGraph" },
      { name: "description", content: "Manage theme, notifications, scan preferences, and dashboard preferences." },
    ],
  }),
});

function Settings() {
  return (
    <>
      <AppTopbar title="Settings" subtitle="Manage your workspace preferences" />
      <main className="p-4 md:p-6">
        <Tabs defaultValue="theme" orientation="vertical" className="grid gap-6 lg:grid-cols-[220px_1fr]">
          <TabsList className="flex h-auto flex-col items-stretch justify-start bg-transparent p-0">
            {[
              ["theme", "Theme"],
              ["notifications", "Notifications"],
              ["scan", "Scan Preferences"],
              ["dashboard", "Dashboard Preferences"],
              ["about", "About AgileGraph"],
            ].map(([k, l]) => (
              <TabsTrigger key={k} value={k} className="justify-start data-[state=active]:bg-muted data-[state=active]:shadow-none">
                {l}
              </TabsTrigger>
            ))}
          </TabsList>

          <div>
            <TabsContent value="theme"><Section title="Theme" desc="Customize how AgileGraph looks.">
              <Row label="Color mode" desc="Light theme is optimized for readability."><Select defaultValue="light"><SelectTrigger className="w-40"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="light">Light</SelectItem><SelectItem value="system">System</SelectItem></SelectContent></Select></Row>
              <Row label="Accent color" desc="Used for primary actions and highlights."><Select defaultValue="blue"><SelectTrigger className="w-40"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="blue">AgileGraph Blue</SelectItem><SelectItem value="violet">Violet</SelectItem><SelectItem value="emerald">Emerald</SelectItem></SelectContent></Select></Row>
              <Row label="Compact density" desc="Reduce padding across tables and cards."><Switch /></Row>
            </Section></TabsContent>

            <TabsContent value="notifications"><Section title="Notifications" desc="Control how you're alerted.">
              <Row label="Critical asset alerts" desc="Immediate notification for critical findings."><Switch defaultChecked /></Row>
              <Row label="Scan completion" desc="Notify when scans finish."><Switch defaultChecked /></Row>
              <Row label="Weekly digest" desc="Executive summary emailed weekly."><Switch defaultChecked /></Row>
              <Row label="Slack channel" desc="Send alerts to a Slack channel."><Input placeholder="#security-pqc" className="w-56" /></Row>
            </Section></TabsContent>

            <TabsContent value="scan"><Section title="Scan Preferences" desc="Defaults for new scans.">
              <Row label="Deep dependency graph" desc="Analyze transitive dependencies."><Switch defaultChecked /></Row>
              <Row label="Include private keys" desc="Scan discovered keys against known-weak databases."><Switch defaultChecked /></Row>
              <Row label="Scan concurrency" desc="Parallel workers per scan."><Select defaultValue="4"><SelectTrigger className="w-24"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="2">2</SelectItem><SelectItem value="4">4</SelectItem><SelectItem value="8">8</SelectItem></SelectContent></Select></Row>
              <Row label="Fail on critical" desc="CI: exit non-zero when critical assets are found."><Switch /></Row>
            </Section></TabsContent>

            <TabsContent value="dashboard"><Section title="Dashboard Preferences" desc="Personalize your dashboard layout.">
              <Row label="Default view" desc="Which dashboard opens on login."><Select defaultValue="exec"><SelectTrigger className="w-56"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="exec">Executive</SelectItem><SelectItem value="eng">Engineering</SelectItem><SelectItem value="compliance">Compliance</SelectItem></SelectContent></Select></Row>
              <Row label="Show migration progress" desc="Include the migration chart on the dashboard."><Switch defaultChecked /></Row>
              <Row label="Animated counters" desc="Animate KPI numbers on load."><Switch defaultChecked /></Row>
            </Section></TabsContent>

            <TabsContent value="about"><Section title="About AgileGraph" desc="Platform version and credits.">
              <div className="rounded-xl border p-6">
                <div className="flex items-center gap-3">
                  <div className="grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-primary to-[oklch(0.55_0.22_290)] text-white shadow-[var(--shadow-glow)]"><ShieldCheck className="h-6 w-6" /></div>
                  <div>
                    <div className="text-lg font-semibold tracking-tight">AgileGraph</div>
                    <div className="text-xs text-muted-foreground">Post-Quantum Cryptography Decision Platform</div>
                  </div>
                </div>
                <dl className="mt-6 grid gap-3 text-sm md:grid-cols-2">
                  <div><dt className="text-xs text-muted-foreground">Version</dt><dd>1.0.0-rc.4</dd></div>
                  <div><dt className="text-xs text-muted-foreground">Build</dt><dd>2026.07.20 · agilegraph-web</dd></div>
                  <div><dt className="text-xs text-muted-foreground">Standards</dt><dd>NIST FIPS 203 / 204 / 205 · CNSA 2.0</dd></div>
                  <div><dt className="text-xs text-muted-foreground">Compliance</dt><dd>SOC 2 Type II · ISO 27001</dd></div>
                </dl>
                <p className="mt-6 text-xs text-muted-foreground">© 2026 AgileGraph. Built as a Final Year Engineering Project.</p>
              </div>
            </Section></TabsContent>
          </div>
        </Tabs>

        <div className="mt-6 flex justify-end gap-2">
          <Button variant="outline">Reset</Button>
          <Button onClick={() => toast.success("Settings saved")}>Save changes</Button>
        </div>
      </main>
    </>
  );
}

function Section({ title, desc, children }: { title: string; desc: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border bg-card p-6">
      <div>
        <h2 className="text-base font-semibold">{title}</h2>
        <p className="text-xs text-muted-foreground">{desc}</p>
      </div>
      <div className="mt-6 divide-y">{children}</div>
    </div>
  );
}

function Row({ label, desc, children }: { label: string; desc: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <Label className="text-sm font-medium">{label}</Label>
        <p className="text-xs text-muted-foreground">{desc}</p>
      </div>
      <div>{children}</div>
    </div>
  );
}
