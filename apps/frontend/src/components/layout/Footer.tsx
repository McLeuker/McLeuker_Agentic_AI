'use client';

import Link from "next/link";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Linkedin, Instagram, Twitter, ArrowRight, Globe, Mail, MapPin } from "lucide-react";

const footerLinks = {
  product: [
    { name: "Dashboard", href: "/dashboard" },
    { name: "Domains", href: "/domains" },
    { name: "How it Works", href: "/how-it-works" },
    { name: "Pricing", href: "/pricing" },
    { name: "Blog", href: "/blog" },
  ],
  solutions: [
    { name: "Trend Forecasting", href: "/solutions/trend-forecasting" },
    { name: "Supplier Research", href: "/solutions/supplier-research" },
    { name: "Market Analysis", href: "/solutions/market-analysis" },
    { name: "Sustainability Insights", href: "/solutions/sustainability-insights" },
  ],
  domains: [
    { name: "Fashion", href: "/domain/fashion" },
    { name: "Beauty", href: "/domain/beauty" },
    { name: "Skincare", href: "/domain/skincare" },
    { name: "Sustainability", href: "/domain/sustainability" },
    { name: "Fashion Tech", href: "/domain/fashion-tech" },
    { name: "Catwalks", href: "/domain/catwalks" },
    { name: "Textile", href: "/domain/textile" },
    { name: "Culture", href: "/domain/culture" },
    { name: "Lifestyle", href: "/domain/lifestyle" },
  ],
  company: [
    { name: "About", href: "/about" },
    { name: "Careers", href: "/careers" },
    { name: "Press", href: "/press" },
    { name: "Contact", href: "/contact" },
    { name: "Help / FAQ", href: "/help" },
  ],
  legal: [
    { name: "Privacy Policy", href: "/privacy" },
    { name: "Terms of Service", href: "/terms" },
    { name: "Cookie Policy", href: "/cookies" },
    { name: "Mentions Légales", href: "/legal/mentions-legales" },
    { name: "Acceptable Use", href: "/legal/aup" },
    { name: "AI Transparency", href: "/legal/ai-transparency" },
    { name: "Security & Trust", href: "/legal/security" },
    { name: "Subprocessors", href: "/legal/subprocessors" },
    { name: "Data Requests", href: "/legal/dsar" },
  ],
};

