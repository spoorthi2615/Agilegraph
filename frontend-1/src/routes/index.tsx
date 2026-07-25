import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ShieldCheck, ScanLine, Network, ShieldAlert, Sparkles, Route as RouteIcon,
  ArrowRight, Zap, Building2, Eye, GaugeCircle, Github, CheckCircle2, ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/")({
  component: Landing,
  head: () => ({
    meta: [
      { title: "AgileGraph — Accelerate Your Post-Quantum Migration" },
      { name: "description", content: "AI-powered platform to discover vulnerable cryptographic assets and prioritize migration to Post-Quantum Cryptography." },
      { property: "og:title", content: "AgileGraph — Post-Quantum Migration Platform" },
      { property: "og:description", content: "Discover, rank, and migrate vulnerable cryptographic assets to PQC with explainable AI." },
    ],
  }),
});

function Landing() {
  return (
    <div className="min-h-screen bg-background">
      <MarketingNav />
      <Hero />
      <TrustBar />
      <Features />
      <HowItWorks />
      <Benefits />
      <CTA />
      <Footer />
    </div>
  );
}

function MarketingNav() {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-primary to-[oklch(0.55_0.22_290)] text-white shadow-[var(--shadow-glow)]">
            <ShieldCheck className="h-4.5 w-4.5" />
          </div>
          <span className="text-base font-semibold tracking-tight">AgileGraph</span>
        </Link>
        <nav className="hidden items-center gap-8 md:flex">
          <a href="#features" className="text-sm text-muted-foreground hover:text-foreground">Features</a>
          <a href="#how" className="text-sm text-muted-foreground hover:text-foreground">How it works</a>
          <a href="#benefits" className="text-sm text-muted-foreground hover:text-foreground">Benefits</a>
          <Link to="/dashboard" className="text-sm text-muted-foreground hover:text-foreground">Product</Link>
        </nav>
        <div className="flex items-center gap-2">
          <Button asChild size="sm" className="shadow-[var(--shadow-glow)]">
            <Link to="/scan">Start Scan <ArrowRight className="h-3.5 w-3.5" /></Link>
          </Button>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="hero-gradient relative overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-60" />
      <div className="relative mx-auto max-w-7xl px-6 pt-20 pb-24 md:pt-28 md:pb-32">
        <div className="grid items-center gap-14 lg:grid-cols-2">
          <div className="animate-fade-up">
            <Badge variant="secondary" className="mb-5 gap-2 rounded-full border bg-white px-3 py-1 shadow-[var(--shadow-soft)]">
              <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
              NIST PQC ready · CNSA 2.0 aligned
            </Badge>
            <h1 className="text-4xl font-semibold tracking-tight text-foreground md:text-6xl md:leading-[1.05]">
              Accelerate Your
              <br />
              <span className="bg-gradient-to-r from-primary via-[oklch(0.6_0.22_285)] to-[oklch(0.62_0.2_320)] bg-clip-text text-transparent">
                Post-Quantum Migration
              </span>
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">
              AgileGraph discovers every cryptographic asset across your stack, models the
              blast-radius on a live dependency graph, and gives your team an explainable,
              prioritized migration plan to Post-Quantum Cryptography.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Button asChild size="lg" className="h-11 shadow-[var(--shadow-glow)]">
                <Link to="/scan">Start Scan <ArrowRight className="h-4 w-4" /></Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="h-11">
                <a href="#how">Learn More</a>
              </Button>
            </div>
            <div className="mt-8 flex flex-wrap items-center gap-6 text-xs text-muted-foreground">
              {["SOC 2 Type II", "ISO 27001", "FedRAMP In Process", "GDPR"].map((t) => (
                <div key={t} className="flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5 text-success" />{t}</div>
              ))}
            </div>
          </div>

          <HeroIllustration />
        </div>
      </div>
    </section>
  );
}

