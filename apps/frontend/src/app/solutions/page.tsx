'use client';

import Link from "next/link";
import { useRef, useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { ArrowRight, TrendingUp, Search, BarChart3, Leaf, Sparkles, Zap, Globe, FileText } from "lucide-react";

const solutions = [
  {
    icon: TrendingUp,
    title: "Trend Forecasting",
    tagline: "See what's next before it happens",
    description: "AI-powered analysis of global fashion trends across runway shows, street style, social media, and consumer behavior. From color palettes to silhouette evolution.",
    stats: [
      { value: "40+", label: "Fashion weeks analyzed" },
      { value: "10K+", label: "Signals tracked weekly" },
      { value: "<5min", label: "Report generation" },
    ],
    features: ["Runway analysis", "Color forecasting", "Material trends", "Silhouette tracking", "Social signals", "Seasonal predictions"],
    gradient: "from-amber-500/10 via-transparent to-transparent",
    accentColor: "amber",
    href: "/solutions/trend-forecasting",
    preview: {
      type: "heatmap",
      data: [
        { name: "Oversized Tailoring", value: 92 },
        { name: "Sheer Fabrics", value: 78 },
        { name: "Burgundy Tones", value: 71 },
        { name: "Utility Details", value: 65 },
        { name: "Metallic Accents", value: 58 },
      ]
    }
  },
  {
    icon: Search,
    title: "Supplier Research",
    tagline: "Find the right partners, faster",
    description: "Comprehensive supplier discovery and due diligence across certifications, capabilities, MOQ requirements, and sustainability credentials worldwide.",
    stats: [
      { value: "50+", label: "Countries covered" },
      { value: "15+", label: "Certifications tracked" },
      { value: "Excel", label: "Export ready" },
    ],
    features: ["Global database", "Certification verification", "MOQ analysis", "Quality assessment", "Sustainability scoring", "Contact details"],
    gradient: "from-blue-500/10 via-transparent to-transparent",
    accentColor: "blue",
    href: "/solutions/supplier-research",
    preview: {
      type: "table",
      data: [
        { supplier: "Candiani", country: "Italy", cert: "GOTS" },
        { supplier: "Tejidos Royo", country: "Spain", cert: "OEKO" },
        { supplier: "Advance Denim", country: "Portugal", cert: "BCI" },
      ]
    }
  },
  {
    icon: BarChart3,
    title: "Market Analysis",
    tagline: "Data-driven competitive intelligence",
    description: "Deep insights into competitive landscapes, pricing strategies, market sizing, and growth opportunities across luxury, mid-range, and DTC segments.",
    stats: [
      { value: "$42B", label: "Market data tracked" },
      { value: "200+", label: "Brands monitored" },
      { value: "PDF", label: "Report format" },
    ],
    features: ["Competitive intelligence", "Pricing benchmarks", "Market sizing", "Growth mapping", "Brand positioning", "Consumer segments"],
    gradient: "from-purple-500/10 via-transparent to-transparent",
    accentColor: "purple",
    href: "/solutions/market-analysis",
    preview: {
      type: "chart",
      data: [
        { segment: "Luxury", share: 35 },
        { segment: "Premium", share: 28 },
        { segment: "Mid-range", share: 22 },
        { segment: "DTC", share: 15 },
      ]
    }
  },
  {
    icon: Leaf,
    title: "Sustainability Insights",
    tagline: "Responsible fashion, measured",
    description: "Expert guidance on certifications, impact measurement, ESG compliance, and sustainable sourcing to build transparent, responsible supply chains.",
    stats: [
      { value: "20+", label: "Frameworks covered" },
      { value: "100%", label: "Source transparency" },
      { value: "Gap", label: "Analysis included" },
    ],
    features: ["Certification tracking", "Impact assessment", "ESG compliance", "Circular models", "Carbon footprint", "Supply chain mapping"],
    gradient: "from-green-500/10 via-transparent to-transparent",
    accentColor: "green",
    href: "/solutions/sustainability-insights",
    preview: {
      type: "metrics",
      data: [
        { label: "GOTS Compliance", value: 94 },
        { label: "Carbon Reduction", value: 67 },
        { label: "Circular Design", value: 45 },
        { label: "Fair Labor", value: 88 },
      ]
    }
  }
];

const accentColors: Record<string, string> = {
  amber: "bg-amber-500/20 text-amber-400",
  blue: "bg-blue-500/20 text-blue-400",
  purple: "bg-purple-500/20 text-purple-400",
  green: "bg-green-500/20 text-green-400",
};

const accentBorders: Record<string, string> = {
  amber: "border-amber-500/20",
  blue: "border-blue-500/20",
  purple: "border-purple-500/20",
  green: "border-green-500/20",
};

const barColors: Record<string, string> = {
  amber: "bg-amber-500/60",
  blue: "bg-blue-500/60",
  purple: "bg-purple-500/60",
  green: "bg-green-500/60",
};

export default function SolutionsPage() {
  const [activeIdx, setActiveIdx] = useState(0);

  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* Hero Section */}
      <section className="relative pt-20 lg:pt-28 pb-12 lg:pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent" />
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-white/[0.015] rounded-full blur-[120px]" />
        
        <div className="container mx-auto px-6 lg:px-12 relative">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] mb-6">
              <Sparkles className="w-3.5 h-3.5 text-white/50" />
              <span className="text-xs text-white/50 uppercase tracking-[0.15em]">AI-Powered Solutions</span>
            </div>
            <h1 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-5 leading-[1.1]">
              Four pillars of<br />fashion intelligence
            </h1>
            <p className="text-white/55 text-lg lg:text-xl max-w-2xl mx-auto mb-10">
              Each solution is purpose-built for fashion professionals. Real-time data, structured outputs, and domain expertise — all in one platform.
            </p>

            {/* Quick nav pills */}
            <div className="flex flex-wrap items-center justify-center gap-3">
              {solutions.map((s, i) => {
                const Icon = s.icon;
                return (
                  <button
                    key={i}
                    onClick={() => {
                      setActiveIdx(i);
                      document.getElementById(`solution-${i}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }}
                    className={cn(
                      "flex items-center gap-2 px-5 py-2.5 rounded-full text-sm transition-all",
                      activeIdx === i
                        ? "bg-white/[0.1] border border-white/[0.15] text-white"
                        : "bg-white/[0.03] border border-white/[0.06] text-white/50 hover:text-white/70 hover:border-white/[0.1]"
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {s.title}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Solutions — Full-width immersive cards */}
      <section className="pb-12 lg:pb-16">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto space-y-8">
            {solutions.map((solution, i) => {
              const IconComponent = solution.icon;
              const isEven = i % 2 === 0;
              return (
                <div
                  key={i}
                  id={`solution-${i}`}
                  className={cn(
                    "group relative rounded-[24px] overflow-hidden",
                    "bg-gradient-to-b from-[#111111] to-[#0A0A0A]",
                    "border border-white/[0.06] hover:border-white/[0.12] transition-all duration-500"
                  )}
                >
                  {/* Gradient glow */}
                  <div className={cn("absolute inset-0 bg-gradient-to-br opacity-40", solution.gradient)} />
                  
                  <div className={cn(
                    "relative grid lg:grid-cols-2 gap-8 lg:gap-0",
                    !isEven && "lg:[direction:rtl]"
                  )}>
                    {/* Content Side */}
                    <div className={cn("p-8 lg:p-12 lg:[direction:ltr]")}>
                      <div className="flex items-center gap-3 mb-6">
                        <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center", accentColors[solution.accentColor])}>
                          <IconComponent className="w-5 h-5" />
                        </div>
                        <span className="text-xs text-white/40 uppercase tracking-[0.15em]">Solution {String(i + 1).padStart(2, '0')}</span>
                      </div>

                      <h2 className="font-editorial text-3xl lg:text-4xl text-white/[0.92] mb-2 leading-tight">
                        {solution.title}
                      </h2>
                      <p className="text-white/50 text-lg mb-4 italic">{solution.tagline}</p>
                      <p className="text-white/55 leading-relaxed mb-8 max-w-lg">
                        {solution.description}
                      </p>

                      {/* Stats row */}
                      <div className="flex gap-6 mb-8">
                        {solution.stats.map((stat, j) => (
                          <div key={j}>
                            <div className="text-2xl font-semibold text-white/[0.85] mb-0.5">{stat.value}</div>
                            <div className="text-xs text-white/35">{stat.label}</div>
                          </div>
                        ))}
                      </div>

                      {/* Features grid */}
                      <div className="grid grid-cols-2 gap-2 mb-8">
                        {solution.features.map((feature, j) => (
                          <div key={j} className="flex items-center gap-2 text-sm text-white/50">
                            <div className="w-1 h-1 rounded-full bg-white/30" />
                            {feature}
                          </div>
                        ))}
                      </div>

                      <Link
                        href={solution.href}
                        className={cn(
                          "inline-flex items-center gap-2 px-6 py-3 rounded-full text-sm font-medium transition-all",
                          "bg-white text-black hover:bg-white/90",
                          "group-hover:shadow-lg group-hover:shadow-white/5"
                        )}
                      >
                        Explore {solution.title}
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                      </Link>
                    </div>

                    {/* Preview Side */}
                    <div className={cn(
                      "relative p-8 lg:p-12 lg:[direction:ltr]",
                      "flex items-center justify-center",
                      "bg-gradient-to-br from-white/[0.02] to-transparent"
                    )}>
                      <div className="w-full max-w-md">
                        {/* Preview mockup */}
                        <div className={cn(
                          "rounded-2xl overflow-hidden",
                          "bg-[#0A0A0A] border",
                          accentBorders[solution.accentColor]
                        )}>
                          {/* Window bar */}
                          <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06]">
                            <div className="flex gap-1.5">
                              <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                              <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                              <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                            </div>
                            <div className="flex-1 text-center">
                              <span className="text-[10px] text-white/25 font-mono">mcleukerai.com/dashboard</span>
                            </div>
                          </div>

                          {/* Content based on type */}
                          <div className="p-5">
                            {solution.preview.type === "heatmap" && (
                              <div className="space-y-3">
                                <p className="text-[10px] text-white/30 uppercase tracking-wider mb-4">Trend Heatmap — SS26</p>
                                {(solution.preview.data as Array<{name: string; value: number}>).map((item, j) => (
                                  <div key={j} className="flex items-center gap-3">
                                    <span className="text-xs text-white/50 w-32 truncate">{item.name}</span>
                                    <div className="flex-1 h-5 bg-white/[0.04] rounded-full overflow-hidden">
                                      <div
                                        className={cn("h-full rounded-full transition-all duration-1000", barColors[solution.accentColor])}
                                        style={{ width: `${item.value}%` }}
                                      />
                                    </div>
                                    <span className="text-xs text-white/40 w-8 text-right">{item.value}%</span>
                                  </div>
                                ))}
                              </div>
                            )}

                            {solution.preview.type === "table" && (
                              <div>
                                <p className="text-[10px] text-white/30 uppercase tracking-wider mb-4">Supplier Comparison</p>
                                <div className="space-y-0">
                                  <div className="grid grid-cols-3 gap-2 pb-2 border-b border-white/[0.06]">
                                    <span className="text-[10px] text-white/30 uppercase">Supplier</span>
                                    <span className="text-[10px] text-white/30 uppercase">Country</span>
                                    <span className="text-[10px] text-white/30 uppercase">Cert.</span>
                                  </div>
                                  {(solution.preview.data as Array<{supplier: string; country: string; cert: string}>).map((row, j) => (
                                    <div key={j} className="grid grid-cols-3 gap-2 py-2.5 border-b border-white/[0.03]">
                                      <span className="text-xs text-white/60">{row.supplier}</span>
                                      <span className="text-xs text-white/45">{row.country}</span>
                                      <span className={cn("text-[10px] px-2 py-0.5 rounded-full w-fit", accentColors[solution.accentColor])}>{row.cert}</span>
                                    </div>
                                  ))}
                                </div>
                                <p className="text-[10px] text-white/20 mt-3">+ 29 more suppliers across 12 countries</p>
                              </div>
                            )}

                            {solution.preview.type === "chart" && (
                              <div>
                                <p className="text-[10px] text-white/30 uppercase tracking-wider mb-4">Market Share by Segment</p>
                                <div className="flex items-end gap-3 h-32 mb-3">
                                  {(solution.preview.data as Array<{segment: string; share: number}>).map((item, j) => (
                                    <div key={j} className="flex-1 flex flex-col items-center gap-2">
                                      <span className="text-[10px] text-white/40">{item.share}%</span>
                                      <div
                                        className={cn("w-full rounded-t-lg transition-all duration-1000", barColors[solution.accentColor])}
                                        style={{ height: `${item.share * 2.5}px` }}
                                      />
                                      <span className="text-[9px] text-white/30">{item.segment}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {solution.preview.type === "metrics" && (
                              <div>
                                <p className="text-[10px] text-white/30 uppercase tracking-wider mb-4">Compliance Dashboard</p>
                                <div className="grid grid-cols-2 gap-3">
                                  {(solution.preview.data as Array<{label: string; value: number}>).map((item, j) => (
                                    <div key={j} className="bg-white/[0.03] rounded-xl p-3 border border-white/[0.04]">
                                      <div className="text-xl font-semibold text-white/[0.8] mb-1">{item.value}%</div>
                                      <div className="text-[10px] text-white/35">{item.label}</div>
                                      <div className="mt-2 h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                                        <div
                                          className={cn("h-full rounded-full", barColors[solution.accentColor])}
                                          style={{ width: `${item.value}%` }}
                                        />
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Capabilities Banner */}
      <section className="py-12 lg:py-16 border-y border-white/[0.04]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
              {[
                { icon: Zap, label: "Real-time intelligence", desc: "Live signals from web, social, and search" },
                { icon: Globe, label: "10 specialized domains", desc: "Fashion, beauty, skincare, and more" },
                { icon: FileText, label: "Export everything", desc: "PDF, Excel, PPTX, and Word formats" },
                { icon: Sparkles, label: "Multi-model AI", desc: "Best model selected per task" },
              ].map((item, i) => {
                const Icon = item.icon;
                return (
                  <div key={i} className="text-center">
                    <div className="w-12 h-12 rounded-xl bg-white/[0.04] border border-white/[0.06] flex items-center justify-center mx-auto mb-3">
                      <Icon className="w-5 h-5 text-white/50" />
                    </div>
                    <h4 className="text-sm font-medium text-white/[0.8] mb-1">{item.label}</h4>
                    <p className="text-xs text-white/35">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 lg:py-24">
        <div className="container mx-auto px-6 lg:px-12 text-center">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.92] mb-4">
              Ready to transform your research?
            </h2>
            <p className="text-white/50 text-lg mb-8">
              Start with any solution. Your first research task is on us.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors"
              >
                Start Research
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/pricing"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full border border-white/[0.15] text-white/80 hover:bg-white/[0.06] transition-colors"
              >
                View Pricing
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
