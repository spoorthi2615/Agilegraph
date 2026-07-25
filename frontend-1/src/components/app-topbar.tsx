import { Bell, ChevronDown, Search } from "lucide-react";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export function AppTopbar({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: React.ReactNode }) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b bg-background/80 px-4 backdrop-blur-md md:px-6">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="h-6" />
      <div className="flex min-w-0 flex-1 items-center gap-4">
        <div className="min-w-0">
          <h1 className="truncate text-base font-semibold tracking-tight">{title}</h1>
          {subtitle && <p className="truncate text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        <div className="ml-auto hidden max-w-xs flex-1 lg:block">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Search assets, scans, reports…" className="h-9 pl-9" />
          </div>
        </div>
        <div className="flex items-center gap-2">
          {actions}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-4 w-4" />
            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-critical animate-pulse-ring" />
          </Button>
          <Button variant="outline" size="sm" className="hidden md:inline-flex gap-2">
            <span className="h-5 w-5 rounded bg-gradient-to-br from-primary to-[oklch(0.55_0.22_290)]" />
            Acme Bank
            <Badge variant="secondary" className="ml-1 text-[10px]">PROD</Badge>
            <ChevronDown className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
