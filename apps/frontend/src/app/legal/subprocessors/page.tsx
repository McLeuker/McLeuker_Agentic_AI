'use client';

import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function SubprocessorsPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Subprocessors
            </h1>
            <p className="text-white/50 mb-12">
              Last updated: February 6, 2026
            </p>

            <div className="space-y-10">
              <section>
                <p className="text-white/60 leading-relaxed mb-6">
                  McLeuker AI uses the following third-party subprocessors to deliver our Service. Each subprocessor has been vetted for GDPR compliance and operates under a Data Processing Agreement (DPA) with appropriate safeguards, including Standard Contractual Clauses (SCCs) for transfers outside the EEA where applicable.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Infrastructure &amp; Hosting</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Subprocessor</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Purpose</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Location</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Transfer Mechanism</th>
                      </tr>
                    </thead>
                    <tbody className="text-white/60">
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Vercel Inc.</td>
                        <td className="py-3 px-4">Frontend hosting, CDN, edge functions</td>
                        <td className="py-3 px-4">USA (Edge: Global)</td>
                        <td className="py-3 px-4">SCCs + DPA</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Railway Corp.</td>
                        <td className="py-3 px-4">Backend API hosting</td>
                        <td className="py-3 px-4">USA</td>
                        <td className="py-3 px-4">SCCs + DPA</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Supabase Inc.</td>
                        <td className="py-3 px-4">Database, authentication, file storage</td>
                        <td className="py-3 px-4">USA</td>
                        <td className="py-3 px-4">SCCs + DPA</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">AI &amp; Machine Learning</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Subprocessor</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Purpose</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Location</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Transfer Mechanism</th>
                      </tr>
                    </thead>
                    <tbody className="text-white/60">
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">xAI (Grok)</td>
                        <td className="py-3 px-4">Large language model inference for reasoning and content generation</td>
                        <td className="py-3 px-4">USA</td>
                        <td className="py-3 px-4">SCCs + DPA</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Perplexity AI</td>
                        <td className="py-3 px-4">Web search and real-time information retrieval</td>
                        <td className="py-3 px-4">USA</td>
                        <td className="py-3 px-4">SCCs + DPA</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Development &amp; Source Control</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Subprocessor</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Purpose</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Location</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Transfer Mechanism</th>
                      </tr>
                    </thead>
                    <tbody className="text-white/60">
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">GitHub (Microsoft)</td>
                        <td className="py-3 px-4">Source code repository and CI/CD</td>
                        <td className="py-3 px-4">USA</td>
                        <td className="py-3 px-4">SCCs + DPA</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Change Notifications</h2>
                <p className="text-white/60 leading-relaxed">
                  We will update this page whenever we add or remove a subprocessor. If you have subscribed to notifications, we will inform you of material changes at least 30 days before they take effect, giving you the opportunity to object. To subscribe to subprocessor change notifications, please contact{' '}
                  <a href="mailto:dpo@mcleuker.com" className="text-white/80 underline hover:text-white">dpo@mcleuker.com</a>.
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
