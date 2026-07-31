import { Link, useRouterState } from "@tanstack/react-router";
import {
  LayoutDashboard, ScanLine, Network, ShieldAlert, Sparkles,
  Gauge, FileText, Settings, ShieldCheck, LogOut
} from "lucide-react";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent,
  SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem,
} from "@/components/ui/sidebar";
import { supabase } from "@/lib/supabase";
import { useEffect, useState } from "react";

const nav = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Scan Project", url: "/scan", icon: ScanLine },
  { title: "Graph View", url: "/graph", icon: Network },
  { title: "Risk Rankings", url: "/rankings", icon: ShieldAlert },
  { title: "Explainability", url: "/explainability", icon: Sparkles },
  { title: "Mosca Readiness", url: "/mosca", icon: Gauge },
  { title: "Reports", url: "/reports", icon: FileText },
];
const bottom = [{ title: "Settings", url: "/settings", icon: Settings }];

export function AppSidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const isActive = (u: string) => pathname === u || pathname.startsWith(u + "/");
  const [user, setUser] = useState<{ name: string; email: string; initials: string; id: string } | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        const name = user.user_metadata?.full_name || user.email?.split('@')[0] || "User";
        const email = user.email || "";
        const initials = name.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase();
        setUser({ name, email, initials, id: user.id });

        // Hardcode admin email to bypass database permission issues
        if (email === 'spoorthipyadav@gmail.com' || email === 'spoorthi2615@gmail.com') {
          setIsAdmin(true);
        }
      }
    });
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  return (
    <Sidebar collapsible="icon" className="border-r">
      <SidebarHeader className="border-b">
        <Link to="/" className="flex items-center gap-2.5 px-2 py-2">
          <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-primary to-[oklch(0.55_0.22_290)] text-white shadow-[var(--shadow-glow)]">
            <ShieldCheck className="h-4.5 w-4.5" />
          </div>
          <div className="min-w-0 group-data-[collapsible=icon]:hidden">
            <div className="truncate text-sm font-semibold tracking-tight">AgileGraph</div>
            <div className="truncate text-[11px] text-muted-foreground">PQC Migration Platform</div>
          </div>
        </Link>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Workspace</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {nav.map((item) => (
                <SidebarMenuItem key={item.url}>
                  <SidebarMenuButton asChild isActive={isActive(item.url)} tooltip={item.title}>
                    <Link to={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t">
        <SidebarMenu>
          {isAdmin && (
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={isActive("/admin")} tooltip="Admin Console" className="text-primary hover:text-primary/80">
                <Link to="/admin">
                  <ShieldCheck />
                  <span>Admin Console</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}

          {bottom.map((item) => (
            <SidebarMenuItem key={item.url}>
              <SidebarMenuButton asChild isActive={isActive(item.url)} tooltip={item.title}>
                <Link to={item.url}>
                  <item.icon />
                  <span>{item.title}</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
          
          <SidebarMenuItem>
            <SidebarMenuButton 
              onClick={handleLogout} 
              tooltip="Log out" 
              className="text-destructive hover:bg-destructive/10 hover:text-destructive cursor-pointer"
            >
              <LogOut />
              <span>Log out</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
        
        {user && (
          <div className="mt-2 flex w-full items-center gap-2 rounded-lg border bg-muted/40 p-2 text-left group-data-[collapsible=icon]:hidden">
            <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-gradient-to-br from-[oklch(0.7_0.15_20)] to-[oklch(0.65_0.15_320)] text-xs font-semibold text-white">
              {user.initials}
            </div>
            <div className="min-w-0 flex-1 text-xs">
              <div className="truncate font-medium">{user.name}</div>
              <div className="truncate text-muted-foreground">{user.email}</div>
            </div>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
