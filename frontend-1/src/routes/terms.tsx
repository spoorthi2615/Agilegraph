import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";

export const Route = createFileRoute("/terms")({
  component: Terms,
});

function Terms() {
  return (
    <div className="min-h-screen bg-background px-6 py-12">
      <div className="mx-auto max-w-3xl">
        <Link
          to="/login"
          className="mb-8 inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Link>
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Terms of Service</h1>
            <p className="text-muted-foreground mt-2">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>

          <div className="prose prose-sm dark:prose-invert max-w-none space-y-6 text-muted-foreground">
            <section>
              <h2 className="text-xl font-semibold text-foreground">1. Acceptance of Terms</h2>
              <p>
                By accessing or using AgileGraph, you agree to be bound by these Terms of Service.
                If you do not agree to these terms, please do not use our services.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-foreground">2. Description of Service</h2>
              <p>
                AgileGraph is an AI-powered platform designed to discover vulnerable cryptographic
                assets and assist in the migration to Post-Quantum Cryptography (PQC). We provide
                scanning, analysis, and reporting tools.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-foreground">3. User Responsibilities</h2>
              <p>
                You are responsible for maintaining the confidentiality of your account credentials
                and for all activities that occur under your account. You agree not to use the
                service for any illegal or unauthorized purpose.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-foreground">
                4. Data Privacy and Security
              </h2>
              <p>
                We prioritize the security of your data. However, you acknowledge that no system can
                be completely secure. Please refer to our Privacy Policy for detailed information on
                how we collect, use, and protect your data.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
