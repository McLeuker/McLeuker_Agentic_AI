'use client';

import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function SecurityTrustPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Security &amp; Trust
            </h1>
            <p className="text-white/50 mb-12">
              Last updated: February 6, 2026
            </p>

            <div className="space-y-10">
              <section>
                <p className="text-white/60 leading-relaxed">
                  At McLeuker AI, security is foundational to everything we build. We are committed to protecting your data and maintaining your trust through industry-standard security practices and transparent operations.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Data Encryption</h2>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium mb-2">In Transit</p>
                    <p className="text-white/60">All data transmitted between your browser and our servers is encrypted using TLS 1.2 or higher. We enforce HTTPS across all endpoints and use HSTS headers to prevent downgrade attacks.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium mb-2">At Rest</p>
                    <p className="text-white/60">All data stored in our databases is encrypted at rest using AES-256 encryption, managed by our infrastructure providers (Supabase, Railway).</p>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Authentication &amp; Access Control</h2>
                <p className="text-white/60 leading-relaxed">
                  We use Supabase Auth with OAuth 2.0 and PKCE (Proof Key for Code Exchange) for secure authentication. User sessions are managed via secure, HTTP-only cookies. We support Google OAuth for convenient and secure sign-in. Row-Level Security (RLS) policies ensure that users can only access their own data at the database level.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Infrastructure Security</h2>
                <p className="text-white/60 leading-relaxed">
                  Our infrastructure is hosted on enterprise-grade platforms (Vercel, Railway, Supabase) that maintain SOC 2 Type II compliance and undergo regular third-party security audits. We use environment-based secret management and never store API keys or credentials in source code.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">AI Safety &amp; Data Isolation</h2>
                <p className="text-white/60 leading-relaxed">
                  User data submitted to AI models is processed in real-time and is not used to train or fine-tune any models. Each user&apos;s conversation data is isolated at the database level through Row-Level Security policies. We do not share user data between accounts or with third parties beyond what is necessary to provide the Service.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Incident Response</h2>
                <p className="text-white/60 leading-relaxed">
                  In the event of a data breach, we will notify affected users and the relevant supervisory authority (CNIL) within 72 hours, as required by GDPR Article 33. Our incident response process includes immediate containment, investigation, notification, and remediation steps.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Responsible Disclosure</h2>
                <p className="text-white/60 leading-relaxed">
                  If you discover a security vulnerability in our platform, please report it responsibly to{' '}
                  <a href="mailto:security@mcleuker.com" className="text-white/80 underline hover:text-white">security@mcleuker.com</a>.
                  We appreciate the security research community and will acknowledge your contribution. Please do not publicly disclose the vulnerability until we have had a reasonable opportunity to address it.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Contact</h2>
                <p className="text-white/60 leading-relaxed">
                  For security-related questions or concerns, please contact{' '}
                  <a href="mailto:security@mcleuker.com" className="text-white/80 underline hover:text-white">security@mcleuker.com</a>.
                </p>
              </section>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
