'use client';

import { useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { ArrowRight, Mail, MapPin, MessageSquare } from "lucide-react";

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    message: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsSubmitting(false);
    setSubmitted(true);
    setFormData({ name: "", email: "", company: "", message: "" });
  };

  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      
      {/* Spacer for fixed nav */}
      <div className="h-16 lg:h-[72px]" />

      {/* Hero Section */}
      <section className="pt-24 lg:pt-32 pb-16 lg:pb-24 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-xs sm:text-sm text-white/50 uppercase tracking-[0.2em] mb-4">
              Contact Us
            </p>
            <h1 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-6 leading-[1.1]">
              Let's Talk
            </h1>
            <p className="text-white/65 text-lg lg:text-xl max-w-2xl mx-auto">
              Have questions about McLeuker AI? We'd love to hear from you.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-16 lg:py-24 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 max-w-6xl mx-auto">
            {/* Contact Info */}
            <div>
              <h2 className="font-editorial text-2xl md:text-3xl text-white/[0.92] mb-6">
                Get in Touch
              </h2>
              <p className="text-white/65 leading-relaxed mb-10">
                Whether you're interested in our platform, have questions about pricing, 
                or want to explore a partnership, we're here to help.
              </p>

              <div className="space-y-6">
                {/* Email - Updated */}
                <div className={cn(
                  "flex items-start gap-4 p-4 rounded-xl",
                  "mcleuker-bubble mcleuker-bubble-v1"
                )}>
                  <div className="w-12 h-12 rounded-lg bg-[#177b57]/20 flex items-center justify-center flex-shrink-0 relative z-10">
                    <Mail className="w-5 h-5 text-[#4ade80]" />
                  </div>
                  <div className="relative z-10">
                    <h3 className="text-white/[0.92] font-medium mb-1">Email</h3>
                    <a href="mailto:contact@mcluker.com" className="text-[#4ade80] hover:text-[#86efac] transition-colors">
                      contact@mcluker.com
                    </a>
                  </div>
                </div>

                {/* Support */}
                <div className={cn(
                  "flex items-start gap-4 p-4 rounded-xl",
                  "mcleuker-bubble mcleuker-bubble-v2"
                )}>
                  <div className="w-12 h-12 rounded-lg bg-[#177b57]/20 flex items-center justify-center flex-shrink-0 relative z-10">
                    <MessageSquare className="w-5 h-5 text-[#4ade80]" />
                  </div>
                  <div className="relative z-10">
                    <h3 className="text-white/[0.92] font-medium mb-1">Support</h3>
                    <p className="text-white/55">
                      Available Monday - Friday, 9am - 6pm CET
                    </p>
                  </div>
                </div>

                {/* Location - Updated */}
                <div className={cn(
                  "flex items-start gap-4 p-4 rounded-xl",
                  "mcleuker-bubble mcleuker-bubble-v3"
                )}>
                  <div className="w-12 h-12 rounded-lg bg-[#177b57]/20 flex items-center justify-center flex-shrink-0 relative z-10">
                    <MapPin className="w-5 h-5 text-[#4ade80]" />
                  </div>
                  <div className="relative z-10">
                    <h3 className="text-white/[0.92] font-medium mb-1">Location</h3>
                    <p className="text-white/55">
                      Paris, France
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Form - Updated with green accents */}
            <div className={cn(
              "p-8 rounded-[20px]",
              "mcleuker-bubble mcleuker-bubble-v4"
            )}>
              <div className="relative z-10">
                {submitted ? (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 rounded-full bg-[#177b57]/20 flex items-center justify-center mx-auto mb-6">
                      <Mail className="w-8 h-8 text-[#4ade80]" />
                    </div>
                    <h3 className="text-xl font-medium text-white/[0.92] mb-2">
                      Message Sent!
                    </h3>
                    <p className="text-white/55 mb-6">
                      We'll get back to you as soon as possible.
                    </p>
                    <button
                      onClick={() => setSubmitted(false)}
                      className="text-sm text-[#4ade80] hover:text-[#86efac] transition-colors"
                    >
                      Send another message
                    </button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                      <label className="block text-sm text-white/70 mb-2">Name</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className={cn(
                          "w-full h-12 px-4 rounded-lg",
                          "bg-white/[0.06] border border-white/[0.10]",
                          "text-white placeholder:text-white/40",
                          "focus:outline-none focus:border-[#177b57]/50 focus:ring-1 focus:ring-[#177b57]/20"
                        )}
                        placeholder="Your name"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-white/70 mb-2">Email</label>
                      <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className={cn(
                          "w-full h-12 px-4 rounded-lg",
                          "bg-white/[0.06] border border-white/[0.10]",
                          "text-white placeholder:text-white/40",
                          "focus:outline-none focus:border-[#177b57]/50 focus:ring-1 focus:ring-[#177b57]/20"
                        )}
                        placeholder="your@email.com"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-white/70 mb-2">Company (optional)</label>
                      <input
                        type="text"
                        value={formData.company}
                        onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                        className={cn(
                          "w-full h-12 px-4 rounded-lg",
                          "bg-white/[0.06] border border-white/[0.10]",
                          "text-white placeholder:text-white/40",
                          "focus:outline-none focus:border-[#177b57]/50 focus:ring-1 focus:ring-[#177b57]/20"
                        )}
                        placeholder="Your company"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-white/70 mb-2">Message</label>
                      <textarea
                        value={formData.message}
                        onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                        className={cn(
                          "w-full h-32 px-4 py-3 rounded-lg resize-none",
                          "bg-white/[0.06] border border-white/[0.10]",
                          "text-white placeholder:text-white/40",
                          "focus:outline-none focus:border-[#177b57]/50 focus:ring-1 focus:ring-[#177b57]/20"
                        )}
                        placeholder="How can we help?"
                        required
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className={cn(
                        "w-full flex items-center justify-center gap-2 px-6 py-3 rounded-full",
                        "bg-gradient-to-r from-[#177b57] to-[#266a2e] text-white font-medium",
                        "hover:from-[#1a8a62] hover:to-[#2d7a35] transition-all",
                        "disabled:opacity-50"
                      )}
                    >
                      {isSubmitting ? "Sending..." : "Send Message"}
                      {!isSubmitting && <ArrowRight className="w-4 h-4" />}
                    </button>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
