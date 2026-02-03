'use client';

import Link from "next/link";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Linkedin, ArrowRight } from "lucide-react";

const footerLinks = {
  product: [
    { name: "Dashboard", href: "/dashboard" },
    { name: "Domains", href: "/domains" },
    { name: "How it Works", href: "/help" },
  ],
  solutions: [
    { name: "Trend Forecasting", href: "/solutions/trend-forecasting" },
    { name: "Supplier Research", href: "/solutions/supplier-research" },
    { name: "Market Analysis", href: "/solutions/market-analysis" },
    { name: "Sustainability Insights", href: "/solutions/sustainability-insights" },
  ],
  resources: [
    { name: "Help / FAQ", href: "/help" },
    { name: "Contact", href: "/contact" },
  ],
  company: [
    { name: "About", href: "/about" },
    { name: "Pricing", href: "/pricing" },
  ],
  legal: [
    { name: "Privacy Policy", href: "/privacy" },
    { name: "Terms of Service", href: "/terms" },
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
    <footer className="border-t border-white/[0.08] bg-gradient-to-b from-[#0A0A0A] to-[#070707]">
      <div className="container mx-auto px-6 lg:px-8 py-16 lg:py-20">
        {/* Main Footer Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 lg:gap-12 mb-16">
          {/* Brand Column */}
          <div className="col-span-2 md:col-span-3 lg:col-span-1">
            <Link href="/" className="inline-block mb-6">
              <span className="font-editorial text-xl text-white tracking-[0.02em]">
                McLeuker
              </span>
            </Link>
            <p className="text-sm text-white/50 leading-relaxed mb-6 max-w-[240px]">
              AI-powered fashion intelligence for professionals who demand excellence.
            </p>
            <div className="flex items-center gap-3">
              <a
                href="https://linkedin.com/company/mcleuker"
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  "w-9 h-9 rounded-full flex items-center justify-center",
                  "bg-white/[0.06] hover:bg-white/[0.12] transition-colors",
                  "text-white/60 hover:text-white"
                )}
              >
                <Linkedin className="h-4 w-4" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-xs font-medium text-white/40 uppercase tracking-[0.15em] mb-4">
              Product
            </h4>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-white/60 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Solutions */}
          <div>
            <h4 className="text-xs font-medium text-white/40 uppercase tracking-[0.15em] mb-4">
              Solutions
            </h4>
            <ul className="space-y-3">
              {footerLinks.solutions.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-white/60 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-medium text-white/40 uppercase tracking-[0.15em] mb-4">
              Resources
            </h4>
            <ul className="space-y-3">
              {footerLinks.resources.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-white/60 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-xs font-medium text-white/40 uppercase tracking-[0.15em] mb-4">
              Company
            </h4>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-white/60 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-xs font-medium text-white/40 uppercase tracking-[0.15em] mb-4">
              Legal
            </h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-white/60 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Newsletter Section */}
        <div className={cn(
          "p-8 rounded-[20px] mb-12",
          "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
          "border border-white/[0.08]"
        )}>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <h3 className="text-lg font-medium text-white/[0.92] mb-2">
                Get McLeuker insights in your inbox
              </h3>
              <p className="text-sm text-white/50">
                Industry trends, product updates, and fashion intelligence. No spam.
              </p>
            </div>
            <form onSubmit={handleNewsletterSubmit} className="flex gap-3 w-full md:w-auto">
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={cn(
                  "h-11 w-full md:w-[280px] px-4",
                  "bg-white/[0.06] border border-white/[0.10] rounded-full",
                  "text-white placeholder:text-white/40",
                  "focus:border-white/[0.18] focus:ring-white/[0.06] focus:outline-none"
                )}
                required
              />
              <button
                type="submit"
                disabled={isSubmitting}
                className="h-11 px-6 bg-white text-black hover:bg-white/90 rounded-full shrink-0 flex items-center gap-1.5 transition-colors"
              >
                {isSubmitting ? "..." : subscribed ? "Subscribed!" : "Subscribe"}
                {!isSubmitting && !subscribed && <ArrowRight className="h-4 w-4" />}
              </button>
            </form>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8 border-t border-white/[0.06]">
          <p className="text-sm text-white/40">
            © {currentYear} McLeuker AI. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            <Link href="/privacy" className="text-sm text-white/40 hover:text-white/70 transition-colors">
              Privacy
            </Link>
            <Link href="/terms" className="text-sm text-white/40 hover:text-white/70 transition-colors">
              Terms
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
