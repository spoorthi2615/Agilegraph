import { createFileRoute, Link } from '@tanstack/react-router';
import { ArrowLeft } from 'lucide-react';

export const Route = createFileRoute('/privacy')({
  component: PrivacyPolicy,
});

function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background px-6 py-12">
      <div className="mx-auto max-w-3xl">
        <Link to="/login" className="mb-8 inline-flex items-center text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Link>
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Privacy Policy</h1>
            <p className="text-muted-foreground mt-2">Last updated: {new Date().toLocaleDateString()}</p>
          </div>
          
          <div className="prose prose-sm dark:prose-invert max-w-none space-y-6 text-muted-foreground">
            <section>
              <h2 className="text-xl font-semibold text-foreground">1. Information We Collect</h2>
              <p>
                We collect information you provide directly to us, such as when you create or modify your account, request support, or otherwise communicate with us. This includes your name, email address, and authentication credentials.
              </p>
            </section>
            
            <section>
              <h2 className="text-xl font-semibold text-foreground">2. How We Use Your Information</h2>
              <p>
                We use the information we collect to provide, maintain, and improve our services, to process transactions, and to send you related information, including confirmations and technical notices.
              </p>
            </section>
            
            <section>
              <h2 className="text-xl font-semibold text-foreground">3. Security</h2>
              <p>
                We take reasonable measures to help protect information about you from loss, theft, misuse and unauthorized access, disclosure, alteration and destruction.
              </p>
            </section>
            
            <section>
              <h2 className="text-xl font-semibold text-foreground">4. Contact Us</h2>
              <p>
                If you have any questions about this Privacy Policy, please contact us at support@agilegraph.io.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
