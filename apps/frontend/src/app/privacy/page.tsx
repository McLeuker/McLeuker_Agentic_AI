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
              Last updated: January 24, 2026
            </p>

            <div className="space-y-10">
              <section>
                <h2 className="text-xl font-medium text-white mb-4">1. Introduction</h2>
                <p className="text-white/60 leading-relaxed">
                  McLeuker AI (&ldquo;we&rdquo;, &ldquo;our&rdquo;, or &ldquo;us&rdquo;) respects your privacy and is committed to protecting 
                  your personal data. This Privacy Policy explains how we collect, use, disclose, and 
                  safeguard your information when you use our website and services.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">2. Information We Collect</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  We collect information you provide directly to us, including:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2 mb-4">
                  <li>Account information (name, email address, password)</li>
                  <li>Profile information (company name, role, preferences)</li>
                  <li>Payment information (processed securely by our payment providers)</li>
                  <li>Content you submit (research prompts, uploaded files)</li>
                  <li>Communications with us (support requests, feedback)</li>
                </ul>
                <p className="text-white/60 leading-relaxed mb-4">
                  We also automatically collect certain information when you use our Services:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2">
                  <li>Device information (browser type, operating system)</li>
                  <li>Usage data (pages visited, features used, time spent)</li>
                  <li>IP address and approximate location</li>
                  <li>Cookies and similar tracking technologies</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">3. How We Use Your Information</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  We use the information we collect to:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2">
                  <li>Provide, maintain, and improve our Services</li>
                  <li>Process transactions and send related information</li>
                  <li>Send technical notices, updates, and support messages</li>
                  <li>Respond to your comments, questions, and requests</li>
                  <li>Analyze usage patterns to improve user experience</li>
                  <li>Detect, investigate, and prevent security incidents</li>
                  <li>Comply with legal obligations</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">4. Information Sharing</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  We do not sell your personal information. We may share your information with:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2">
                  <li>Service providers who assist in operating our Services</li>
                  <li>Business partners with your consent</li>
                  <li>Legal authorities when required by law</li>
                  <li>Successors in the event of a merger or acquisition</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">5. Data Security</h2>
                <p className="text-white/60 leading-relaxed">
                  We implement appropriate technical and organizational measures to protect your personal 
                  information against unauthorized access, alteration, disclosure, or destruction. These 
                  measures include encryption, access controls, and regular security assessments. However, 
                  no method of transmission over the Internet is 100% secure.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">6. Data Retention</h2>
                <p className="text-white/60 leading-relaxed">
                  We retain your personal information for as long as necessary to provide our Services 
                  and fulfill the purposes described in this Privacy Policy. When you delete your account, 
                  we will delete or anonymize your personal information within 30 days, except where 
                  retention is required by law.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">7. Your Rights</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  Depending on your location, you may have the following rights:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2">
                  <li>Access your personal information</li>
                  <li>Correct inaccurate data</li>
                  <li>Request deletion of your data</li>
                  <li>Object to processing of your data</li>
                  <li>Request data portability</li>
                  <li>Withdraw consent at any time</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">8. Cookies</h2>
                <p className="text-white/60 leading-relaxed">
                  We use cookies and similar tracking technologies to collect and store information about 
                  your interactions with our Services. You can control cookie preferences through your 
                  browser settings. Disabling certain cookies may affect the functionality of our Services.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">9. International Transfers</h2>
                <p className="text-white/60 leading-relaxed">
                  Your information may be transferred to and processed in countries other than your own. 
                  We ensure appropriate safeguards are in place to protect your information in accordance 
                  with this Privacy Policy.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">10. Children&apos;s Privacy</h2>
                <p className="text-white/60 leading-relaxed">
                  Our Services are not intended for individuals under the age of 16. We do not knowingly 
                  collect personal information from children. If you believe we have collected information 
                  from a child, please contact us immediately.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">11. Changes to This Policy</h2>
                <p className="text-white/60 leading-relaxed">
                  We may update this Privacy Policy from time to time. We will notify you of any material 
                  changes by posting the new Privacy Policy on this page and updating the &ldquo;Last updated&rdquo; date.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">12. Contact Us</h2>
                <p className="text-white/60 leading-relaxed">
                  If you have questions about this Privacy Policy or our privacy practices, please contact us at:
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
