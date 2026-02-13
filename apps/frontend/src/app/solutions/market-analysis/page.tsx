'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { BarChart3, ArrowRight, Check, Sparkles, Target, DollarSign, Users, PieChart, TrendingUp } from "lucide-react";

const marketSegments = [
  { segment: "Luxury", share: 35, revenue: "$14.7B", growth: "+4.2%" },
  { segment: "Premium", share: 28, revenue: "$11.8B", growth: "+6.1%" },
  { segment: "Mid-range", share: 22, revenue: "$9.2B", growth: "+3.8%" },
  { segment: "DTC / Indie", share: 15, revenue: "$6.3B", growth: "+12.4%" },
];

const capabilities = [
  { icon: Target, title: "Competitive Intelligence", desc: "Brand positioning, pricing strategies, and market share analysis across segments" },
  { icon: DollarSign, title: "Pricing Benchmarks", desc: "Category-level pricing data with regional variations and seasonal adjustments" },
  { icon: PieChart, title: "Market Sizing", desc: "TAM, SAM, SOM calculations with growth projections and segment breakdowns" },
  { icon: Users, title: "Consumer Segments", desc: "Demographic and psychographic profiling with spending behavior analysis" },
  { icon: TrendingUp, title: "Growth Mapping", desc: "Emerging market opportunities, white space analysis, and expansion potential" },
  { icon: Sparkles, title: "AI Synthesis", desc: "Multi-source data fusion from financial reports, social signals, and trade data" },
];

const workflow = [
  { step: "01", title: "Brief", desc: "\"Analyze the European sustainable fashion market for DTC brands\"", detail: "Define market, segment, geography, and competitive scope" },
  { step: "02", title: "Gather", desc: "AI collects data from financial reports, trade publications, and market databases", detail: "Real-time data from multiple verified sources" },
  { step: "03", title: "Analyze", desc: "Competitive positioning, pricing benchmarks, and growth opportunities identified", detail: "Statistical modeling and trend correlation" },
  { step: "04", title: "Report", desc: "Professional PDF with charts, executive summary, and strategic recommendations", detail: "Board-ready format with source citations" },
];

