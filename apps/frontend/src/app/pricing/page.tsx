'use client';

import Link from "next/link";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import {
  ArrowRight, Check, X as XIcon, Zap, Building2, Sparkles,
  FileText, BarChart3, Users, Shield, Headphones, Globe, Coins
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

const plans = [
  {
    id: "free",
    slug: "free",
    name: "Free",
    desc: "Explore the platform",
    monthlyPrice: 0,
    yearlyPrice: 0,
    priceLabel: "Free",
    credits: 50,
    icon: Zap,
    features: [
      "50 credits / month",
      "5 daily free credits",
      "Basic research queries",
      "All 10 domains",
      "Standard response time",
      "Email support",
    ],
    cta: "Get Started",
    href: "/signup",
    highlighted: false,
  },
  {
    id: "starter",
    slug: "starter",
    name: "Starter",
    desc: "For individual researchers",
    monthlyPrice: 29,
    yearlyPrice: 290,
    credits: 500,
    icon: Sparkles,
    features: [
      "500 credits / month",
      "10 daily free credits",
      "Advanced trend forecasting",
      "All 10 domains",
      "Export to PDF, Excel, PPTX",
      "Priority support",
    ],
    cta: "Subscribe",
    highlighted: false,
  },
  {
    id: "professional",
    slug: "pro",
    name: "Professional",
    desc: "For fashion professionals",
    monthlyPrice: 79,
    yearlyPrice: 790,
    credits: 2000,
    icon: Building2,
    features: [
      "2,000 credits / month",
      "20 daily free credits",
      "Deep research & analysis",
      "Supplier intelligence",
      "Market analysis reports",
      "All export formats",
      "Priority support",
    ],
    cta: "Subscribe",
    highlighted: true,
    badge: "Most Popular",
  },
  {
    id: "enterprise",
    slug: "enterprise",
    name: "Enterprise",
    desc: "For teams & organizations",
    monthlyPrice: 199,
    yearlyPrice: 1990,
    credits: 10000,
    icon: Building2,
    features: [
      "10,000 credits / month",
      "50 daily free credits",
      "Unlimited research depth",
      "Custom AI model training",
      "Dedicated account manager",
      "API access & integrations",
      "SLA guarantee",
    ],
    cta: "Subscribe",
    highlighted: false,
  },
];

const comparisonFeatures = [
  { category: "Credits & Research", features: [
    { name: "Monthly credits", free: "50", starter: "500", pro: "2,000", enterprise: "10,000" },
    { name: "Daily free credits", free: "5", starter: "10", pro: "20", enterprise: "50" },
    { name: "Domain access", free: "All 10", starter: "All 10", pro: "All 10", enterprise: "All 10 + Custom" },
    { name: "Response time", free: "Standard", starter: "Priority", pro: "Priority", enterprise: "Instant" },
    { name: "Source depth", free: "Basic", starter: "Advanced", pro: "Deep", enterprise: "Deep + Custom" },
  ]},
  { category: "Exports", features: [
    { name: "PDF reports", free: true, starter: true, pro: true, enterprise: true },
    { name: "Excel exports", free: true, starter: true, pro: true, enterprise: true },
    { name: "PowerPoint decks", free: true, starter: true, pro: true, enterprise: true },
    { name: "Word documents", free: true, starter: true, pro: true, enterprise: true },
    { name: "Custom templates", free: false, starter: false, pro: false, enterprise: true },
  ]},
  { category: "Support", features: [
    { name: "Email support", free: true, starter: true, pro: true, enterprise: true },
    { name: "Priority support", free: false, starter: true, pro: true, enterprise: true },
    { name: "Dedicated manager", free: false, starter: false, pro: false, enterprise: true },
    { name: "SLA guarantee", free: false, starter: false, pro: false, enterprise: true },
  ]},
];

const faqs = [
  { q: "What are credits?", a: "Credits are the currency used for AI research on McLeuker. Each search, file generation, or analysis consumes credits based on the complexity of the task." },
  { q: "How do daily free credits work?", a: "Every day you can claim free credits — 5 for Free, 10 for Starter, 20 for Pro, 50 for Enterprise. Consecutive daily claims build a streak that earns bonus credits." },
  { q: "Can I buy extra credits?", a: "Yes, you can purchase credit packs anytime from your billing page. Larger packs include bonus credits and never expire." },
  { q: "Can I change plans later?", a: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately with prorated billing." },
  { q: "What payment methods do you accept?", a: "We accept all major credit cards via Stripe. Enterprise plans also support wire transfers." },
  { q: "What happens when I run out of credits?", a: "You can claim daily free credits, purchase credit packs, or upgrade your plan. Your research history and files are always preserved." },
  { q: "Do you offer refunds?", a: "We offer a 30-day money-back guarantee on all paid plans. No questions asked." },
];

export default function PricingPage() {
  const [annual, setAnnual] = useState(true);
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
  const [subscribing, setSubscribing] = useState<string | null>(null);
  const { user, session } = useAuth();

  const handleSubscribe = async (planSlug: string) => {
    if (planSlug === 'free') {
      window.location.href = '/signup';
      return;
    }
    if (!session?.access_token) {
      window.location.href = '/login';
      return;
    }
    setSubscribing(planSlug);
    try {
      const res = await fetch(`${API_URL}/api/v1/subscriptions/checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan_slug: planSlug,
          billing_period: annual ? 'yearly' : 'monthly',
          success_url: `${window.location.origin}/billing?success=true`,
          cancel_url: `${window.location.origin}/pricing`,
        }),
      });
      const data = await res.json();
      if (data.success && data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (error) {
      console.error('Checkout error:', error);
    } finally {
      setSubscribing(null);
    }
  };

  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* ═══════════════════════════════════════════════════════ */}
      {/* HERO — Monochromatic */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative pt-24 lg:pt-32 pb-16 lg:pb-20 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-full bg-white/[0.015] blur-[120px]" />
        </div>

        <div className="relative z-10 container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06] mb-6">
              <div className="w-1.5 h-1.5 rounded-full bg-white/30 animate-pulse" />
              <span className="text-[11px] text-white/35 uppercase tracking-[0.15em]">Pricing</span>
            </div>

            <h1 className="font-editorial text-4xl md:text-5xl lg:text-[3.5rem] text-white/[0.95] tracking-tight leading-[1.08] mb-5">
              Intelligence that<br />
              <span className="text-white/50">pays for itself</span>
            </h1>

            <p className="text-white/40 text-lg max-w-xl mx-auto leading-relaxed mb-10">
              Start free. Upgrade when your research demands it. Every plan includes structured, exportable deliverables.
            </p>

            {/* Billing Toggle */}
            <div className="inline-flex items-center gap-3 p-1 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <button
                onClick={() => setAnnual(false)}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm transition-all",
                  !annual ? "bg-white/[0.08] text-white" : "text-white/40 hover:text-white/60"
                )}
              >
                Monthly
              </button>
              <button
                onClick={() => setAnnual(true)}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2",
                  annual ? "bg-white/[0.08] text-white" : "text-white/40 hover:text-white/60"
                )}
              >
                Annual
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.08] text-white/60 font-medium">-20%</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* PRICING CARDS — Monochromatic */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="pb-20 lg:pb-28">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
            {plans.map((plan) => {
              const PlanIcon = plan.icon;
              const price = plan.priceLabel || (annual ? `$${plan.yearlyPrice}` : `$${plan.monthlyPrice}`);
              return (
                <div
                  key={plan.id}
                  className={cn(
                    "relative p-6 lg:p-7 rounded-2xl border transition-all",
                    plan.highlighted
                      ? "bg-[#0d0d0d] border-white/[0.12] scale-[1.02] shadow-2xl shadow-black/30"
                      : "bg-[#0a0a0a] border-white/[0.05] hover:border-white/[0.10]"
                  )}
                >
                  {/* Badge */}
                  {plan.badge && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <div className="px-3 py-1 rounded-full text-[10px] font-medium uppercase tracking-wider bg-white/[0.08] text-white/70 border border-white/[0.10]">
                        {plan.badge}
                      </div>
                    </div>
                  )}

                  {/* Header */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-9 h-9 rounded-lg flex items-center justify-center border border-white/[0.06] bg-white/[0.02]">
                      <PlanIcon className="w-4 h-4 text-white/50" />
                    </div>
                    <div>
                      <h3 className="text-base font-medium text-white/90">{plan.name}</h3>
                      <p className="text-[11px] text-white/30">{plan.desc}</p>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="mb-5 pb-5 border-b border-white/[0.05]">
                    <div className="flex items-baseline gap-1.5">
                      <span className="text-3xl lg:text-4xl font-editorial text-white/95">{price}</span>
                      {plan.monthlyPrice !== null && plan.monthlyPrice > 0 && (
                        <span className="text-sm text-white/30">/ {annual ? 'year' : 'month'}</span>
                      )}
                    </div>
                    {plan.credits && (
                      <div className="flex items-center gap-1.5 mt-2">
                        <Coins className="w-3 h-3 text-white/30" />
                        <span className="text-xs text-white/40">{plan.credits.toLocaleString()} credits / month</span>
                      </div>
                    )}
                  </div>

                  {/* Features */}
                  <ul className="space-y-2.5 mb-7">
                    {plan.features.map((feature, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm">
                        <div className="w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 bg-white/[0.04]">
                          <Check className="w-2.5 h-2.5 text-white/50" />
                        </div>
                        <span className="text-white/55">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA */}
                  <button
                    onClick={() => handleSubscribe(plan.slug)}
                    disabled={subscribing === plan.slug}
                    className={cn(
                      "w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-medium transition-all",
                      plan.highlighted
                        ? "bg-white text-[#0A0A0A] hover:bg-white/90"
                        : "border border-white/[0.10] text-white/70 hover:bg-white/[0.05] hover:text-white",
                      subscribing === plan.slug && "opacity-50 cursor-wait"
                    )}
                  >
                    {subscribing === plan.slug ? 'Processing...' : plan.cta}
                    {subscribing !== plan.slug && <ArrowRight className="w-3.5 h-3.5" />}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* COMPARISON TABLE — Monochromatic */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.95] tracking-tight mb-3">
                Compare Plans
              </h2>
              <p className="text-white/35 text-base">Detailed feature comparison across all plans.</p>
            </div>

            <div className="rounded-2xl border border-white/[0.06] overflow-hidden">
              {/* Table Header */}
              <div className="grid grid-cols-5 bg-[#0d0d0d] border-b border-white/[0.06]">
                <div className="p-4 lg:p-5">
                  <span className="text-xs text-white/25 uppercase tracking-wider">Feature</span>
                </div>
                <div className="p-4 lg:p-5 text-center">
                  <span className="text-sm text-white/50">Free</span>
                </div>
                <div className="p-4 lg:p-5 text-center">
                  <span className="text-sm text-white/50">Starter</span>
                </div>
                <div className="p-4 lg:p-5 text-center border-x border-white/[0.04]">
                  <span className="text-sm font-medium text-white/80">Professional</span>
                </div>
                <div className="p-4 lg:p-5 text-center">
                  <span className="text-sm text-white/50">Enterprise</span>
                </div>
              </div>

              {/* Table Body */}
              {comparisonFeatures.map((group, gi) => (
                <div key={gi}>
                  <div className="px-4 lg:px-5 py-3 bg-white/[0.02] border-b border-white/[0.04]">
                    <span className="text-[11px] text-white/30 uppercase tracking-[0.15em] font-medium">{group.category}</span>
                  </div>
                  {group.features.map((feature, fi) => (
                    <div key={fi} className="grid grid-cols-5 border-b border-white/[0.03] hover:bg-white/[0.01] transition-colors">
                      <div className="p-4 lg:p-5 flex items-center">
                        <span className="text-sm text-white/50">{feature.name}</span>
                      </div>
                      {['free', 'starter', 'pro', 'enterprise'].map((tier, ti) => {
                        const val = (feature as any)[tier];
                        return (
                          <div key={ti} className={cn("p-4 lg:p-5 flex items-center justify-center", ti === 2 && "border-x border-white/[0.04] bg-white/[0.01]")}>
                            {typeof val === 'boolean' ? (
                              val ? (
                                <div className="w-5 h-5 rounded-full bg-white/[0.06] flex items-center justify-center">
                                  <Check className="w-3 h-3 text-white/50" />
                                </div>
                              ) : (
                                <div className="w-5 h-5 rounded-full bg-white/[0.03] flex items-center justify-center">
                                  <XIcon className="w-3 h-3 text-white/15" />
                                </div>
                              )
                            ) : (
                              <span className="text-sm text-white/60 text-center">{val}</span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* WHAT'S INCLUDED — Monochromatic */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.95] tracking-tight mb-3">
                Every Plan Includes
              </h2>
              <p className="text-white/35 text-base">Core capabilities available across all tiers.</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {[
                { icon: FileText, title: "Structured Reports", desc: "Professional, exportable deliverables" },
                { icon: BarChart3, title: "Data Visualization", desc: "Charts, matrices, and comparisons" },
                { icon: Shield, title: "Source Citations", desc: "Every insight is traceable" },
                { icon: Users, title: "Fashion Expertise", desc: "Industry-specific AI models" },
                { icon: Globe, title: "Global Coverage", desc: "Multi-market intelligence" },
                { icon: Headphones, title: "Support", desc: "Email support on all plans" },
              ].map((item, i) => {
                const ItemIcon = item.icon;
                return (
                  <div key={i} className="p-5 rounded-xl bg-[#0a0a0a] border border-white/[0.04] hover:border-white/[0.08] transition-all">
                    <div className="w-9 h-9 rounded-lg flex items-center justify-center border border-white/[0.06] bg-white/[0.02] mb-3">
                      <ItemIcon className="w-4 h-4 text-white/40" />
                    </div>
                    <h3 className="text-sm font-medium text-white/80 mb-1">{item.title}</h3>
                    <p className="text-[12px] text-white/30">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* FAQ */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.95] tracking-tight mb-3">
                Frequently Asked Questions
              </h2>
            </div>

            <div className="space-y-2">
              {faqs.map((faq, i) => (
                <div key={i} className="rounded-xl border border-white/[0.05] overflow-hidden">
                  <button
                    onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                    className="w-full flex items-center justify-between p-5 text-left hover:bg-white/[0.02] transition-colors"
                  >
                    <span className="text-sm text-white/75 font-medium pr-4">{faq.q}</span>
                    <div className={cn("w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 bg-white/[0.04] transition-transform", expandedFaq === i && "rotate-45")}>
                      <span className="text-white/40 text-sm">+</span>
                    </div>
                  </button>
                  {expandedFaq === i && (
                    <div className="px-5 pb-5 -mt-1">
                      <p className="text-sm text-white/40 leading-relaxed">{faq.a}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CTA */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#070707] relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-full bg-white/[0.01] blur-[120px]" />
        </div>
        <div className="relative z-10 container mx-auto px-6 lg:px-12 text-center">
          <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.95] tracking-tight mb-4">
            Ready to start researching?
          </h2>
          <p className="text-white/40 text-lg mb-8 max-w-xl mx-auto">
            Join fashion professionals using McLeuker AI for smarter, faster intelligence.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-7 py-3 rounded-xl bg-white text-[#0A0A0A] font-medium text-sm hover:bg-white/90 transition-all"
            >
              Start Free Trial
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/contact"
              className="inline-flex items-center gap-2 px-7 py-3 rounded-xl border border-white/[0.08] text-white/60 text-sm hover:bg-white/[0.04] transition-all"
            >
              Talk to Sales
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
