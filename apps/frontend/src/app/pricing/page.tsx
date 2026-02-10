'use client';

import Link from "next/link";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/integrations/supabase/client";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import {
  ArrowRight, Check, X as XIcon, Zap, Building2, Sparkles, Crown,
  FileText, BarChart3, Users, Shield, Headphones, Globe, Coins,
  Lock, Search, Brain, Palette, Layers, Clock, Download, Star,
  MessageSquare
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

/* ═══════════════════════════════════════════════════════════════════
   PRICING ARCHITECTURE — V5.5
   Free / Standard $19 / Pro $99 / Enterprise (contact)
   18% annual discount across all paid plans
   ═══════════════════════════════════════════════════════════════════ */

const ANNUAL_DISCOUNT = 0.18;

const plans = [
  {
    id: "free",
    slug: "free",
    name: "Free",
    desc: "Explore the platform",
    monthlyPrice: 0,
    yearlyPrice: 0,
    priceLabel: "Free",
    icon: Zap,
    dailyCredits: 15,
    monthlyCredits: 450,
    maxDomains: 2,
    features: [
      "15 daily fresh credits",
      "~450 credits / month",
      "2 domains (Global + 1)",
      "Instant search only",
      "Standard response time",
      "Community support",
    ],
    limitations: [
      "No deep search",
      "No agent mode",
      "No file exports",
    ],
    cta: "Get Started",
    href: "/signup",
    highlighted: false,
  },
  {
    id: "standard",
    slug: "standard",
    name: "Standard",
    desc: "For individual researchers",
    monthlyPrice: 19,
    yearlyPrice: Math.round(19 * 12 * (1 - ANNUAL_DISCOUNT)),
    icon: Sparkles,
    dailyCredits: 50,
    monthlyCredits: 1500,
    maxDomains: 5,
    features: [
      "50 daily fresh credits",
      "~1,500 credits / month",
      "5 domains access",
      "Deep search & analysis",
      "Export to PDF, Excel, PPTX",
      "3 concurrent tasks",
      "Priority support",
    ],
    limitations: [],
    cta: "Subscribe",
    highlighted: true,
    badge: "Most Popular",
  },
  {
    id: "pro",
    slug: "pro",
    name: "Pro",
    desc: "For fashion professionals",
    monthlyPrice: 99,
    yearlyPrice: Math.round(99 * 12 * (1 - ANNUAL_DISCOUNT)),
    icon: Crown,
    dailyCredits: 300,
    monthlyCredits: 9000,
    maxDomains: 10,
    features: [
      "300 daily fresh credits",
      "~9,000 credits / month",
      "All 10 domains",
      "Agent mode & creative",
      "Advanced trend forecasting",
      "Supplier intelligence",
      "Unlimited concurrent tasks",
      "Priority support",
    ],
    limitations: [],
    cta: "Subscribe",
    highlighted: false,
  },
  {
    id: "enterprise",
    slug: "enterprise",
    name: "Enterprise",
    desc: "For teams & organizations",
    monthlyPrice: null,
    yearlyPrice: null,
    priceLabel: "Custom",
    icon: Building2,
    dailyCredits: 500,
    monthlyCredits: 25000,
    maxDomains: 10,
    features: [
      "Custom credit allocation",
      "All 10 domains + custom",
      "Dedicated account manager",
      "Custom AI model training",
      "API access & integrations",
      "SSO & advanced security",
      "SLA guarantee",
      "Custom report templates",
    ],
    limitations: [],
    cta: "Contact Sales",
    href: "/contact",
    highlighted: false,
  },
];