export default function MarketAnalysisPage() {
  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* Hero — Monochromatic */}
      <section className="relative pt-20 lg:pt-28 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent" />
        <div className="absolute top-40 right-0 w-[500px] h-[500px] bg-white/[0.01] rounded-full blur-[120px]" />
        
        <div className="container mx-auto px-6 lg:px-12 relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] mb-6">
                <BarChart3 className="w-3.5 h-3.5 text-white/50" />
                <span className="text-xs text-white/50 uppercase tracking-[0.15em]">Market Analysis</span>
              </div>
              <h1 className="font-editorial text-4xl md:text-5xl lg:text-[3.5rem] text-white/[0.92] mb-5 leading-[1.1]">
                Data-driven<br />competitive intelligence
              </h1>
              <p className="text-white/55 text-lg leading-relaxed mb-8 max-w-lg">
                Deep insights into competitive landscapes, pricing strategies, market sizing, and growth opportunities across luxury, mid-range, and DTC segments.
              </p>
              <div className="flex flex-wrap gap-4 mb-10">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
                  Try Market Analysis <ArrowRight className="w-4 h-4" />
                </Link>
                <Link href="/solutions" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full border border-white/[0.12] text-white/70 hover:bg-white/[0.04] transition-colors">
                  All Solutions
                </Link>
              </div>
              <div className="flex gap-8">
                {[
                  { value: "$42B", label: "Market tracked" },
                  { value: "200+", label: "Brands monitored" },
                  { value: "PDF", label: "Report format" },
                ].map((s, i) => (
                  <div key={i}>
                    <div className="text-2xl font-semibold text-white/[0.85]">{s.value}</div>
                    <div className="text-xs text-white/35">{s.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Chart preview mockup — Monochromatic */}
            <div className="relative">
              <div className="rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.08] shadow-2xl shadow-black/40">
                <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] bg-[#0A0A0A]">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                  </div>
                  <span className="text-[10px] text-white/20 font-mono mx-auto">market_analysis_2026.pdf</span>
                </div>
                <div className="p-6">
                  <p className="text-[10px] text-white/30 uppercase tracking-wider mb-1">McLeuker AI Report</p>
                  <h3 className="text-lg font-medium text-white/80 mb-5">European Fashion Market — Segment Breakdown</h3>
                  
                  {/* Bar chart — Monochromatic shades */}
                  <div className="flex items-end gap-4 h-40 mb-4 px-4">
                    {marketSegments.map((seg, i) => (
                      <div key={i} className="flex-1 flex flex-col items-center gap-2">
                        <span className="text-[10px] text-white/40">{seg.share}%</span>
                        <div
                          className="w-full rounded-t-lg"
                          style={{
                            height: `${seg.share * 3}px`,
                            backgroundColor: `rgba(255,255,255,${0.08 + (seg.share / 100) * 0.25})`
                          }}
                        />
                        <span className="text-[9px] text-white/30 text-center">{seg.segment}</span>
                      </div>
                    ))}
                  </div>

                  {/* Data table */}
                  <div className="border-t border-white/[0.06] pt-3">
                    <div className="grid grid-cols-4 gap-2 mb-2">
                      {["Segment", "Revenue", "Growth", "Share"].map((h, i) => (
                        <span key={i} className="text-[9px] text-white/25 uppercase">{h}</span>
                      ))}
                    </div>
                    {marketSegments.map((seg, i) => (
                      <div key={i} className="grid grid-cols-4 gap-2 py-1.5 border-b border-white/[0.03]">
                        <span className="text-[10px] text-white/50">{seg.segment}</span>
                        <span className="text-[10px] text-white/40">{seg.revenue}</span>
                        <span className="text-[10px] text-white/50">{seg.growth}</span>
                        <span className="text-[10px] text-white/40">{seg.share}%</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-[10px] text-white/15">Source: Euromonitor, BoF, McKinsey</span>
                    <span className="text-[10px] text-white/30">Page 5 of 18</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Grid — Monochromatic */}
      <section className="py-12 lg:py-16 border-y border-white/[0.04]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">What you get</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {capabilities.map((cap, i) => {
                const Icon = cap.icon;
                return (
                  <div key={i} className="group p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-white/[0.12] transition-all">
                    <Icon className="w-5 h-5 text-white/40 group-hover:text-white/60 transition-colors mb-3" />
                    <h3 className="text-sm font-medium text-white/[0.8] mb-1.5">{cap.title}</h3>
                    <p className="text-xs text-white/40 leading-relaxed">{cap.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Workflow — Monochromatic */}
      <section className="py-12 lg:py-16">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">How it works</h2>
            <div className="space-y-0">
              {workflow.map((step, i) => (
                <div key={i} className="flex gap-6 relative">
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-white/[0.04] border border-white/[0.08] flex items-center justify-center shrink-0">
                      <span className="text-xs font-mono text-white/50">{step.step}</span>
                    </div>
                    {i < workflow.length - 1 && <div className="w-px flex-1 bg-white/[0.06] my-2" />}
                  </div>
                  <div className="pb-10">
                    <h3 className="text-lg font-medium text-white/[0.85] mb-1">{step.title}</h3>
                    <p className="text-white/55 mb-1">{step.desc}</p>
                    <p className="text-xs text-white/30">{step.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Who it's for — Monochromatic */}
      <section className="py-12 lg:py-16 border-t border-white/[0.04]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">Who it&apos;s for</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                "Strategy Teams",
                "Brand Managers",
                "Investors & VCs",
                "Business Development",
                "Marketing Directors",
                "Retail Executives",
              ].map((role, i) => (
                <div key={i} className="flex items-center gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                  <Check className="w-4 h-4 text-white/40 shrink-0" />
                  <span className="text-sm text-white/60">{role}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 lg:py-20">
        <div className="container mx-auto px-6 lg:px-12 text-center">
          <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.92] mb-4">
            Your next market report, in minutes
          </h2>
          <p className="text-white/50 text-lg mb-8 max-w-xl mx-auto">
            Board-ready competitive intelligence without the consulting fees.
          </p>
          <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
            Try Market Analysis <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
