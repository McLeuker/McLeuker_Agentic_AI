'use client';

import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function AcceptableUsePolicyPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Acceptable Use Policy
            </h1>
            <p className="text-white/50 mb-12">
              Last updated: February 6, 2026
            </p>

            <div className="space-y-10">
              <section>
                <h2 className="text-xl font-medium text-white mb-4">1. Purpose</h2>
                <p className="text-white/60 leading-relaxed">
                  This Acceptable Use Policy (&ldquo;AUP&rdquo;) defines the rules and boundaries for using the McLeuker AI platform. It supplements our <Link href="/terms" className="text-white/80 underline hover:text-white">Terms of Service</Link> and applies to all users. Our goal is to ensure a safe, ethical, and productive environment for everyone.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">2. Prohibited Uses</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  You may not use the McLeuker AI platform to:
                </p>
                <ul className="space-y-3 text-white/60">
                  <li className="flex gap-3">
                    <span className="text-red-400/60 shrink-0">&times;</span>
                    <span>Generate, distribute, or facilitate illegal content, including but not limited to child sexual abuse material, terrorism-related content, or content that incites violence or hatred.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-red-400/60 shrink-0">&times;</span>
                    <span>Engage in fraud, phishing, social engineering, or any form of deception targeting individuals or organizations.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-red-400/60 shrink-0">&times;</span>
                    <span>Develop, distribute, or deploy malware, ransomware, or any other malicious software.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-red-400/60 shrink-0">&times;</span>
                    <span>Attempt to reverse engineer, extract, or replicate our AI models, algorithms, or proprietary technology.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-red-400/60 shrink-0">&times;</span>
                    <span>Circumvent, disable, or interfere with any security features, rate limits, or access controls of the platform.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-red-400/60 shrink-0">&times;</span>
                    <span>Use the platform for unauthorized surveillance, profiling, or tracking of individuals.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-red-400/60 shrink-0">&times;</span>
                    <span>Impersonate another person, entity, or AI system, or misrepresent your affiliation with any entity.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-red-400/60 shrink-0">&times;</span>
                    <span>Use the platform to generate spam, unsolicited communications, or misleading content at scale.</span>
                  </li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">3. Agent-Specific Rules</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  When using the McLeuker AI agent to perform actions on your behalf, you must:
                </p>
                <ul className="space-y-3 text-white/60">
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span>Only connect third-party accounts that you own or have explicit authorization to use.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span>Review all high-impact actions (sending emails, making purchases, deleting data) before approving them.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span>Not instruct the agent to perform actions that violate any third-party service&apos;s terms of service.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span>Not use the agent to automate actions that would constitute harassment, stalking, or abuse.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span>Accept responsibility for all actions performed by the agent on your behalf.</span>
                  </li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">4. Enforcement</h2>
                <p className="text-white/60 leading-relaxed">
                  We reserve the right to investigate and take appropriate action against any user who violates this AUP. Actions may include, but are not limited to: issuing warnings, temporarily suspending access, permanently terminating accounts, and reporting violations to law enforcement authorities where required by law.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">5. Reporting Violations</h2>
                <p className="text-white/60 leading-relaxed">
                  If you become aware of any violation of this AUP, please report it to{' '}
                  <a href="mailto:abuse@mcleuker.com" className="text-white/80 underline hover:text-white">abuse@mcleuker.com</a>.
                  We take all reports seriously and will investigate promptly.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">6. Contact Us</h2>
                <p className="text-white/60 leading-relaxed">
                  For questions about this Acceptable Use Policy, please contact us at{' '}
                  <a href="mailto:legal@mcleuker.com" className="text-white/80 underline hover:text-white">legal@mcleuker.com</a>.
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
