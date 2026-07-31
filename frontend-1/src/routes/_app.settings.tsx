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
import { useEffect, useState } from "react";

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
  const [activeTab, setActiveTab] = useState("theme");

  // Theme state
  const [colorMode, setColorMode] = useState((typeof window !== 'undefined' ? localStorage.getItem('theme') : null) || 'dark');
  const [accent, setAccent] = useState((typeof window !== 'undefined' ? localStorage.getItem('accent') : null) || 'blue');
  const [compact, setCompact] = useState((typeof window !== 'undefined' ? localStorage.getItem('compact') : null) === 'true');

  // Notifications state
  const [notifyCritical, setNotifyCritical] = useState((typeof window !== 'undefined' ? localStorage.getItem('notifyCritical') : null) !== 'false');
  const [notifyScan, setNotifyScan] = useState((typeof window !== 'undefined' ? localStorage.getItem('notifyScan') : null) !== 'false');
  const [notifyWeekly, setNotifyWeekly] = useState((typeof window !== 'undefined' ? localStorage.getItem('notifyWeekly') : null) !== 'false');
  const [slackChannel, setSlackChannel] = useState((typeof window !== 'undefined' ? localStorage.getItem('slackChannel') : null) || '');

  // Scan state
  const [deepGraph, setDeepGraph] = useState((typeof window !== 'undefined' ? localStorage.getItem('deepGraph') : null) !== 'false');
  const [includeKeys, setIncludeKeys] = useState((typeof window !== 'undefined' ? localStorage.getItem('includeKeys') : null) !== 'false');
  const [scanConcurrency, setScanConcurrency] = useState((typeof window !== 'undefined' ? localStorage.getItem('scanConcurrency') : null) || '4');
  const [failCritical, setFailCritical] = useState((typeof window !== 'undefined' ? localStorage.getItem('failCritical') : null) === 'true');

  // Dashboard state
  const [defaultView, setDefaultView] = useState((typeof window !== 'undefined' ? localStorage.getItem('defaultView') : null) || 'exec');
  const [showProgress, setShowProgress] = useState((typeof window !== 'undefined' ? localStorage.getItem('showProgress') : null) !== 'false');
  const [animatedCounters, setAnimatedCounters] = useState((typeof window !== 'undefined' ? localStorage.getItem('animatedCounters') : null) !== 'false');

  // Apply visual changes instantly
  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    if (colorMode === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(colorMode);
    }
  }, [colorMode]);

  useEffect(() => {
    const root = window.document.documentElement;
    if (compact) {
      root.classList.add('compact-density');
    } else {
      root.classList.remove('compact-density');
    }
  }, [compact]);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('theme-accent-blue', 'theme-accent-violet', 'theme-accent-emerald');
    root.classList.add(`theme-accent-${accent}`);
  }, [accent]);

  const handleSave = () => {
    localStorage.setItem('theme', colorMode);
    localStorage.setItem('accent', accent);
    localStorage.setItem('compact', compact.toString());
    
    localStorage.setItem('notifyCritical', notifyCritical.toString());
    localStorage.setItem('notifyScan', notifyScan.toString());
    localStorage.setItem('notifyWeekly', notifyWeekly.toString());
    localStorage.setItem('slackChannel', slackChannel);
    
    localStorage.setItem('deepGraph', deepGraph.toString());
    localStorage.setItem('includeKeys', includeKeys.toString());
    localStorage.setItem('scanConcurrency', scanConcurrency);
    localStorage.setItem('failCritical', failCritical.toString());
    
    localStorage.setItem('defaultView', defaultView);
    localStorage.setItem('showProgress', showProgress.toString());
    localStorage.setItem('animatedCounters', animatedCounters.toString());

    toast.success("Settings saved successfully", {
      description: "Your workspace preferences have been updated."
    });
  };

  const handleReset = () => {
    setColorMode('dark');
    setAccent('blue');
    setCompact(false);
    setNotifyCritical(true);
    setNotifyScan(true);
    setNotifyWeekly(true);
    setSlackChannel('');
    setDeepGraph(true);
    setIncludeKeys(true);
    setScanConcurrency('4');
    setFailCritical(false);
    setDefaultView('exec');
    setShowProgress(true);
    setAnimatedCounters(true);
    toast.info("Settings reset to defaults", { description: "Click save to confirm." });
  };

  return (
    <>
      <AppTopbar title="Settings" subtitle="Manage your workspace preferences" />
      <main className="p-4 md:p-6 animate-in fade-in slide-in-from-bottom-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} orientation="vertical" className="grid gap-6 lg:grid-cols-[220px_1fr]">
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
              <Row label="Color mode" desc="Light theme is optimized for readability."><Select value={colorMode} onValueChange={setColorMode}><SelectTrigger className="w-40"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="light">Light</SelectItem><SelectItem value="dark">Dark</SelectItem><SelectItem value="system">System</SelectItem></SelectContent></Select></Row>
              <Row label="Accent color" desc="Used for primary actions and highlights."><Select value={accent} onValueChange={setAccent}><SelectTrigger className="w-40"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="blue">AgileGraph Blue</SelectItem><SelectItem value="violet">Violet</SelectItem><SelectItem value="emerald">Emerald</SelectItem></SelectContent></Select></Row>
              <Row label="Compact density" desc="Reduce padding across tables and cards."><Switch checked={compact} onCheckedChange={setCompact} /></Row>
            </Section></TabsContent>

            <TabsContent value="notifications"><Section title="Notifications" desc="Control how you're alerted.">
              <Row label="Critical asset alerts" desc="Immediate notification for critical findings."><Switch checked={notifyCritical} onCheckedChange={setNotifyCritical} /></Row>
              <Row label="Scan completion" desc="Notify when scans finish."><Switch checked={notifyScan} onCheckedChange={setNotifyScan} /></Row>
              <Row label="Weekly digest" desc="Executive summary emailed weekly."><Switch checked={notifyWeekly} onCheckedChange={setNotifyWeekly} /></Row>
              <Row label="Slack channel" desc="Send alerts to a Slack channel."><Input placeholder="#security-pqc" className="w-56" value={slackChannel} onChange={(e) => setSlackChannel(e.target.value)} /></Row>
            </Section></TabsContent>

            <TabsContent value="scan"><Section title="Scan Preferences" desc="Defaults for new scans.">
              <Row label="Deep dependency graph" desc="Analyze transitive dependencies."><Switch checked={deepGraph} onCheckedChange={setDeepGraph} /></Row>
              <Row label="Include private keys" desc="Scan discovered keys against known-weak databases."><Switch checked={includeKeys} onCheckedChange={setIncludeKeys} /></Row>
              <Row label="Scan concurrency" desc="Parallel workers per scan."><Select value={scanConcurrency} onValueChange={setScanConcurrency}><SelectTrigger className="w-24"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="2">2</SelectItem><SelectItem value="4">4</SelectItem><SelectItem value="8">8</SelectItem></SelectContent></Select></Row>
              <Row label="Fail on critical" desc="CI: exit non-zero when critical assets are found."><Switch checked={failCritical} onCheckedChange={setFailCritical} /></Row>
            </Section></TabsContent>

            <TabsContent value="dashboard"><Section title="Dashboard Preferences" desc="Personalize your dashboard layout.">
              <Row label="Default view" desc="Which dashboard opens on login."><Select value={defaultView} onValueChange={setDefaultView}><SelectTrigger className="w-56"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="exec">Executive</SelectItem><SelectItem value="eng">Engineering</SelectItem><SelectItem value="compliance">Compliance</SelectItem></SelectContent></Select></Row>
              <Row label="Show migration progress" desc="Include the migration chart on the dashboard."><Switch checked={showProgress} onCheckedChange={setShowProgress} /></Row>
              <Row label="Animated counters" desc="Animate KPI numbers on load."><Switch checked={animatedCounters} onCheckedChange={setAnimatedCounters} /></Row>
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

        {activeTab !== 'about' && (
          <div className="mt-6 flex justify-end gap-2 animate-in fade-in slide-in-from-bottom-2">
            <Button variant="outline" onClick={handleReset}>Reset</Button>
            <Button onClick={handleSave}>Save changes</Button>
          </div>
        )}
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