const comparisonFeatures = [
  { category: "Credits & Usage", features: [
    { name: "Daily fresh credits", free: "15", standard: "50", pro: "300", enterprise: "500+" },
    { name: "Monthly credits (approx.)", free: "~450", standard: "~1,500", pro: "~9,000", enterprise: "Custom" },
    { name: "Fresh credits usable for", free: "Instant search", standard: "Instant search", pro: "Instant search", enterprise: "Instant search" },
    { name: "Purchased credits usable for", free: "All tasks", standard: "All tasks", pro: "All tasks", enterprise: "All tasks" },
  ]},
  { category: "Research Capabilities", features: [
    { name: "Instant search", free: true, standard: true, pro: true, enterprise: true },
    { name: "Deep search & analysis", free: false, standard: true, pro: true, enterprise: true },
    { name: "Agent mode", free: false, standard: false, pro: true, enterprise: true },
    { name: "Creative mode", free: false, standard: false, pro: true, enterprise: true },
    { name: "Real-time data", free: "Basic", standard: "Standard", pro: "Advanced", enterprise: "Custom" },
    { name: "Concurrent tasks", free: "1", standard: "3", pro: "Unlimited", enterprise: "Unlimited" },
    { name: "Response time", free: "Standard", standard: "Priority", pro: "Priority", enterprise: "Instant" },
  ]},
  { category: "Domain Access", features: [
    { name: "Number of domains", free: "2", standard: "5", pro: "All 10", enterprise: "All 10 + Custom" },
    { name: "Global intelligence", free: true, standard: true, pro: true, enterprise: true },
    { name: "Fashion", free: true, standard: true, pro: true, enterprise: true },
    { name: "Beauty & Skincare", free: false, standard: true, pro: true, enterprise: true },
    { name: "Sustainability", free: false, standard: true, pro: true, enterprise: true },
    { name: "Fashion Tech", free: false, standard: true, pro: true, enterprise: true },
    { name: "Catwalks & Culture", free: false, standard: false, pro: true, enterprise: true },
    { name: "Textile & Lifestyle", free: false, standard: false, pro: true, enterprise: true },
  ]},
  { category: "Exports & Deliverables", features: [
    { name: "PDF reports", free: false, standard: true, pro: true, enterprise: true },
    { name: "Excel exports", free: false, standard: true, pro: true, enterprise: true },
    { name: "PowerPoint decks", free: false, standard: true, pro: true, enterprise: true },
    { name: "Word documents", free: false, standard: true, pro: true, enterprise: true },
    { name: "Custom templates", free: false, standard: false, pro: false, enterprise: true },
  ]},
  { category: "Support", features: [
    { name: "Community support", free: true, standard: true, pro: true, enterprise: true },
    { name: "Priority support", free: false, standard: true, pro: true, enterprise: true },
    { name: "Dedicated account manager", free: false, standard: false, pro: false, enterprise: true },
    { name: "SLA guarantee", free: false, standard: false, pro: false, enterprise: true },
    { name: "Custom integrations", free: false, standard: false, pro: false, enterprise: true },
  ]},
];

const faqs = [
  { q: "What are credits and how do they work?", a: "Credits are the currency for AI research on McLeuker. Each task consumes credits based on complexity — instant search uses fewer credits, while deep research, agent mode, and creative tasks use more. You receive daily fresh credits that refresh every 24 hours, plus you can purchase additional credits from the Usage page in your dashboard." },
  { q: "What's the difference between daily fresh credits and purchased credits?", a: "Daily fresh credits refresh every 24 hours and can only be used for instant search queries. Purchased credits can be used for any task type including deep search, agent mode, and creative tasks. Purchased credits never expire." },
  { q: "What happens when I run out of credits during a task?", a: "If you run out of credits mid-task, the system will pause and prompt you to purchase additional credits to continue. Your progress is saved, so you can resume right where you left off after adding credits." },
  { q: "How much do credits cost?", a: "Credits are priced at a flat rate of $0.10 per credit for all users, starting from 50 credits ($5). There are 18 different credit tiers available from 50 to 25,000 credits. Annual subscribers receive an 18% discount on all credit purchases." },
  { q: "How does domain access work?", a: "Domains are specialized research areas (Fashion, Beauty, Sustainability, etc.). Free users get 2 domains, Standard gets 5, and Pro gets all 10. Locked domains show an upgrade prompt when selected." },
  { q: "Can I change plans later?", a: "Yes, you can upgrade or downgrade at any time. Upgrades take effect immediately with prorated billing. Downgrades apply at the end of your current billing period." },
  { q: "Is there a discount for annual billing?", a: "Yes! Annual billing saves you 18% compared to monthly pricing. Standard drops from $19/mo to $15.58/mo, and Pro drops from $99/mo to $81.18/mo. Annual subscribers also get 18% off all credit purchases." },
  { q: "What payment methods do you accept?", a: "We accept all major credit and debit cards via Stripe. Enterprise plans also support wire transfers and invoicing." },
  { q: "Do you offer refunds?", a: "We offer a 14-day money-back guarantee on all paid plans. Credit pack purchases are non-refundable but never expire." },
];

const PLAN_RANK: Record<string, number> = { free: 0, standard: 1, pro: 2, enterprise: 3 };

