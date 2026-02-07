'use client';

import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Privacy Policy
            </h1>
            <p className="text-white/50 mb-12">
              Last updated: February 6, 2026
            </p>

            <div className="space-y-10">
              {/* 1. Introduction */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">1. Introduction</h2>
                <p className="text-white/60 leading-relaxed">
                  Welcome to McLeuker AI (&ldquo;we&rdquo;, &ldquo;our&rdquo;, or &ldquo;us&rdquo;). We are committed to protecting your personal data and respecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our agentive AI platform and services (the &ldquo;Service&rdquo;). This policy is designed to comply with the EU General Data Protection Regulation (GDPR, Regulation (EU) 2016/679) and France&apos;s Data Protection Act (Loi Informatique et Libert&eacute;s, Loi n&deg;78-17).
                </p>
              </section>

              {/* 2. Data We Collect */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">2. What Personal Data We Collect</h2>
                <p className="text-white/60 leading-relaxed mb-6">
                  We collect information necessary to provide and improve our Service. The following table describes the categories of data we process:
                </p>
                <div className="overflow-x-auto mb-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Data Category</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Examples</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Purpose</th>
                      </tr>
                    </thead>
                    <tbody className="text-white/60">
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Account Information</td>
                        <td className="py-3 px-4">Name, email address, password</td>
                        <td className="py-3 px-4">Create and manage your account</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Profile Information</td>
                        <td className="py-3 px-4">Company name, role, preferences</td>
                        <td className="py-3 px-4">Personalize your experience</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">User Content</td>
                        <td className="py-3 px-4">Prompts, uploaded files, content you provide to the agent</td>
                        <td className="py-3 px-4">Execute your requests and provide the Service</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Connected Account Data</td>
                        <td className="py-3 px-4">Data from third-party accounts you connect (e.g., emails, calendar events)</td>
                        <td className="py-3 px-4">Allow the agent to perform actions on your behalf</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Payment Information</td>
                        <td className="py-3 px-4">Billing details (processed by Stripe)</td>
                        <td className="py-3 px-4">Process subscription payments</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Usage &amp; Telemetry Data</td>
                        <td className="py-3 px-4">Pages visited, features used, agent actions, error logs</td>
                        <td className="py-3 px-4">Security, debugging, improving reliability</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Device Information</td>
                        <td className="py-3 px-4">IP address, browser type, operating system</td>
                        <td className="py-3 px-4">Security and analytics</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              {/* 3. Lawful Basis */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">3. How We Use Your Data &amp; Lawful Basis</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  Our processing of your personal data is based on the following legal grounds under GDPR Article 6:
                </p>
                <ul className="space-y-3 text-white/60 mb-6">
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Performance of a Contract (Art. 6(1)(b)):</strong> We process your Account Information, User Content, and Connected Account Data to provide the core functionality of the Service you have requested.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Legitimate Interests (Art. 6(1)(f)):</strong> We process Usage &amp; Telemetry Data and Device Information for security, fraud prevention, and to analyze and improve the performance of our Service. We have conducted a balancing test to ensure our interests do not override your fundamental rights.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Consent (Art. 6(1)(a)):</strong> We rely on your consent for sending marketing communications and for the use of non-essential cookies and trackers.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Legal Obligation (Art. 6(1)(c)):</strong> We may process your data to comply with legal requirements, such as financial regulations or requests from law enforcement.</span>
                  </li>
                </ul>
                <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                  <p className="text-white/80 font-medium mb-2">Our Policy on Model Training</p>
                  <p className="text-white/60">
                    We do not use your User Content, files, or Connected Account Data to train or fine-tune our foundation AI models. We may use limited, aggregated, and de-identified logs and feedback (e.g., error reports, safety flags) to improve reliability and security&mdash;without training foundation models on your content.
                  </p>
                </div>
              </section>

              {/* 4. Acting on Your Behalf */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">4. Acting on Your Behalf &amp; Connected Accounts</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  When you connect a third-party account (e.g., Google, email, calendar), you authorize the Service to access and perform actions in that account strictly to provide the features you request. We do not take high-impact actions (sending messages, deleting data, purchases) without asking you to confirm.
                </p>
                <p className="text-white/60 leading-relaxed mb-4">
                  We store access tokens securely to maintain your connection. You can revoke access at any time in the app or with the provider (e.g., Google). After revocation, we stop accessing the connected account.
                </p>
                <p className="text-white/60 leading-relaxed">
                  If you ask the agent to email someone, we process recipients&apos; contact details and message content as instructed by you, solely to send the communication.
                </p>
              </section>

              {/* 5. Data Sharing */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">5. Data Sharing &amp; Subprocessors</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  We do not sell your personal data. We share information only with trusted service providers (subprocessors) who help us operate our Service under strict data processing agreements. A full list is available on our{' '}
                  <Link href="/legal/subprocessors" className="text-white/80 underline hover:text-white">Subprocessors page</Link>.
                </p>
                <p className="text-white/60 leading-relaxed">
                  We may also disclose your information to legal authorities when required by law, or to successors in the event of a merger or acquisition.
                </p>
              </section>

              {/* 6. International Transfers */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">6. International Data Transfers</h2>
                <p className="text-white/60 leading-relaxed">
                  Your data may be processed outside of the European Economic Area (EEA). Where such transfers occur, we ensure they are protected by appropriate safeguards, primarily through the use of Standard Contractual Clauses (SCCs) approved by the European Commission, combined with supplementary measures where necessary.
                </p>
              </section>

              {/* 7. Data Retention */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">7. Data Retention</h2>
                <p className="text-white/60 leading-relaxed mb-6">
                  We retain your data only for as long as necessary to fulfill the purposes described in this policy:
                </p>
                <div className="overflow-x-auto mb-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Data Type</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Retention Period</th>
                      </tr>
                    </thead>
                    <tbody className="text-white/60">
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4">User Content (prompts, files)</td>
                        <td className="py-3 px-4">30 days (user can delete anytime)</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4">Security &amp; Audit Logs</td>
                        <td className="py-3 px-4">12 months</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4">Account Information</td>
                        <td className="py-3 px-4">Duration of account existence</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4">Backups</td>
                        <td className="py-3 px-4">30 days</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="text-white/60 leading-relaxed">
                  When you delete your account, we will delete or anonymize your personal information within 30 days, except where retention is required by law.
                </p>
              </section>

              {/* 8. Your Rights */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">8. Your Data Protection Rights</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  Under the GDPR, you have the following rights regarding your personal data:
                </p>
                <ul className="space-y-3 text-white/60 mb-4">
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Right of Access:</strong> Obtain a copy of the personal data we hold about you.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Right to Rectification:</strong> Correct any inaccurate or incomplete personal data.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Right to Erasure:</strong> Request deletion of your personal data.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Right to Restriction:</strong> Restrict the processing of your personal data.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Right to Data Portability:</strong> Receive your data in a structured, machine-readable format.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Right to Object:</strong> Object to processing based on legitimate interests.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Right to Withdraw Consent:</strong> Withdraw consent at any time for processing based on consent.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Right to Lodge a Complaint:</strong> File a complaint with the CNIL (Commission Nationale de l&apos;Informatique et des Libert&eacute;s) at <a href="https://www.cnil.fr" target="_blank" rel="noopener noreferrer" className="underline hover:text-white">www.cnil.fr</a>.</span>
                  </li>
                </ul>
                <p className="text-white/60 leading-relaxed">
                  To exercise these rights, please visit our{' '}
                  <Link href="/legal/dsar" className="text-white/80 underline hover:text-white">Data Subject Request page</Link>{' '}
                  or contact us at{' '}
                  <a href="mailto:dpo@mcleuker.com" className="text-white/80 underline hover:text-white">dpo@mcleuker.com</a>.
                </p>
              </section>

              {/* 9. Automated Decision-Making */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">9. Automated Decision-Making</h2>
                <p className="text-white/60 leading-relaxed">
                  Our AI agent assists you in performing tasks but does not make decisions with legal or similarly significant effects on you without your explicit confirmation. You always retain the ability to review, approve, or reject any action the agent proposes.
                </p>
              </section>

              {/* 10. Children's Privacy */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">10. Children&apos;s Privacy</h2>
                <p className="text-white/60 leading-relaxed">
                  Our Service is not intended for individuals under the age of 15. In accordance with French law, users aged 15 or older may consent on their own. For users under 15, joint consent with a parent or guardian is required. We do not knowingly collect personal information from children under 15. If you believe we have collected information from a child, please contact us immediately.
                </p>
              </section>

              {/* 11. Cookies */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">11. Cookies &amp; Trackers</h2>
                <p className="text-white/60 leading-relaxed">
                  We use cookies and similar tracking technologies. Non-essential cookies require your prior consent, which you can provide or refuse through our cookie banner. Refusing non-essential cookies is as easy as accepting them. For full details, please see our{' '}
                  <Link href="/cookies" className="text-white/80 underline hover:text-white">Cookie Policy</Link>.
                </p>
              </section>

              {/* 12. Changes */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">12. Changes to This Policy</h2>
                <p className="text-white/60 leading-relaxed">
                  We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new Privacy Policy on this page and updating the &ldquo;Last updated&rdquo; date. We encourage you to review this page periodically.
                </p>
              </section>

              {/* 13. Contact */}
              <section>
                <h2 className="text-xl font-medium text-white mb-4">13. Contact Us</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  If you have questions about this Privacy Policy or our privacy practices, please contact our Data Protection Officer:
                </p>
                <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/60">
                  <p><strong className="text-white/80">Email:</strong>{' '}
                    <a href="mailto:dpo@mcleuker.com" className="underline hover:text-white">dpo@mcleuker.com</a>
                  </p>
                  <p className="mt-2"><strong className="text-white/80">Supervisory Authority:</strong>{' '}
                    <a href="https://www.cnil.fr" target="_blank" rel="noopener noreferrer" className="underline hover:text-white">CNIL (Commission Nationale de l&apos;Informatique et des Libert&eacute;s)</a>
                  </p>
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
