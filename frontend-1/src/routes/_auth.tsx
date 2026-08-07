import { createFileRoute, Outlet, Link, useNavigate } from "@tanstack/react-router";
import { ShieldCheck } from "lucide-react";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export const Route = createFileRoute("/_auth")({
  component: AuthLayout,
});

function AuthLayout() {
  const navigate = useNavigate();

  useEffect(() => {
    // If the user is already logged in and tries to view login/signup pages, send them back to the dashboard
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        navigate({ to: "/dashboard", replace: true });
      }
    });

    // Also listen for auth state changes just in case they log in on another tab
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        navigate({ to: "/dashboard", replace: true });
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  return (
    <div className="flex min-h-screen">
      {/* Left side - Branding & Decorative */}
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden border-r bg-muted/20 p-10 lg:flex">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-[oklch(0.7_0.2_300)]/10" />
        <div className="absolute inset-0 grid-bg opacity-30" />

        <div className="relative z-10 flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-primary to-[oklch(0.55_0.22_290)] text-white shadow-[var(--shadow-glow)]">
            <ShieldCheck className="h-4.5 w-4.5" />
          </div>
          <span className="text-xl font-semibold tracking-tight">AgileGraph</span>
        </div>

        <div className="relative z-10 animate-fade-up">
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl md:leading-[1.1]">
            Secure your transition to <br />
            <span className="bg-gradient-to-r from-primary to-[oklch(0.62_0.2_320)] bg-clip-text text-transparent">
              Post-Quantum Cryptography
            </span>
          </h1>
          <p className="mt-4 max-w-md text-muted-foreground">
            Discover vulnerable assets, map your dependencies, and prioritize migration seamlessly
            with our AI-powered graph platform.
          </p>

          <div className="mt-12 flex items-center gap-4 text-xs font-medium text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-success"></span> SOC 2 Type II
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-success"></span> ISO 27001
            </span>
          </div>
        </div>
      </div>

      {/* Right side - Auth forms */}
      <div className="flex w-full flex-col justify-center px-4 py-12 lg:w-1/2 lg:px-12 xl:px-24">
        {/* Mobile Header */}
        <div className="mb-8 flex items-center justify-center gap-2 lg:hidden">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-primary to-[oklch(0.55_0.22_290)] text-white shadow-[var(--shadow-glow)]">
            <ShieldCheck className="h-4.5 w-4.5" />
          </div>
          <span className="text-xl font-semibold tracking-tight">AgileGraph</span>
        </div>

        <div className="mx-auto w-full max-w-sm animate-fade-up">
          <Outlet />
        </div>

        <p className="mx-auto mt-12 text-center text-xs text-muted-foreground">
          By continuing, you agree to our{" "}
          <Link to="/terms" className="underline hover:text-foreground">
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link to="/privacy" className="underline hover:text-foreground">
            Privacy Policy
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
