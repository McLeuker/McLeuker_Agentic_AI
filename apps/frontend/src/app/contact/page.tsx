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
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-white/[0.08] flex items-center justify-center flex-shrink-0">
                    <Mail className="w-5 h-5 text-white/70" />
                  </div>
                  <div>
                    <h3 className="text-white/[0.92] font-medium mb-1">Email</h3>
                    <a href="mailto:hello@mcleukerai.com" className="text-white/55 hover:text-white transition-colors">
                      hello@mcleukerai.com
                    </a>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-white/[0.08] flex items-center justify-center flex-shrink-0">
                    <MessageSquare className="w-5 h-5 text-white/70" />
                  </div>
                  <div>
                    <h3 className="text-white/[0.92] font-medium mb-1">Support</h3>
                    <p className="text-white/55">
                      Available Monday - Friday, 9am - 6pm CET
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-white/[0.08] flex items-center justify-center flex-shrink-0">
                    <MapPin className="w-5 h-5 text-white/70" />
                  </div>
                  <div>
                    <h3 className="text-white/[0.92] font-medium mb-1">Location</h3>
                    <p className="text-white/55">
                      Amsterdam, Netherlands
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Form */}
            <div className={cn(
              "p-8 rounded-[20px]",
              "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
              "border border-white/[0.08]"
            )}>
              {submitted ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 rounded-full bg-white/[0.08] flex items-center justify-center mx-auto mb-6">
                    <Mail className="w-8 h-8 text-white/70" />
                  </div>
                  <h3 className="text-xl font-medium text-white/[0.92] mb-2">
                    Message Sent!
                  </h3>
                  <p className="text-white/55 mb-6">
                    We'll get back to you as soon as possible.
                  </p>
                  <button
                    onClick={() => setSubmitted(false)}
                    className="text-sm text-white/70 hover:text-white transition-colors"
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
                        "focus:outline-none focus:border-white/[0.18]"
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
                        "focus:outline-none focus:border-white/[0.18]"
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
                        "focus:outline-none focus:border-white/[0.18]"
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
                        "focus:outline-none focus:border-white/[0.18]"
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
                      "bg-white text-black font-medium",
                      "hover:bg-white/90 transition-colors",
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
      </section>

      <Footer />
    </div>
  );
}
