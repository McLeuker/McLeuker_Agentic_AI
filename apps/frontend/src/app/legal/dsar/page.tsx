'use client';

import { useState } from "react";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function DSARPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    requestType: '',
    details: '',
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // In production, this would send to the backend API
    const mailtoLink = `mailto:dpo@mcleuker.com?subject=DSAR Request: ${encodeURIComponent(formData.requestType)}&body=${encodeURIComponent(
      `Name: ${formData.name}\nEmail: ${formData.email}\nRequest Type: ${formData.requestType}\n\nDetails:\n${formData.details}`
    )}`;
    window.location.href = mailtoLink;
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Data Subject Access Request
            </h1>
            <p className="text-white/50 mb-12">
              Exercise your rights under GDPR and the Loi Informatique et Libert&eacute;s
            </p>

            <div className="space-y-10">
              <section>
                <h2 className="text-xl font-medium text-white mb-4">Your Rights</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  Under the General Data Protection Regulation (GDPR) and the French Loi Informatique et Libert&eacute;s, you have the following rights regarding your personal data:
                </p>
                <div className="grid gap-3">
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium">Right of Access (Art. 15)</p>
                    <p className="text-white/60 text-sm">Obtain a copy of all personal data we hold about you.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium">Right to Rectification (Art. 16)</p>
                    <p className="text-white/60 text-sm">Request correction of inaccurate or incomplete personal data.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium">Right to Erasure (Art. 17)</p>
                    <p className="text-white/60 text-sm">Request deletion of your personal data (&ldquo;right to be forgotten&rdquo;).</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium">Right to Data Portability (Art. 20)</p>
                    <p className="text-white/60 text-sm">Receive your data in a structured, machine-readable format.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium">Right to Object (Art. 21)</p>
                    <p className="text-white/60 text-sm">Object to processing of your personal data for specific purposes.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium">Right to Restrict Processing (Art. 18)</p>
                    <p className="text-white/60 text-sm">Request limitation of processing of your personal data.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium">Right to Withdraw Consent</p>
                    <p className="text-white/60 text-sm">Withdraw your consent at any time where processing is based on consent.</p>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Submit a Request</h2>
                <p className="text-white/60 leading-relaxed mb-6">
                  To exercise any of these rights, please complete the form below or email us directly at{' '}
                  <a href="mailto:dpo@mcleuker.com" className="text-white/80 underline hover:text-white">dpo@mcleuker.com</a>.
                  We will respond to your request within 30 days, as required by GDPR.
                </p>

                {submitted ? (
                  <div className="p-6 rounded-lg bg-green-500/10 border border-green-500/20">
                    <p className="text-green-400 font-medium mb-2">Request Submitted</p>
                    <p className="text-white/60">Your email client should have opened with your request details. If it did not, please send your request directly to dpo@mcleuker.com. We will respond within 30 days.</p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">Full Name</label>
                      <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-4 py-3 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white placeholder-white/30 focus:outline-none focus:border-white/20"
                        placeholder="Your full name"
                      />
                    </div>
                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">Email Address</label>
                      <input
                        type="email"
                        required
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full px-4 py-3 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white placeholder-white/30 focus:outline-none focus:border-white/20"
                        placeholder="your@email.com"
                      />
                    </div>
                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">Request Type</label>
                      <select
                        required
                        value={formData.requestType}
                        onChange={(e) => setFormData({ ...formData, requestType: e.target.value })}
                        className="w-full px-4 py-3 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white focus:outline-none focus:border-white/20"
                      >
                        <option value="" className="bg-[#070707]">Select a request type</option>
                        <option value="Access" className="bg-[#070707]">Access my data</option>
                        <option value="Rectification" className="bg-[#070707]">Correct my data</option>
                        <option value="Erasure" className="bg-[#070707]">Delete my data</option>
                        <option value="Portability" className="bg-[#070707]">Export my data</option>
                        <option value="Objection" className="bg-[#070707]">Object to processing</option>
                        <option value="Restriction" className="bg-[#070707]">Restrict processing</option>
                        <option value="Withdraw Consent" className="bg-[#070707]">Withdraw consent</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">Details</label>
                      <textarea
                        required
                        rows={4}
                        value={formData.details}
                        onChange={(e) => setFormData({ ...formData, details: e.target.value })}
                        className="w-full px-4 py-3 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white placeholder-white/30 focus:outline-none focus:border-white/20 resize-none"
                        placeholder="Please describe your request in detail..."
                      />
                    </div>
                    <button
                      type="submit"
                      className="px-6 py-3 rounded-lg bg-white text-black font-medium hover:bg-white/90 transition-colors"
                    >
                      Submit Request
                    </button>
                  </form>
                )}
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Supervisory Authority</h2>
                <p className="text-white/60 leading-relaxed">
                  If you are not satisfied with our response to your request, you have the right to lodge a complaint with the French data protection authority (CNIL):{' '}
                  <a href="https://www.cnil.fr/fr/plaintes" target="_blank" rel="noopener noreferrer" className="text-white/80 underline hover:text-white">www.cnil.fr/fr/plaintes</a>.
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
