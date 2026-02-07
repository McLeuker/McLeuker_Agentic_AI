'use client';

import Link from "next/link";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import {
  ArrowRight, Check, X as XIcon, Zap, Building2, Sparkles,
  FileText, BarChart3, Users, Shield, Headphones, Globe
} from "lucide-react";

const plans = [
  {
    id: "starter",
    name: "Starter",
    desc: "Explore the platform",
    monthlyPrice: 0,
    yearlyPrice: 0,
    priceLabel: "Free",
    icon: Zap,
    features: [
      "5 research queries / month",
      "Basic trend reports",
      "1 domain access",
      "Standard response time",
      "Email support",
    ],
    cta: "Get Started",
    href: "/signup",
    highlighted: false,
  },
  {
    id: "professional",
    name: "Professional",
    desc: "For fashion professionals",
    monthlyPrice: 99,
    yearlyPrice: 79,
    icon: Sparkles,
    features: [
      "100 research queries / month",
      "Advanced trend forecasting",
      "All 10 domains",
      "Supplier intelligence",
      "Market analysis reports",
      "Export to PDF, Excel, PPTX",
      "Priority support",
    ],
    cta: "Start Free Trial",
    href: "/signup",
    highlighted: true,
    badge: "Most Popular",
  },
  {
    id: "enterprise",
    name: "Enterprise",
    desc: "For teams & organizations",
    monthlyPrice: null,
    yearlyPrice: null,
    priceLabel: "Custom",
    icon: Building2,
    features: [
      "Unlimited research queries",
      "Custom AI model training",
      "Dedicated account manager",
      "API access & integrations",
      "SSO & advanced security",
      "Custom report templates",
      "SLA guarantee",
    ],
    cta: "Contact Sales",
    href: "/contact",
    highlighted: false,
  },
];

const comparisonFeatures = [
  { category: "Research", features: [
    { name: "Monthly queries", starter: "5", pro: "100", enterprise: "Unlimited" },
    { name: "Domain access", starter: "1", pro: "All 10", enterprise: "All 10 + Custom" },
    { name: "Response time", starter: "Standard", pro: "Priority", enterprise: "Instant" },
    { name: "Source depth", starter: "Basic", pro: "Advanced", enterprise: "Deep + Custom" },
  ]},
  { category: "Exports", features: [
    { name: "PDF reports", starter: true, pro: true, enterprise: true },
    { name: "Excel exports", starter: false, pro: true, enterprise: true },
    { name: "PowerPoint decks", starter: false, pro: true, enterprise: true },
    { name: "Word documents", starter: false, pro: true, enterprise: true },
    { name: "Custom templates", starter: false, pro: false, enterprise: true },
  ]},
  { category: "Support", features: [
    { name: "Email support", starter: true, pro: true, enterprise: true },
    { name: "Priority support", starter: false, pro: true, enterprise: true },
    { name: "Dedicated manager", starter: false, pro: false, enterprise: true },
    { name: "SLA guarantee", starter: false, pro: false, enterprise: true },
  ]},
];

const faqs = [
  { q: "How does the free trial work?", a: "Start with our Professional plan free for 14 days. No credit card required. Cancel anytime." },
  { q: "Can I change plans later?", a: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately with prorated billing." },
  { q: "What payment methods do you accept?", a: "We accept all major credit cards, PayPal, and wire transfers for Enterprise plans." },
  { q: "Is there a discount for annual billing?", a: "Yes, annual plans receive a 20% discount compared to monthly billing — saving you over $230/year on Professional." },
  { q: "What happens when I reach my query limit?", a: "You'll receive a notification at 80% usage. You can upgrade mid-cycle or purchase additional queries as needed." },
  { q: "Do you offer refunds?", a: "We offer a 30-day money-back guarantee on all paid plans. No questions asked." },
];

export default function PricingPage() {
  const [annual, setAnnual] = useState(true);
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto">
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
                  <div className="flex items-baseline gap-1.5 mb-5 pb-5 border-b border-white/[0.05]">
                    <span className="text-3xl lg:text-4xl font-editorial text-white/95">{price}</span>
                    {plan.monthlyPrice !== null && plan.monthlyPrice > 0 && (
                      <span className="text-sm text-white/30">/ month</span>
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
                  <Link
                    href={plan.href}
                    className={cn(
                      "w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-medium transition-all",
                      plan.highlighted
                        ? "bg-white text-[#0A0A0A] hover:bg-white/90"
                        : "border border-white/[0.10] text-white/70 hover:bg-white/[0.05] hover:text-white"
                    )}
                  >
                    {plan.cta}
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
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
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.95] tracking-tight mb-3">
                Compare Plans
              </h2>
              <p className="text-white/35 text-base">Detailed feature comparison across all plans.</p>
            </div>

            <div className="rounded-2xl border border-white/[0.06] overflow-hidden">
              {/* Table Header */}
              <div className="grid grid-cols-4 bg-[#0d0d0d] border-b border-white/[0.06]">
                <div className="p-4 lg:p-5">
                  <span className="text-xs text-white/25 uppercase tracking-wider">Feature</span>
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
                    <div key={fi} className="grid grid-cols-4 border-b border-white/[0.03] hover:bg-white/[0.01] transition-colors">
                      <div className="p-4 lg:p-5 flex items-center">
                        <span className="text-sm text-white/50">{feature.name}</span>
                      </div>
                      {['starter', 'pro', 'enterprise'].map((tier, ti) => {
                        const val = tier === 'starter' ? feature.starter : tier === 'pro' ? feature.pro : feature.enterprise;
                        return (
                          <div key={ti} className={cn("p-4 lg:p-5 flex items-center justify-center", ti === 1 && "border-x border-white/[0.04] bg-white/[0.01]")}>
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
