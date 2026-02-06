'use client';

import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function CookiePolicyPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Cookie Policy
            </h1>
            <p className="text-white/50 mb-12">
              Last updated: February 6, 2026
            </p>

            <div className="space-y-10">
              <section>
                <h2 className="text-xl font-medium text-white mb-4">1. What Are Cookies?</h2>
                <p className="text-white/60 leading-relaxed">
                  Cookies are small text files placed on your device when you visit a website. They are widely used to make websites work efficiently, provide information to the website operators, and improve the user experience. In accordance with the EU ePrivacy Directive and CNIL (Commission Nationale de l&apos;Informatique et des Libert&eacute;s) guidelines, we require your prior consent before placing non-essential cookies on your device.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">2. How We Use Cookies</h2>
                <p className="text-white/60 leading-relaxed mb-6">
                  We use the following categories of cookies on our platform:
                </p>
                <div className="overflow-x-auto mb-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Category</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Purpose</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Lawful Basis</th>
                        <th className="text-left py-3 px-4 text-white/80 font-medium">Duration</th>
                      </tr>
                    </thead>
                    <tbody className="text-white/60">
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Strictly Necessary</td>
                        <td className="py-3 px-4">Essential for the website to function (authentication, security, session management, cookie consent preferences)</td>
                        <td className="py-3 px-4">Exempt (no consent required)</td>
                        <td className="py-3 px-4">Session / 1 year</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Performance &amp; Analytics</td>
                        <td className="py-3 px-4">Understand how visitors use our site, measure performance, and identify issues</td>
                        <td className="py-3 px-4">Consent</td>
                        <td className="py-3 px-4">13 months max</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Functional</td>
                        <td className="py-3 px-4">Remember your preferences and settings (language, theme, display options)</td>
                        <td className="py-3 px-4">Consent</td>
                        <td className="py-3 px-4">13 months max</td>
                      </tr>
                      <tr className="border-b border-white/[0.06]">
                        <td className="py-3 px-4 font-medium text-white/70">Marketing</td>
                        <td className="py-3 px-4">Personalize marketing communications and measure campaign effectiveness</td>
                        <td className="py-3 px-4">Consent</td>
                        <td className="py-3 px-4">13 months max</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="text-white/60 leading-relaxed">
                  In compliance with CNIL guidelines, non-essential cookies have a maximum lifespan of 13 months, and your consent is re-requested at least every 13 months.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">3. Your Choices</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  When you first visit our website, a cookie consent banner will appear. You can choose to accept all cookies, reject all non-essential cookies, or customize your preferences. Both &ldquo;Accept All&rdquo; and &ldquo;Reject All&rdquo; options are presented with equal prominence, as required by CNIL guidelines. No non-essential cookies are set before you make your choice.
                </p>
                <p className="text-white/60 leading-relaxed mb-4">
                  You can change your cookie preferences at any time by clicking the &ldquo;Cookie Settings&rdquo; link in the footer of any page. You can also control cookies through your browser settings, though this may affect the functionality of our website.
                </p>
                <p className="text-white/60 leading-relaxed">
                  Refusing non-essential cookies will not affect the core functionality of our Service. You will still be able to use all essential features of the platform.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">4. Third-Party Cookies</h2>
                <p className="text-white/60 leading-relaxed">
                  Some cookies may be placed by third-party services we use, such as analytics providers. These third parties have their own privacy policies governing the use of their cookies. We only enable third-party cookies after you have given your explicit consent. This data is aggregated and anonymized to help us improve our services.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">5. Updates to This Policy</h2>
                <p className="text-white/60 leading-relaxed">
                  We may update this Cookie Policy from time to time to reflect changes in our practices or for legal, operational, or regulatory reasons. We will update the &ldquo;Last updated&rdquo; date at the top of this page.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">6. Contact Us</h2>
                <p className="text-white/60 leading-relaxed">
                  If you have questions about our use of cookies, please contact us at{' '}
                  <a href="mailto:dpo@mcleuker.com" className="text-white/80 underline hover:text-white">dpo@mcleuker.com</a>.
                  For more information about cookies and your rights, you can visit the{' '}
                  <a href="https://www.cnil.fr/fr/cookies-et-autres-traceurs" target="_blank" rel="noopener noreferrer" className="text-white/80 underline hover:text-white">CNIL website</a>.
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