export function Footer() {
  const currentYear = new Date().getFullYear();
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [subscribed, setSubscribed] = useState(false);

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    
    setIsSubmitting(true);
    await new Promise(resolve => setTimeout(resolve, 800));
    setIsSubmitting(false);
    setEmail("");
    setSubscribed(true);
    setTimeout(() => setSubscribed(false), 3000);
  };

  return (
    <footer className="border-t border-white/[0.06] bg-gradient-to-b from-[#0A0A0A] to-[#050505]">
      {/* Newsletter Banner */}
      <div className="border-b border-white/[0.06]">
        <div className="container mx-auto px-6 lg:px-8 py-12 lg:py-16">
          <div className="max-w-[1200px] mx-auto">
            <div className="grid lg:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="font-editorial text-2xl lg:text-3xl text-white/[0.92] mb-3 leading-tight">
                  Stay ahead of the industry
                </h3>
                <p className="text-sm text-white/45 leading-relaxed max-w-md">
                  Weekly fashion intelligence, product updates, and trend reports delivered to your inbox. Trusted by professionals across 10 domains.
                </p>
              </div>
              <form onSubmit={handleNewsletterSubmit} className="flex gap-3">
                <div className="relative flex-1">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/25" />
                  <input
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={cn(
                      "h-12 w-full pl-11 pr-4",
                      "bg-white/[0.04] border border-white/[0.08] rounded-xl",
                      "text-white text-sm placeholder:text-white/30",
                      "focus:border-white/[0.18] focus:ring-1 focus:ring-white/[0.06] focus:outline-none",
                      "transition-all"
                    )}
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={cn(
                    "h-12 px-6 rounded-xl shrink-0 flex items-center gap-2 text-sm font-medium transition-all",
                    "bg-white text-black hover:bg-white/90",
                    "disabled:opacity-50 disabled:cursor-not-allowed"
                  )}
                >
                  {isSubmitting ? "..." : subscribed ? "Subscribed!" : "Subscribe"}
                  {!isSubmitting && !subscribed && <ArrowRight className="h-4 w-4" />}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="container mx-auto px-6 lg:px-8 py-14 lg:py-18">
        <div className="max-w-[1200px] mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-12 gap-8 lg:gap-6">
            {/* Brand Column — spans 3 cols */}
            <div className="col-span-2 md:col-span-3 lg:col-span-3">
              <Link href="/" className="inline-block mb-5">
                <span className="font-editorial text-xl text-white tracking-[0.02em]">
                  McLeuker<span className="text-white/30">.ai</span>
                </span>
              </Link>
              <p className="text-[13px] text-white/40 leading-relaxed mb-6 max-w-[260px]">
                AI-powered fashion intelligence platform. From trend analysis to supplier sourcing — structured, professional, and ready to act on.
              </p>
              
              {/* Social Icons */}
              <div className="flex items-center gap-2.5 mb-6">
                {[
                  { icon: Linkedin, href: "https://linkedin.com/company/mcleuker", label: "LinkedIn" },
                  { icon: Instagram, href: "https://www.instagram.com/mcleuker/", label: "Instagram" },
                  { icon: Twitter, href: "https://x.com/mcleuker", label: "X" },
                ].map((social) => {
                  const SocialIcon = social.icon;
                  return (
                    <a
                      key={social.label}
                      href={social.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={social.label}
                      className={cn(
                        "w-8 h-8 rounded-lg flex items-center justify-center",
                        "bg-white/[0.04] border border-white/[0.06]",
                        "hover:bg-white/[0.08] hover:border-white/[0.12] transition-all",
                        "text-white/40 hover:text-white/70"
                      )}
                    >
                      <SocialIcon className="h-3.5 w-3.5" />
                    </a>
                  );
                })}
              </div>

              {/* Location */}
              <div className="flex items-start gap-2 text-[12px] text-white/25">
                <MapPin className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                <span>Paris, France</span>
              </div>
            </div>

            {/* Product */}
            <div className="lg:col-span-2">
              <h4 className="text-[11px] font-medium text-white/30 uppercase tracking-[0.15em] mb-4">
                Product
              </h4>
              <ul className="space-y-2.5">
                {footerLinks.product.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-[13px] text-white/50 hover:text-white/80 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Solutions */}
            <div className="lg:col-span-2">
              <h4 className="text-[11px] font-medium text-white/30 uppercase tracking-[0.15em] mb-4">
                Solutions
              </h4>
              <ul className="space-y-2.5">
                {footerLinks.solutions.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-[13px] text-white/50 hover:text-white/80 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Domains */}
            <div className="lg:col-span-2">
              <h4 className="text-[11px] font-medium text-white/30 uppercase tracking-[0.15em] mb-4">
                Domains
              </h4>
              <ul className="space-y-2.5">
                {footerLinks.domains.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-[13px] text-white/50 hover:text-white/80 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Company */}
            <div className="lg:col-span-1">
              <h4 className="text-[11px] font-medium text-white/30 uppercase tracking-[0.15em] mb-4">
                Company
              </h4>
              <ul className="space-y-2.5">
                {footerLinks.company.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-[13px] text-white/50 hover:text-white/80 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal */}
            <div className="lg:col-span-2">
              <h4 className="text-[11px] font-medium text-white/30 uppercase tracking-[0.15em] mb-4">
                Legal
              </h4>
              <ul className="space-y-2.5">
                {footerLinks.legal.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-[13px] text-white/50 hover:text-white/80 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/[0.04]">
        <div className="container mx-auto px-6 lg:px-8 py-6">
          <div className="max-w-[1200px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500/60 animate-pulse" />
              <p className="text-[12px] text-white/30">
                All systems operational
              </p>
              <span className="text-white/10">·</span>
              <p className="text-[12px] text-white/30">
                © {currentYear} McLeuker AI. All rights reserved.
              </p>
            </div>
            <div className="flex items-center gap-5 flex-wrap justify-center">
              <Link href="/privacy" className="text-[12px] text-white/30 hover:text-white/60 transition-colors">
                Privacy
              </Link>
              <Link href="/terms" className="text-[12px] text-white/30 hover:text-white/60 transition-colors">
                Terms
              </Link>
              <Link href="/cookies" className="text-[12px] text-white/30 hover:text-white/60 transition-colors">
                Cookies
              </Link>
              <Link href="/legal/mentions-legales" className="text-[12px] text-white/30 hover:text-white/60 transition-colors">
                Mentions Légales
              </Link>
              <div className="flex items-center gap-1.5 text-[12px] text-white/20">
                <Globe className="w-3 h-3" />
                <span>EN</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
