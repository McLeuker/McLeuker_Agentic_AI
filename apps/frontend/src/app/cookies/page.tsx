'use client';

import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function CookiesPage() {
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
              Last updated: January 24, 2026
            </p>

            <div className="space-y-10">
              <section>
                <h2 className="text-xl font-medium text-white mb-4">1. What Are Cookies</h2>
                <p className="text-white/60 leading-relaxed">
                  Cookies are small text files that are stored on your device when you visit a website. 
                  They help websites remember your preferences, understand how you use the site, and 
                  improve your overall experience.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">2. How We Use Cookies</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  McLeuker AI uses cookies for the following purposes:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2">
                  <li><strong className="text-white/80">Essential cookies:</strong> Required for the website to function properly, including authentication and security.</li>
                  <li><strong className="text-white/80">Preference cookies:</strong> Remember your settings and preferences (e.g., selected domain, theme).</li>
                  <li><strong className="text-white/80">Analytics cookies:</strong> Help us understand how visitors interact with our website to improve functionality.</li>
                  <li><strong className="text-white/80">Performance cookies:</strong> Monitor site performance and identify technical issues.</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">3. Types of Cookies We Use</h2>
                <div className="space-y-4">
                  <div className="bg-[#0D0D0D] rounded-xl p-5 border border-white/[0.05]">
                    <h4 className="text-white font-medium mb-2">Session Cookies</h4>
                    <p className="text-white/60 text-sm">
                      Temporary cookies that expire when you close your browser. Used to maintain your session while using the platform.
                    </p>
                  </div>
                  <div className="bg-[#0D0D0D] rounded-xl p-5 border border-white/[0.05]">
                    <h4 className="text-white font-medium mb-2">Persistent Cookies</h4>
                    <p className="text-white/60 text-sm">
                      Remain on your device for a set period. Used to remember your preferences and provide a personalized experience.
                    </p>
                  </div>
                  <div className="bg-[#0D0D0D] rounded-xl p-5 border border-white/[0.05]">
                    <h4 className="text-white font-medium mb-2">Third-Party Cookies</h4>
                    <p className="text-white/60 text-sm">
                      Set by services we use for analytics and performance monitoring. We only work with trusted providers who comply with privacy regulations.
                    </p>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">4. Managing Cookies</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  You can control and manage cookies through your browser settings. Most browsers allow you to:
                </p>
                <ul className="list-disc list-inside text-white/60 space-y-2">
                  <li>View what cookies are stored and delete them individually</li>
                  <li>Block third-party cookies</li>
                  <li>Block cookies from specific sites</li>
                  <li>Block all cookies</li>
                  <li>Delete all cookies when you close your browser</li>
                </ul>
                <p className="text-white/60 leading-relaxed mt-4">
                  Please note that blocking or deleting cookies may affect the functionality of our website 
                  and your ability to use certain features.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">5. Analytics Services</h2>
                <p className="text-white/60 leading-relaxed">
                  We use analytics services to understand how visitors interact with our website. These services 
                  may collect information about your visit, including pages viewed, time spent, and how you 
                  arrived at our site. This data is aggregated and anonymized to help us improve our services.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">6. Updates to This Policy</h2>
                <p className="text-white/60 leading-relaxed">
                  We may update this Cookie Policy from time to time to reflect changes in our practices or 
                  for legal, operational, or regulatory reasons. We encourage you to review this page 
                  periodically for the latest information.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">7. Contact Us</h2>
                <p className="text-white/60 leading-relaxed">
                  If you have questions about our use of cookies, please contact us at:
                </p>
                <p className="text-white mt-2">
                  <a href="mailto:info@mcleuker.com" className="hover:underline">
                    info@mcleuker.com
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
