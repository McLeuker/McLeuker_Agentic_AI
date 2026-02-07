'use client';

import { useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import {
  ArrowRight, Mail, MapPin, MessageSquare, Clock, Send,
  Linkedin, Instagram, Globe, CheckCircle
} from "lucide-react";

const contactMethods = [
  {
    icon: Mail,
    title: "Email Us",
    desc: "For general inquiries and partnerships",
    value: "contact@mcleuker.com",
    href: "mailto:contact@mcleuker.com",
    color: "#C9A96E",
  },
  {
    icon: MessageSquare,
    title: "Support",
    desc: "Technical help and account questions",
    value: "Monday – Friday, 9am – 6pm CET",
    href: null,
    color: "#8ECAE6",
  },
  {
    icon: MapPin,
    title: "Location",
    desc: "Our headquarters",
    value: "Paris, France",
    href: null,
    color: "#A78BFA",
  },
  {
    icon: Clock,
    title: "Response Time",
    desc: "We aim to reply within",
    value: "24 hours",
    href: null,
    color: "#6b9b8a",
  },
];

const socialLinks = [
  { name: "LinkedIn", href: "https://www.linkedin.com/company/mcleuker/", icon: Linkedin },
  { name: "Instagram", href: "https://www.instagram.com/mcleuker/", icon: Instagram },
  { name: "X (Twitter)", href: "https://x.com/mcleuker", icon: Globe },
  { name: "TikTok", href: "https://www.tiktok.com/@mcleukerparis", icon: Globe },
  { name: "Pinterest", href: "https://fr.pinterest.com/McLeuker/", icon: Globe },
];

const inquiryTypes = [
  "General Inquiry",
  "Partnership",
  "Enterprise Sales",
  "Press & Media",
  "Technical Support",
  "Careers",
];

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    type: "",
    message: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSubmitting(false);
    setSubmitted(true);
    setFormData({ name: "", email: "", company: "", type: "", message: "" });
  };

  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* ═══════════════════════════════════════════════════════ */}
      {/* HERO */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative pt-24 lg:pt-32 pb-16 lg:pb-20 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/3 left-1/4 w-[400px] h-[300px] rounded-full bg-[#A78BFA]/[0.02] blur-[120px]" />
          <div className="absolute top-1/2 right-1/4 w-[300px] h-[200px] rounded-full bg-[#C9A96E]/[0.02] blur-[100px]" />
        </div>

        <div className="relative z-10 container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06] mb-6">
              <div className="w-1.5 h-1.5 rounded-full bg-[#A78BFA]/50 animate-pulse" />
              <span className="text-[11px] text-white/35 uppercase tracking-[0.15em]">Contact</span>
            </div>

            <h1 className="font-editorial text-4xl md:text-5xl lg:text-[3.5rem] text-white/[0.95] tracking-tight leading-[1.08] mb-5">
              Let&apos;s build the future<br />
              <span className="bg-gradient-to-r from-[#A78BFA] to-[#8ECAE6] bg-clip-text text-transparent">of fashion intelligence</span>
            </h1>

            <p className="text-white/40 text-lg max-w-xl mx-auto leading-relaxed">
              Whether you&apos;re exploring the platform, interested in enterprise solutions, or want to partner — we&apos;d love to hear from you.
            </p>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CONTACT METHODS */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="pb-16 lg:pb-20">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-5xl mx-auto">
            {contactMethods.map((method, i) => {
              const MethodIcon = method.icon;
              const Wrapper = method.href ? 'a' : 'div';
              const wrapperProps = method.href ? { href: method.href } : {};
              return (
                <Wrapper
                  key={i}
                  {...wrapperProps as any}
                  className={cn(
                    "p-5 rounded-xl bg-[#0a0a0a] border border-white/[0.04] transition-all",
                    method.href && "hover:border-white/[0.10] cursor-pointer"
                  )}
                >
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center border mb-3" style={{ backgroundColor: `${method.color}06`, borderColor: `${method.color}12` }}>
                    <MethodIcon className="w-4 h-4" style={{ color: `${method.color}70` }} />
                  </div>
                  <h3 className="text-sm font-medium text-white/80 mb-0.5">{method.title}</h3>
                  <p className="text-[11px] text-white/25 mb-2">{method.desc}</p>
                  <p className={cn("text-sm", method.href ? "text-white/70" : "text-white/50")}>{method.value}</p>
                </Wrapper>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* FORM + SIDEBAR */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-16 lg:py-24 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid lg:grid-cols-5 gap-8 lg:gap-12 max-w-5xl mx-auto">
            {/* Form - 3 columns */}
            <div className="lg:col-span-3">
              <div className="p-6 lg:p-8 rounded-2xl bg-[#0d0d0d] border border-white/[0.06]">
                {submitted ? (
                  <div className="text-center py-16">
                    <div className="w-14 h-14 rounded-full bg-[#6b9b8a]/10 flex items-center justify-center mx-auto mb-5">
                      <CheckCircle className="w-7 h-7 text-[#6b9b8a]/70" />
                    </div>
                    <h3 className="text-xl font-editorial text-white/90 mb-2">Message Sent</h3>
                    <p className="text-sm text-white/40 mb-6 max-w-sm mx-auto">
                      Thank you for reaching out. We&apos;ll get back to you within 24 hours.
                    </p>
                    <button
                      onClick={() => setSubmitted(false)}
                      className="text-sm text-white/40 hover:text-white/70 transition-colors underline underline-offset-4"
                    >
                      Send another message
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="mb-6">
                      <h2 className="text-lg font-medium text-white/90 mb-1">Send us a message</h2>
                      <p className="text-sm text-white/30">Fill out the form and we&apos;ll be in touch.</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-xs text-white/40 mb-1.5 uppercase tracking-wider">Name</label>
                          <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="w-full h-11 px-4 rounded-lg bg-white/[0.04] border border-white/[0.06] text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-white/[0.15] transition-colors"
                            placeholder="Your name"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-white/40 mb-1.5 uppercase tracking-wider">Email</label>
                          <input
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            className="w-full h-11 px-4 rounded-lg bg-white/[0.04] border border-white/[0.06] text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-white/[0.15] transition-colors"
                            placeholder="your@email.com"
                            required
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-xs text-white/40 mb-1.5 uppercase tracking-wider">Company <span className="text-white/20">(optional)</span></label>
                          <input
                            type="text"
                            value={formData.company}
                            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                            className="w-full h-11 px-4 rounded-lg bg-white/[0.04] border border-white/[0.06] text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-white/[0.15] transition-colors"
                            placeholder="Your company"
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-white/40 mb-1.5 uppercase tracking-wider">Inquiry Type</label>
                          <select
                            value={formData.type}
                            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                            className="w-full h-11 px-4 rounded-lg bg-white/[0.04] border border-white/[0.06] text-sm text-white/60 focus:outline-none focus:border-white/[0.15] transition-colors appearance-none"
                          >
                            <option value="" className="bg-[#111]">Select type</option>
                            {inquiryTypes.map((type) => (
                              <option key={type} value={type} className="bg-[#111]">{type}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs text-white/40 mb-1.5 uppercase tracking-wider">Message</label>
                        <textarea
                          value={formData.message}
                          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                          className="w-full h-32 px-4 py-3 rounded-lg resize-none bg-white/[0.04] border border-white/[0.06] text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-white/[0.15] transition-colors"
                          placeholder="Tell us about your project or question..."
                          required
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-white text-[#0A0A0A] font-medium text-sm hover:bg-white/90 transition-all disabled:opacity-50"
                      >
                        {isSubmitting ? (
                          <>Sending...</>
                        ) : (
                          <>
                            Send Message
                            <Send className="w-3.5 h-3.5" />
                          </>
                        )}
                      </button>
                    </form>
                  </>
                )}
              </div>
            </div>

            {/* Sidebar - 2 columns */}
            <div className="lg:col-span-2 space-y-4">
              {/* Quick Contact */}
              <div className="p-5 rounded-xl bg-[#0d0d0d] border border-white/[0.06]">
                <h3 className="text-sm font-medium text-white/70 mb-3">Quick Contact</h3>
                <a
                  href="mailto:contact@mcleuker.com"
                  className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.04] hover:border-white/[0.10] transition-all group mb-3"
                >
                  <div className="w-8 h-8 rounded-md flex items-center justify-center bg-[#C9A96E]/[0.08]">
                    <Mail className="w-4 h-4 text-[#C9A96E]/70" />
                  </div>
                  <div>
                    <div className="text-sm text-white/70 group-hover:text-white transition-colors">contact@mcleuker.com</div>
                    <div className="text-[10px] text-white/25">General inquiries</div>
                  </div>
                </a>
                <div className="text-[11px] text-white/20 px-1">
                  Typical response time: within 24 hours
                </div>
              </div>

              {/* Social Links */}
              <div className="p-5 rounded-xl bg-[#0d0d0d] border border-white/[0.06]">
                <h3 className="text-sm font-medium text-white/70 mb-3">Follow Us</h3>
                <div className="space-y-1.5">
                  {socialLinks.map((social, i) => (
                    <a
                      key={i}
                      href={social.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/[0.03] transition-all group"
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-white/20 group-hover:bg-white/40 transition-colors" />
                      <span className="text-sm text-white/45 group-hover:text-white/70 transition-colors">{social.name}</span>
                      <ArrowRight className="w-3 h-3 text-white/15 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  ))}
                </div>
              </div>

              {/* Enterprise CTA */}
              <div className="p-5 rounded-xl border border-[#A78BFA]/[0.10] bg-[#A78BFA]/[0.02]">
                <h3 className="text-sm font-medium text-white/80 mb-2">Enterprise Solutions</h3>
                <p className="text-[12px] text-white/35 leading-relaxed mb-4">
                  Need custom AI models, dedicated support, or API access? Let&apos;s discuss your requirements.
                </p>
                <Link
                  href="/signup"
                  className="inline-flex items-center gap-2 text-sm text-[#A78BFA]/80 hover:text-[#A78BFA] transition-colors"
                >
                  Schedule a demo <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* MAP / LOCATION VISUAL */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-16 lg:py-20 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-5xl mx-auto">
            <div className="p-8 lg:p-10 rounded-2xl bg-[#0a0a0a] border border-white/[0.04] relative overflow-hidden">
              {/* Decorative grid */}
              <div className="absolute inset-0 opacity-[0.015] pointer-events-none" style={{
                backgroundImage: `radial-gradient(circle, white 1px, transparent 1px)`,
                backgroundSize: '30px 30px'
              }} />

              <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <MapPin className="w-4 h-4 text-[#A78BFA]/50" />
                    <span className="text-[11px] text-white/25 uppercase tracking-[0.15em]">Headquarters</span>
                  </div>
                  <h3 className="font-editorial text-3xl text-white/90 mb-2">Paris, France</h3>
                  <p className="text-sm text-white/35 max-w-md">
                    Based in the heart of the fashion capital. Building AI-powered intelligence for the global fashion industry.
                  </p>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-editorial text-[#C9A96E]/70 mb-0.5">CET</div>
                    <div className="text-[10px] text-white/20 uppercase tracking-wider">Timezone</div>
                  </div>
                  <div className="w-px h-10 bg-white/[0.06]" />
                  <div className="text-center">
                    <div className="text-2xl font-editorial text-[#8ECAE6]/70 mb-0.5">9–6</div>
                    <div className="text-[10px] text-white/20 uppercase tracking-wider">Hours</div>
                  </div>
                  <div className="w-px h-10 bg-white/[0.06]" />
                  <div className="text-center">
                    <div className="text-2xl font-editorial text-[#6b9b8a]/70 mb-0.5">Mon–Fri</div>
                    <div className="text-[10px] text-white/20 uppercase tracking-wider">Days</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
