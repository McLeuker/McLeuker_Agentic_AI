'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { TrendingUp, ArrowRight, Check, Sparkles, Eye, Palette, Layers, BarChart3, Globe } from "lucide-react";

const trendData = [
  { name: "Oversized Tailoring", value: 92, change: "+12%" },
  { name: "Sheer Fabrics", value: 78, change: "+8%" },
  { name: "Burgundy Tones", value: 71, change: "+15%" },
  { name: "Utility Details", value: 65, change: "+5%" },
  { name: "Metallic Accents", value: 58, change: "+22%" },
  { name: "Maxi Lengths", value: 52, change: "+3%" },
];

const capabilities = [
  { icon: Eye, title: "Runway Analysis", desc: "Every major fashion week decoded — Milan, Paris, London, New York, and 36 more" },
  { icon: Palette, title: "Color Forecasting", desc: "Pantone-referenced color predictions with adoption timeline projections" },
  { icon: Layers, title: "Material Trends", desc: "Fabric innovation tracking from technical textiles to sustainable alternatives" },
  { icon: BarChart3, title: "Consumer Signals", desc: "Social media sentiment, search trends, and retail data cross-referenced" },
  { icon: Globe, title: "Regional Mapping", desc: "How trends translate across markets — from Seoul to São Paulo" },
  { icon: Sparkles, title: "Predictive Models", desc: "AI-powered forecasting that identifies emerging trends before mainstream adoption" },
];

const workflow = [
  { step: "01", title: "Ask", desc: "\"Analyze SS26 womenswear trends from Milan and Paris\"", detail: "Natural language — no templates needed" },
  { step: "02", title: "Analyze", desc: "AI processes 40+ fashion weeks, 10K+ social signals", detail: "Multi-model analysis in parallel" },
  { step: "03", title: "Structure", desc: "Findings organized into trend heatmaps, comparisons, and forecasts", detail: "Charts, tables, and visual references" },
  { step: "04", title: "Deliver", desc: "12-page PDF report with executive summary and recommendations", detail: "Export as PDF, PPTX, or Excel" },
];

export default function TrendForecastingPage() {
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
                <TrendingUp className="w-3.5 h-3.5 text-white/50" />
                <span className="text-xs text-white/50 uppercase tracking-[0.15em]">Trend Forecasting</span>
              </div>
              <h1 className="font-editorial text-4xl md:text-5xl lg:text-[3.5rem] text-white/[0.92] mb-5 leading-[1.1]">
                See what&apos;s next<br />before it happens
              </h1>
              <p className="text-white/55 text-lg leading-relaxed mb-8 max-w-lg">
                AI-powered trend intelligence that analyzes runway shows, street style, social media, and consumer behavior to give you a structured view of what&apos;s coming.
              </p>
              <div className="flex flex-wrap gap-4 mb-10">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
                  Try Trend Forecasting <ArrowRight className="w-4 h-4" />
                </Link>
                <Link href="/solutions" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full border border-white/[0.12] text-white/70 hover:bg-white/[0.04] transition-colors">
                  All Solutions
                </Link>
              </div>
              <div className="flex gap-8">
                {[
                  { value: "40+", label: "Fashion weeks" },
                  { value: "10K+", label: "Signals / week" },
                  { value: "<5min", label: "Report time" },
                ].map((s, i) => (
                  <div key={i}>
                    <div className="text-2xl font-semibold text-white/[0.85]">{s.value}</div>
                    <div className="text-xs text-white/35">{s.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Live preview mockup — Monochromatic */}
            <div className="relative">
              <div className="rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.08] shadow-2xl shadow-black/40">
                <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] bg-[#0A0A0A]">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                  </div>
                  <span className="text-[10px] text-white/20 font-mono mx-auto">trend_analysis_ss26.pdf</span>
                </div>
                <div className="p-6">
                  <p className="text-[10px] text-white/30 uppercase tracking-wider mb-1">McLeuker AI Report</p>
                  <h3 className="text-lg font-medium text-white/80 mb-4">SS26 Trend Heatmap</h3>
                  <div className="space-y-3">
                    {trendData.map((item, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <span className="text-xs text-white/50 w-36 truncate">{item.name}</span>
                        <div className="flex-1 h-6 bg-white/[0.04] rounded-lg overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-white/30 to-white/15 rounded-lg flex items-center justify-end pr-2" style={{ width: `${item.value}%` }}>
                            <span className="text-[10px] text-white/70 font-medium">{item.value}%</span>
                          </div>
                        </div>
                        <span className="text-[10px] text-white/40 w-10 text-right">{item.change}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 pt-3 border-t border-white/[0.04] flex items-center justify-between">
                    <span className="text-[10px] text-white/20">Source: 47 runway shows analyzed</span>
                    <span className="text-[10px] text-white/30">Page 3 of 12</span>
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
                "Creative Directors",
                "Design Teams",
                "Buyers & Merchandisers",
                "Product Developers",
                "Fashion Students",
                "Trend Researchers",
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
            Your next trend report, in minutes
          </h2>
          <p className="text-white/50 text-lg mb-8 max-w-xl mx-auto">
            Stop spending weeks on manual research. Get structured trend intelligence now.
          </p>
          <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
            Try Trend Forecasting <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