function HeroIllustration() {
  return (
    <div className="relative animate-fade-up">
      <div className="absolute -inset-6 rounded-3xl bg-gradient-to-br from-primary/15 via-transparent to-[oklch(0.7_0.2_300)]/15 blur-2xl" />
      <div className="relative rounded-2xl border bg-card p-4 shadow-[var(--shadow-elevated)]">
        <div className="flex items-center gap-2 border-b pb-3">
          <span className="h-2.5 w-2.5 rounded-full bg-critical/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-warning/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-success/70" />
          <span className="ml-3 text-xs text-muted-foreground">agilegraph.io — Crypto Graph</span>
        </div>
        <svg viewBox="0 0 520 340" className="mt-3 w-full">
          <defs>
            <radialGradient id="g1" cx="50%" cy="50%">
              <stop offset="0%" stopColor="oklch(0.548 0.212 265)" stopOpacity="0.4" />
              <stop offset="100%" stopColor="oklch(0.548 0.212 265)" stopOpacity="0" />
            </radialGradient>
          </defs>
          <circle cx="260" cy="170" r="150" fill="url(#g1)" />
          {[
            [140, 90, 22, "oklch(0.628 0.238 27)"],
            [380, 80, 18, "oklch(0.79 0.155 75)"],
            [420, 210, 16, "oklch(0.708 0.155 163)"],
            [130, 240, 20, "oklch(0.62 0.15 300)"],
            [270, 60, 14, "oklch(0.708 0.155 163)"],
            [260, 300, 16, "oklch(0.79 0.155 75)"],
            [90, 170, 14, "oklch(0.708 0.155 163)"],
            [340, 260, 14, "oklch(0.62 0.15 300)"],
          ].map((n, i) => {
            const [x, y, r, c] = n as [number, number, number, string];
            return (
              <g key={i}>
                <line x1={260} y1={170} x2={x} y2={y} stroke="oklch(0.85 0.02 260)" strokeWidth="1.2" />
              </g>
            );
          })}
          <circle cx="260" cy="170" r="34" fill="white" stroke="oklch(0.548 0.212 265)" strokeWidth="2" />
          <circle cx="260" cy="170" r="10" fill="oklch(0.548 0.212 265)" />
          {[
            [140, 90, 22, "oklch(0.628 0.238 27)"],
            [380, 80, 18, "oklch(0.79 0.155 75)"],
            [420, 210, 16, "oklch(0.708 0.155 163)"],
            [130, 240, 20, "oklch(0.62 0.15 300)"],
            [270, 60, 14, "oklch(0.708 0.155 163)"],
            [260, 300, 16, "oklch(0.79 0.155 75)"],
            [90, 170, 14, "oklch(0.708 0.155 163)"],
            [340, 260, 14, "oklch(0.62 0.15 300)"],
          ].map((n, i) => {
            const [x, y, r, c] = n as [number, number, number, string];
            return <circle key={i} cx={x} cy={y} r={r} fill="white" stroke={c} strokeWidth="3" />;
          })}
        </svg>
        <div className="mt-3 grid grid-cols-3 gap-3">
          {[
            { label: "Critical", value: 12, color: "text-critical", bg: "bg-critical/10" },
            { label: "High", value: 34, color: "text-warning", bg: "bg-warning/10" },
            { label: "Ready", value: "42%", color: "text-success", bg: "bg-success/10" },
          ].map((s) => (
            <div key={s.label} className={`rounded-lg border p-3 ${s.bg}`}>
              <div className="text-[11px] text-muted-foreground">{s.label}</div>
              <div className={`text-lg font-semibold ${s.color}`}>{s.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function TrustBar() {
  return (
    <div className="border-y bg-muted/30">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-x-14 gap-y-4 px-6 py-8 text-sm font-medium text-muted-foreground">
        <span className="text-xs uppercase tracking-widest">Trusted by teams at</span>
        {["Meridian Bank", "Northwind Health", "Orbit Telecom", "Ministry of Digital", "Vector Capital", "Helios Energy"].map((n) => (
          <span key={n} className="opacity-70">{n}</span>
        ))}
      </div>
    </div>
  );
}

const features = [
  { icon: ScanLine, title: "Automated Discovery", body: "Scan repos, containers, TLS endpoints, and certificates to inventory every cryptographic asset in minutes." },
  { icon: Network, title: "Graph AI", body: "A live dependency graph exposes blast-radius, hidden trust chains, and the true impact of every algorithm." },
  { icon: ShieldAlert, title: "Risk Prioritization", body: "Multi-factor risk scoring combines Mosca timelines, exploitability, and business criticality." },
  { icon: Sparkles, title: "Explainable AI", body: "Every recommendation ships with a plain-language rationale, contributing factors, and confidence." },
  { icon: RouteIcon, title: "Migration Roadmap", body: "Sequenced plan with owners, effort, and PQC algorithm suggestions aligned to NIST FIPS 203/204/205." },
];

function Features() {
  return (
    <section id="features" className="mx-auto max-w-7xl px-6 py-24">
      <div className="mx-auto max-w-2xl text-center">
        <div className="text-xs font-semibold uppercase tracking-widest text-primary">Platform</div>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">Everything you need for a defensible PQC program</h2>
        <p className="mt-4 text-muted-foreground">One workspace for discovery, analysis, and orchestration — built for security, compliance, and engineering leaders.</p>
      </div>
      <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {features.map((f, i) => (
          <div key={f.title} className="card-hover animate-fade-up rounded-2xl border bg-card p-6" style={{ animationDelay: `${i * 60}ms` }}>
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-primary/10 text-primary">
              <f.icon className="h-5 w-5" />
            </div>
            <h3 className="mt-5 text-lg font-semibold">{f.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.body}</p>
          </div>
        ))}
        <div className="rounded-2xl border bg-gradient-to-br from-primary/8 to-transparent p-6">
          <div className="text-xs font-semibold uppercase tracking-widest text-primary">Standards</div>
          <h3 className="mt-3 text-lg font-semibold">Aligned with NIST FIPS 203, 204, 205 & CNSA 2.0</h3>
          <p className="mt-2 text-sm text-muted-foreground">Recommendations map directly to ML-KEM, ML-DSA, and SLH-DSA — with fallbacks for hybrid deployments.</p>
        </div>
      </div>
    </section>
  );
}

const steps = [
  { n: 1, title: "Scan Infrastructure", body: "Connect a repo, upload a bundle, or point AgileGraph at a domain. Discovery runs in minutes." },
  { n: 2, title: "Build Crypto Graph", body: "We reconstruct the full dependency graph — certificates, libraries, services, and sensitive data flows." },
  { n: 3, title: "Analyze Risk", body: "Every node is scored using Mosca's inequality, exploitability, and business criticality." },
  { n: 4, title: "Generate Migration Plan", body: "Sequenced, explainable roadmap to PQC — with owners, effort, and rollback checkpoints." },
];

function HowItWorks() {
  return (
    <section id="how" className="border-y bg-muted/30 py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <div className="text-xs font-semibold uppercase tracking-widest text-primary">How it works</div>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">From blind spot to migration plan in four steps</h2>
        </div>
        <div className="mt-14 grid gap-4 md:grid-cols-4">
          {steps.map((s, i) => (
            <div key={s.n} className="relative rounded-2xl border bg-card p-6 card-hover">
              <div className="flex items-center gap-3">
                <div className="grid h-9 w-9 place-items-center rounded-lg bg-primary text-sm font-semibold text-primary-foreground shadow-[var(--shadow-glow)]">
                  {s.n}
                </div>
                <div className="text-sm font-semibold">{s.title}</div>
              </div>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">{s.body}</p>
              {i < steps.length - 1 && (
                <ChevronRight className="absolute -right-3 top-1/2 hidden h-6 w-6 -translate-y-1/2 text-muted-foreground/40 md:block" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const benefits = [
  { icon: Building2, title: "Enterprise Ready", body: "SSO, RBAC, air-gapped deployment, and audit logs on day one." },
  { icon: Eye, title: "Explainable AI", body: "Every score comes with contributing factors and confidence intervals." },
  { icon: Zap, title: "Fast Analysis", body: "Discovery and scoring at millions of LOC per hour, running incrementally." },
  { icon: GaugeCircle, title: "Interactive Dashboard", body: "Executive KPIs, engineering deep-dives, and compliance exports in one place." },
];

function Benefits() {
  return (
    <section id="benefits" className="mx-auto max-w-7xl px-6 py-24">
      <div className="grid items-center gap-14 lg:grid-cols-2">
        <div>
          <div className="text-xs font-semibold uppercase tracking-widest text-primary">Why AgileGraph</div>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">Built for regulated industries and long-lived data</h2>
          <p className="mt-4 max-w-lg text-muted-foreground">
            Banks, healthcare, telecom, and government agencies choose AgileGraph to protect
            data that must remain confidential for decades — before harvest-now-decrypt-later becomes reality.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {benefits.map((b) => (
              <div key={b.title} className="rounded-xl border bg-card p-5 card-hover">
                <div className="grid h-9 w-9 place-items-center rounded-lg bg-primary/10 text-primary">
                  <b.icon className="h-4.5 w-4.5" />
                </div>
                <div className="mt-4 text-sm font-semibold">{b.title}</div>
                <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{b.body}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="relative">
          <div className="absolute -inset-8 rounded-3xl bg-gradient-to-br from-primary/10 to-transparent blur-2xl" />
          <div className="relative rounded-2xl border bg-card p-6 shadow-[var(--shadow-elevated)]">
            <div className="text-sm font-semibold">Executive Snapshot</div>
            <div className="text-xs text-muted-foreground">Live PQC readiness across your organization</div>
            <div className="mt-6 grid grid-cols-3 gap-4">
              {[
                { k: "Assets", v: "1,284", c: "text-foreground" },
                { k: "Critical", v: "47", c: "text-critical" },
                { k: "Migrated", v: "38%", c: "text-success" },
              ].map((s) => (
                <div key={s.k} className="rounded-lg border p-4">
                  <div className="text-[11px] text-muted-foreground">{s.k}</div>
                  <div className={`text-2xl font-semibold ${s.c}`}>{s.v}</div>
                </div>
              ))}
            </div>
            <div className="mt-6 space-y-3">
              {[["Payments", 72], ["Identity", 55], ["Core Banking", 41], ["Data Platform", 28]].map(([l, v]) => (
                <div key={l as string}>
                  <div className="mb-1 flex justify-between text-xs"><span className="text-muted-foreground">{l}</span><span className="font-medium">{v}%</span></div>
                  <div className="h-2 rounded-full bg-muted"><div className="h-full rounded-full bg-gradient-to-r from-primary to-[oklch(0.6_0.22_290)]" style={{ width: `${v}%` }} /></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section className="mx-auto max-w-7xl px-6 pb-24">
      <div className="relative overflow-hidden rounded-3xl border bg-gradient-to-br from-primary to-[oklch(0.5_0.22_285)] p-12 text-primary-foreground shadow-[var(--shadow-elevated)]">
        <div className="absolute inset-0 grid-bg opacity-20" />
        <div className="relative flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          <div>
            <h3 className="text-2xl font-semibold tracking-tight md:text-3xl">Ready to see your crypto graph?</h3>
            <p className="mt-2 max-w-lg text-primary-foreground/80">Run your first scan in under five minutes. No agents. No production impact.</p>
          </div>
          <div className="flex gap-3">
            <Button asChild size="lg" variant="secondary" className="h-11">
              <Link to="/scan">Start Scan <ArrowRight className="h-4 w-4" /></Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="h-11 border-white/30 bg-white/10 text-white hover:bg-white/20">
              <Link to="/dashboard">View Demo</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="mx-auto grid max-w-7xl gap-10 px-6 py-14 md:grid-cols-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-primary to-[oklch(0.55_0.22_290)] text-white">
              <ShieldCheck className="h-4.5 w-4.5" />
            </div>
            <span className="text-base font-semibold tracking-tight">AgileGraph</span>
          </div>
          <p className="mt-4 max-w-xs text-sm text-muted-foreground">
            The decision-support platform for post-quantum cryptographic migration.
          </p>
        </div>
        {[
          { h: "Product", l: ["Dashboard", "Scan", "Graph View", "Reports"] },
          { h: "Resources", l: ["NIST PQC Guide", "Mosca Framework", "Documentation", "Changelog"] },
          { h: "Company", l: ["About", "Security", "Privacy", "Contact"] },
        ].map((c) => (
          <div key={c.h}>
            <div className="text-sm font-semibold">{c.h}</div>
            <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
              {c.l.map((i) => <li key={i}><a href="#" className="hover:text-foreground">{i}</a></li>)}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-6 py-6 text-xs text-muted-foreground md:flex-row">
          <span>© 2026 AgileGraph. All rights reserved.</span>
          <div className="flex items-center gap-4">
            <a href="#" className="hover:text-foreground inline-flex items-center gap-1"><Github className="h-3.5 w-3.5" /> GitHub</a>
            <span>SOC 2 · ISO 27001</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
