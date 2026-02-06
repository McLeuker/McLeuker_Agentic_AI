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
              Last updated: January 24, 2026
            </p>

            <div className="space-y-10">
              <section>
                <h2 className="text-xl font-medium text-white mb-4">1. Acceptance of Terms</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  By accessing or using McLeuker AI&apos;s services, website, or applications (collectively, the &ldquo;Services&rdquo;), 
                  you agree to be bound by these Terms of Service (&ldquo;Terms&rdquo;). If you do not agree to these Terms, 
                  please do not use our Services.
                </p>
                <p className="text-white/60 leading-relaxed">
                  We reserve the right to modify these Terms at any time. We will notify you of any material changes 
                  by posting the updated Terms on our website. Your continued use of the Services after such changes 
                  constitutes acceptance of the new Terms.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">2. Description of Services</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  McLeuker AI provides AI-powered fashion intelligence services, including but not limited to:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2 mb-4">
                  <li>Trend forecasting and analysis</li>
                  <li>Supplier research and evaluation</li>
                  <li>Market analysis and competitive intelligence</li>
                  <li>Sustainability consulting and reporting</li>
                  <li>AI-generated reports, data exports, and presentations</li>
                </ul>
                <p className="text-white/60 leading-relaxed">
                  The Services are provided on an &ldquo;as is&rdquo; and &ldquo;as available&rdquo; basis. We may modify, suspend, 
                  or discontinue any aspect of the Services at any time without prior notice.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">3. User Accounts</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  To access certain features of the Services, you must create an account. You agree to:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2">
                  <li>Provide accurate and complete registration information</li>
                  <li>Maintain the security of your account credentials</li>
                  <li>Notify us immediately of any unauthorized access</li>
                  <li>Accept responsibility for all activities under your account</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">4. Subscription and Payments</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  Some Services require a paid subscription. By subscribing, you agree to:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2 mb-4">
                  <li>Pay all fees associated with your chosen plan</li>
                  <li>Automatic renewal unless cancelled before the renewal date</li>
                  <li>Provide accurate payment information</li>
                </ul>
                <p className="text-white/60 leading-relaxed">
                  Refunds are handled on a case-by-case basis. Please contact our support team for refund requests.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">5. Intellectual Property</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  All content, features, and functionality of the Services are owned by McLeuker AI and protected 
                  by international copyright, trademark, and other intellectual property laws.
                </p>
                <p className="text-white/60 leading-relaxed">
                  You retain ownership of any content you submit to the Services. By submitting content, you grant 
                  us a non-exclusive license to use, process, and analyze such content to provide the Services.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">6. Acceptable Use</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  You agree not to:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2">
                  <li>Use the Services for any illegal purpose</li>
                  <li>Attempt to gain unauthorized access to our systems</li>
                  <li>Interfere with or disrupt the Services</li>
                  <li>Reverse engineer or attempt to extract source code</li>
                  <li>Use automated systems to access the Services without permission</li>
                  <li>Share your account credentials with third parties</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">7. Limitation of Liability</h2>
                <p className="text-white/60 leading-relaxed">
                  To the maximum extent permitted by law, McLeuker AI shall not be liable for any indirect, 
                  incidental, special, consequential, or punitive damages arising from your use of the Services. 
                  Our total liability shall not exceed the amount paid by you for the Services in the twelve months 
                  preceding the claim.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">8. Disclaimer of Warranties</h2>
                <p className="text-white/60 leading-relaxed">
                  THE SERVICES ARE PROVIDED &ldquo;AS IS&rdquo; WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
                  BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR 
                  NON-INFRINGEMENT. WE DO NOT GUARANTEE THAT THE SERVICES WILL BE UNINTERRUPTED, ERROR-FREE, 
                  OR COMPLETELY SECURE.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">9. Governing Law</h2>
                <p className="text-white/60 leading-relaxed">
                  These Terms shall be governed by and construed in accordance with the laws of the jurisdiction 
                  in which McLeuker AI operates, without regard to conflict of law principles.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">10. Contact Information</h2>
                <p className="text-white/60 leading-relaxed">
                  For questions about these Terms, please contact us at:
                </p>
                <p className="text-white mt-2">
                  <a href="mailto:contact@mcleuker.com" className="hover:underline">
                    contact@mcleuker.com
                  </a>
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
