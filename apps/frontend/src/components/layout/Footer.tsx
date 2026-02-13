'use client';

import Link from "next/link";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Linkedin, Instagram, Twitter, ArrowRight, Mail, MapPin } from "lucide-react";

/* Custom TikTok icon */
function TikTokIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
      <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 0010.86 4.48v-7.1a8.16 8.16 0 004.77 1.52v-3.4a4.85 4.85 0 01-.81-.07 4.86 4.86 0 01-.38-3.94z" />
    </svg>
  );
}

/* Custom Pinterest icon */
function PinterestIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.477 2 2 6.477 2 12c0 4.236 2.636 7.855 6.356 9.312-.088-.791-.167-2.005.035-2.868.181-.78 1.172-4.97 1.172-4.97s-.299-.598-.299-1.482c0-1.388.806-2.425 1.808-2.425.853 0 1.265.64 1.265 1.408 0 .858-.546 2.14-.828 3.33-.236.995.499 1.806 1.481 1.806 1.778 0 3.144-1.874 3.144-4.58 0-2.393-1.72-4.068-4.177-4.068-2.845 0-4.515 2.135-4.515 4.34 0 .859.331 1.781.745 2.282a.3.3 0 01.069.288l-.278 1.133c-.044.183-.145.222-.335.134-1.249-.581-2.03-2.407-2.03-3.874 0-3.154 2.292-6.052 6.608-6.052 3.469 0 6.165 2.473 6.165 5.776 0 3.447-2.173 6.22-5.19 6.22-1.013 0-1.965-.527-2.291-1.148l-.623 2.378c-.226.869-.835 1.958-1.244 2.621.937.29 1.931.446 2.962.446 5.523 0 10-4.477 10-10S17.523 2 12 2z" />
    </svg>
  );
}

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
              
              {/* Social Icons — Now with 5 platforms */}
              <div className="flex items-center gap-2.5 mb-6">
                {[
                  { icon: Linkedin, href: "https://linkedin.com/company/mcleuker", label: "LinkedIn" },
                  { icon: Instagram, href: "https://www.instagram.com/mcleuker/", label: "Instagram" },
                  { icon: Twitter, href: "https://x.com/mcleuker", label: "X" },
                  { icon: TikTokIcon, href: "https://www.tiktok.com/@mcleukerparis", label: "TikTok" },
                  { icon: PinterestIcon, href: "https://fr.pinterest.com/McLeuker/", label: "Pinterest" },
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
            </div>

          </div>
        </div>
      </div>
    </footer>
  );
}
