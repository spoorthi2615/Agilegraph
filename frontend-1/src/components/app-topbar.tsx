import { Bell, ChevronDown, Search as SearchIcon, Loader2, Check, LayoutGrid } from "lucide-react";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useState } from "react";
import { useSearch, useNotifications, useWorkspaces } from "@/hooks/use-agilegraph";
import { Link } from "@tanstack/react-router";

export function AppTopbar({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: React.ReactNode }) {
  const [searchQuery, setSearchQuery] = useState("");
  const { data: searchResults = [], isFetching: isSearching } = useSearch(searchQuery);
  const { data: notifications = [] } = useNotifications();
  const { data: workspaces = [] } = useWorkspaces();

  const unreadCount = notifications.filter((n: any) => !n.read).length;
  const activeWorkspace = workspaces.find((w: any) => w.isActive) || workspaces[0];

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b bg-background/80 px-4 backdrop-blur-md md:px-6">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="h-6" />
      <div className="flex min-w-0 flex-1 items-center gap-4">
        <div className="min-w-0">
          <h1 className="truncate text-base font-semibold tracking-tight">{title}</h1>
          {subtitle && <p className="truncate text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        
        {/* Search */}
        <div className="ml-auto hidden max-w-xs flex-1 lg:block">
          <Popover open={searchQuery.length > 0}>
            <PopoverTrigger asChild>
              <div className="relative">
                <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input 
                  placeholder="Search assets, scans, reports…" 
                  className="h-9 pl-9" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                {isSearching && (
                  <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
                )}
              </div>
            </PopoverTrigger>
            <PopoverContent className="w-[320px] p-0" align="start">
              {searchQuery.length >= 2 && (
                <div className="max-h-[300px] overflow-y-auto p-2">
                  {searchResults.length === 0 && !isSearching ? (
                    <div className="p-4 text-center text-sm text-muted-foreground">No results found for "{searchQuery}"</div>
                  ) : (
                    <div className="flex flex-col gap-1">
                      {searchResults.map((result: any) => (
                        <Link 
                          key={result.id} 
                          to={result.url} 
                          onClick={() => setSearchQuery("")}
                          className="flex flex-col rounded-md px-3 py-2 text-sm hover:bg-muted/50"
                        >
                          <span className="font-medium">{result.title}</span>
                          <span className="text-xs text-muted-foreground">{result.subtitle}</span>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </PopoverContent>
          </Popover>
        </div>

        <div className="flex items-center gap-2">
          {actions}
          
          {/* Notifications */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                  <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-critical animate-pulse-ring" />
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80 p-0" align="end">
              <div className="flex items-center justify-between border-b px-4 py-3">
                <h4 className="font-semibold text-sm">Notifications</h4>
                <Badge variant="secondary">{unreadCount} unread</Badge>
              </div>
              <div className="max-h-[300px] overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-4 text-center text-sm text-muted-foreground">You're all caught up!</div>
                ) : (
                  notifications.map((n: any) => (
                    <div key={n.id} className={`flex flex-col gap-1 border-b p-4 last:border-0 ${!n.read ? "bg-muted/20" : ""}`}>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{n.title}</span>
                        <span className="text-xs text-muted-foreground">{n.time}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{n.message}</p>
                    </div>
                  ))
                )}
              </div>
            </PopoverContent>
          </Popover>

          {/* Workspaces */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="hidden md:inline-flex gap-2">
                <LayoutGrid className="h-4 w-4 text-muted-foreground" />
                {activeWorkspace?.name || "Select Workspace"}
                {activeWorkspace && (
                  <Badge variant="secondary" className="ml-1 text-[10px]">
                    {activeWorkspace.environment}
                  </Badge>
                )}
                <ChevronDown className="h-3.5 w-3.5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[200px]">
              <DropdownMenuLabel>Switch Workspace</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {workspaces.map((ws: any) => (
                <DropdownMenuItem key={ws.id} className="flex items-center justify-between">
                  <span>{ws.name}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[10px]">{ws.environment}</Badge>
                    {ws.isActive && <Check className="h-4 w-4" />}
                  </div>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

        </div>
      </div>
    </header>
  );
}
