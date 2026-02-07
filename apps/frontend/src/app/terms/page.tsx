'use client';

import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Terms of Service
            </h1>
            <p className="text-white/50 mb-12">
              Last updated: February 6, 2026
            </p>

            <div className="space-y-10">
              <section>
                <h2 className="text-xl font-medium text-white mb-4">1. Acceptance of Terms</h2>
                <p className="text-white/60 leading-relaxed">
                  By accessing or using the McLeuker AI platform and services (the &ldquo;Service&rdquo;), you agree to be bound by these Terms of Service (&ldquo;Terms&rdquo;). If you do not agree to these Terms, you may not use the Service. These Terms constitute a legally binding agreement between you and McLeuker AI, governed by the laws of France.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">2. Eligibility</h2>
                <p className="text-white/60 leading-relaxed">
                  You must be at least 15 years old to use the Service. In France, users aged 15 or older may consent on their own in accordance with the Loi Informatique et Libert&eacute;s. For users under 15, parental or guardian consent is required. By using the Service, you represent and warrant that you meet these requirements.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">3. Your Account</h2>
                <p className="text-white/60 leading-relaxed">
                  You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You must provide accurate and complete registration information and notify us immediately of any unauthorized access. We are not liable for any loss arising from unauthorized use of your account.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">4. Description of the Service</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  McLeuker AI provides an agentive AI platform for fashion intelligence professionals. The Service includes AI-powered analysis, trend forecasting, supplier research, market analysis, sustainability insights, document generation, and the ability to connect third-party accounts for the agent to act on your behalf.
                </p>
                <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                  <p className="text-white/80 font-medium mb-2">Important Notice About AI</p>
                  <p className="text-white/60">
                    The Service uses artificial intelligence, which may occasionally produce inaccurate, incomplete, or misleading information (&ldquo;hallucinations&rdquo;). You are responsible for reviewing and verifying all AI-generated output before relying on it for any purpose. The Service does not provide medical, legal, or financial advice.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">5. User Responsibilities &amp; Agent Actions</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  When using the Service, you agree to the following responsibilities:
                </p>
                <ul className="space-y-3 text-white/60">
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Authority:</strong> You must ensure you have the right to connect third-party accounts and instruct the agent to perform actions on your behalf.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Review &amp; Approval:</strong> You must review and approve all high-impact actions suggested by the agent before they are executed (e.g., sending emails, deleting files, making purchases).</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Compliance:</strong> You must comply with our <Link href="/legal/aup" className="text-white/80 underline hover:text-white">Acceptable Use Policy</Link> and all applicable laws and regulations.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Accuracy:</strong> You must provide accurate and complete information when creating your account and using the Service.</span>
                  </li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">6. Subscriptions &amp; Payment</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  Certain features of the Service require a paid subscription. By subscribing, you agree to pay all fees associated with your chosen plan. Subscriptions renew automatically unless cancelled before the renewal date. You may cancel your subscription at any time, and cancellation will take effect at the end of the current billing period.
                </p>
                <p className="text-white/60 leading-relaxed">
                  We reserve the right to change our pricing with reasonable notice. Refund requests are handled on a case-by-case basis. Please contact our support team for assistance.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">7. Intellectual Property</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  <strong className="text-white/80">Your Content:</strong> You retain all ownership rights to the content you provide to the Service (&ldquo;User Content&rdquo;). By using the Service, you grant us a limited, non-exclusive license to process your User Content solely to provide and improve the Service. We do not use your User Content to train our AI models.
                </p>
                <p className="text-white/60 leading-relaxed">
                  <strong className="text-white/80">Our Service:</strong> All content, features, functionality, technology, software, algorithms, and designs of the Service are owned by McLeuker AI and protected by international copyright, trademark, and other intellectual property laws. Nothing in these Terms grants you any right to use our trademarks, logos, or brand features.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">8. Acceptable Use</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  You agree not to use the Service for any illegal purpose, attempt to gain unauthorized access to our systems, interfere with or disrupt the Service, reverse engineer or extract source code, use automated systems without permission, or share your account credentials with third parties. Full details are available in our <Link href="/legal/aup" className="text-white/80 underline hover:text-white">Acceptable Use Policy</Link>.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">9. Disclaimers</h2>
                <p className="text-white/60 leading-relaxed">
                  The Service is provided &ldquo;as is&rdquo; and &ldquo;as available&rdquo; without warranties of any kind, whether express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement. We do not warrant that the Service will be uninterrupted, error-free, or completely secure. We do not warrant the accuracy, completeness, or reliability of any AI-generated output.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">10. Limitation of Liability</h2>
                <p className="text-white/60 leading-relaxed">
                  To the fullest extent permitted by applicable law, McLeuker AI shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenues, data, use, goodwill, or other intangible losses resulting from your use of the Service. Our total liability shall not exceed the amount paid by you for the Service in the twelve months preceding the claim. Nothing in these Terms limits our liability for fraud, gross negligence, or any liability that cannot be excluded under applicable law.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">11. Termination</h2>
                <p className="text-white/60 leading-relaxed">
                  We may suspend or terminate your access to the Service at any time for violation of these Terms or our Acceptable Use Policy. You may terminate your account at any time through your account settings or by contacting us. Upon termination, your right to use the Service will immediately cease, and we will handle your data in accordance with our <Link href="/privacy" className="text-white/80 underline hover:text-white">Privacy Policy</Link>.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">12. Governing Law &amp; Jurisdiction</h2>
                <p className="text-white/60 leading-relaxed">
                  These Terms are governed by and construed in accordance with the laws of France. Any disputes arising from or relating to these Terms or the Service shall be subject to the exclusive jurisdiction of the courts of Paris, France, without prejudice to any mandatory consumer protection rules that may apply under your local law.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">13. Changes to These Terms</h2>
                <p className="text-white/60 leading-relaxed">
                  We may update these Terms from time to time. We will notify you of material changes by posting the updated Terms on this page and updating the &ldquo;Last updated&rdquo; date. Your continued use of the Service after such changes constitutes your acceptance of the new Terms.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">14. Contact Us</h2>
                <p className="text-white/60 leading-relaxed">
                  For any questions about these Terms, please contact us at{' '}
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