export default function PricingPage() {
  const [annual, setAnnual] = useState(true);
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
  const [subscribing, setSubscribing] = useState<string | null>(null);
  const { user, session } = useAuth();
  const [currentPlan, setCurrentPlan] = useState<string | null>(null);

  // Fetch user's current plan if logged in
  useEffect(() => {
    if (!user) { setCurrentPlan(null); return; }
    supabase
      .from('users')
      .select('subscription_plan')
      .eq('id', user.id)
      .single()
      .then(({ data }) => {
        setCurrentPlan(data?.subscription_plan || 'free');
      });
  }, [user]);

  // Determine button text based on login state and current plan
  const getButtonText = (planSlug: string) => {
    if (!user) {
      // Not logged in
      if (planSlug === 'free') return 'Get Started Free';
      if (planSlug === 'enterprise') return 'Contact Sales';
      return 'Subscribe';
    }
    // Logged in
    if (planSlug === 'enterprise') return 'Contact Sales';
    if (currentPlan === planSlug) return 'Current Plan';
    if (PLAN_RANK[planSlug] > PLAN_RANK[currentPlan || 'free']) return 'Upgrade';
    if (PLAN_RANK[planSlug] < PLAN_RANK[currentPlan || 'free']) return 'Downgrade';
    return 'Subscribe';
  };

  const isCurrentPlan = (planSlug: string) => user && currentPlan === planSlug;

  const handleSubscribe = async (planSlug: string) => {
    // Don't do anything if it's the current plan
    if (isCurrentPlan(planSlug)) return;
    if (planSlug === 'free' && !user) {
      window.location.href = '/signup';
      return;
    }
    if (planSlug === 'free' && user) {
      // Already on free or downgrading — go to billing
      window.location.href = '/billing';
      return;
    }
    if (planSlug === 'enterprise') {
      window.location.href = '/contact';
      return;
    }
    if (!session?.access_token) {
      window.location.href = `/login?redirect=/pricing&plan=${planSlug}`;
      return;
    }
    setSubscribing(planSlug);
    try {
      const res = await fetch(`${API_URL}/api/v1/billing/checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan_slug: planSlug,
          billing_interval: annual ? 'year' : 'month',
          mode: 'subscription',
        }),
      });
      const data = await res.json();
      if (data.success && data.url) {
        window.location.href = data.url;
      } else if (data.detail) {
        alert(data.detail);
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
      {/* HERO */}
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
              Start free with 15 daily credits. Upgrade when your research demands it.
              Every plan includes real-time data and structured deliverables.
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
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.08] text-white/60 font-medium">Save 18%</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* PRICING CARDS */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="pb-20 lg:pb-28">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
            {plans.map((plan) => {
              const PlanIcon = plan.icon;
              const price = plan.priceLabel || (annual && plan.yearlyPrice ? `$${Math.round(plan.yearlyPrice / 12)}` : `$${plan.monthlyPrice}`);
              const period = plan.monthlyPrice === null ? '' : annual ? '/mo' : '/mo';
              const billedNote = annual && plan.yearlyPrice ? `Billed $${plan.yearlyPrice}/year` : null;
              return (
                <div
                  key={plan.id}
                  className={cn(
                    "relative p-6 lg:p-7 rounded-2xl border transition-all flex flex-col",
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
                        <span className="text-sm text-white/30">{period}</span>
                      )}
                    </div>
                    {billedNote && (
                      <p className="text-[11px] text-white/25 mt-1">{billedNote}</p>
                    )}
                    <div className="flex items-center gap-1.5 mt-2">
                      <Coins className="w-3 h-3 text-white/30" />
                      <span className="text-xs text-white/40">{plan.dailyCredits} daily credits &middot; {plan.maxDomains === 10 ? 'All' : plan.maxDomains} domains</span>
                    </div>
                  </div>

                  {/* Features */}
                  <ul className="space-y-2.5 mb-4 flex-1">
                    {plan.features.map((feature, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm">
                        <div className="w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 bg-white/[0.04]">
                          <Check className="w-2.5 h-2.5 text-white/50" />
                        </div>
                        <span className="text-white/55">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* Limitations for free */}
                  {plan.limitations && plan.limitations.length > 0 && (
                    <ul className="space-y-1.5 mb-5">
                      {plan.limitations.map((lim, j) => (
                        <li key={j} className="flex items-start gap-2.5 text-sm">
                          <div className="w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 bg-white/[0.02]">
                            <XIcon className="w-2.5 h-2.5 text-white/20" />
                          </div>
                          <span className="text-white/25">{lim}</span>
                        </li>
                      ))}
                    </ul>
                  )}

                  {/* CTA */}
                  <button
                    onClick={() => handleSubscribe(plan.slug)}
                    disabled={subscribing === plan.slug || isCurrentPlan(plan.slug)}
                    className={cn(
                      "w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-medium transition-all mt-auto",
                      isCurrentPlan(plan.slug)
                        ? "border border-[#5c6652]/40 text-[#5c6652] cursor-default"
                        : plan.highlighted
                          ? "bg-white text-[#0A0A0A] hover:bg-white/90"
                          : "border border-white/[0.10] text-white/70 hover:bg-white/[0.05] hover:text-white",
                      subscribing === plan.slug && "opacity-50 cursor-wait"
                    )}
                  >
                    {subscribing === plan.slug ? 'Processing...' : (
                      <>
                        {isCurrentPlan(plan.slug) && <Check className="w-3.5 h-3.5" />}
                        {getButtonText(plan.slug)}
                        {!isCurrentPlan(plan.slug) && subscribing !== plan.slug && <ArrowRight className="w-3.5 h-3.5" />}
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CREDIT INFO BANNER */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-12 lg:py-16 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <div className="p-6 lg:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02]">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.03] border border-white/[0.06] mb-4">
                <Coins className="w-3 h-3 text-white/30" />
                <span className="text-[11px] text-white/35 uppercase tracking-[0.15em]">Credits</span>
              </div>
              <h3 className="font-editorial text-2xl md:text-3xl text-white/[0.95] tracking-tight mb-3">
                Need more credits?
              </h3>
              <p className="text-white/40 text-base max-w-lg mx-auto mb-4">
                Purchase credits starting at $5 from your dashboard. Flat rate of $0.10/credit for all users.
                Annual subscribers save 18% on every credit purchase.
              </p>
              <p className="text-white/30 text-sm">
                Credits never expire and work for all task types including deep search, agent mode, and creative.
              </p>
              <Link
                href={user ? "/billing" : "/login?redirect=/billing"}
                className="inline-flex items-center gap-2 mt-5 px-5 py-2.5 rounded-xl border border-white/[0.10] text-white/60 text-sm hover:bg-white/[0.04] transition-all"
              >
                Buy Credits <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* COMPARISON TABLE */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.95] tracking-tight mb-3">
                Compare Plans
              </h2>
              <p className="text-white/35 text-base">
                Every feature, every capability — side by side.
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.06] overflow-hidden">
              {/* Table Header */}
              <div className="grid grid-cols-5 bg-[#0d0d0d] border-b border-white/[0.06]">
                <div className="p-4 lg:p-5">
                  <span className="text-xs text-white/25 uppercase tracking-wider">Feature</span>
                </div>
                <div className="p-4 lg:p-5 text-center">
                  <span className="text-sm text-white/50">Free</span>
                  <p className="text-[10px] text-white/20 mt-0.5">$0</p>
                </div>
                <div className="p-4 lg:p-5 text-center">
                  <span className="text-sm text-white/50">Standard</span>
                  <p className="text-[10px] text-white/20 mt-0.5">$19/mo</p>
                </div>
                <div className="p-4 lg:p-5 text-center border-x border-white/[0.04]">
                  <span className="text-sm font-medium text-white/80">Pro</span>
                  <p className="text-[10px] text-white/30 mt-0.5">$99/mo</p>
                </div>
                <div className="p-4 lg:p-5 text-center">
                  <span className="text-sm text-white/50">Enterprise</span>
                  <p className="text-[10px] text-white/20 mt-0.5">Custom</p>
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
                      {['free', 'standard', 'pro', 'enterprise'].map((tier, ti) => {
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
      {/* WHAT'S INCLUDED */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#0a0a0a]">
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
                { icon: Search, title: "Real-Time Research", desc: "Live data from across the fashion industry" },
                { icon: FileText, title: "Structured Reports", desc: "Professional, exportable deliverables" },
                { icon: BarChart3, title: "Data Visualization", desc: "Charts, matrices, and comparisons" },
                { icon: Shield, title: "Source Citations", desc: "Every insight is traceable and verifiable" },
                { icon: Globe, title: "Global Coverage", desc: "Multi-market intelligence across regions" },
                { icon: Headphones, title: "Support", desc: "Community support on all plans" },
              ].map((item, i) => {
                const ItemIcon = item.icon;
                return (
                  <div key={i} className="p-5 rounded-xl bg-[#0d0d0d] border border-white/[0.04] hover:border-white/[0.08] transition-all">
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
      <section className="py-20 lg:py-28 bg-[#070707]">
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
      <section className="py-24 lg:py-32 bg-[#0a0a0a] relative overflow-hidden">
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
              Start Free
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
