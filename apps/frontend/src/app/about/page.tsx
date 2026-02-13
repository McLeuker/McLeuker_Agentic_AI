'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import {
  ArrowRight, Leaf, Target, Users, Sparkles, Brain, Zap, Globe,
  Layers, Shield, Eye, Code, BarChart3, TrendingUp, FileText,
  Cpu, Heart, Shirt, Droplets, Factory, Palette
} from "lucide-react";

const timeline = [
  { year: "2024", title: "The Idea", desc: "Identified the gap between fashion industry needs and AI capabilities. Research began." },
  { year: "2025", title: "Building", desc: "Assembled the team, built the multi-model AI architecture, and onboarded first beta users." },
  { year: "2026", title: "Launch", desc: "McLeuker AI goes live with 10 specialized domains, professional report generation, and real-time intelligence." },
  { year: "Next", title: "Vision", desc: "Expanding to 20+ domains, predictive analytics, and becoming the operating system for fashion intelligence." },
];

const techStack = [
  { icon: Brain, label: "Multi-Model AI", desc: "4+ AI models working in parallel for every query" },
  { icon: Zap, label: "Real-Time Signals", desc: "Live data from web, social, and search sources" },
  { icon: Layers, label: "Structured Output", desc: "Tables, matrices, comparisons — not chat responses" },
  { icon: Shield, label: "Source-Backed", desc: "Every insight traceable to its original source" },
  { icon: Code, label: "Export Engine", desc: "Generate .xlsx, .pdf, .pptx, .docx automatically" },
  { icon: Globe, label: "10 Domains", desc: "Fashion, Beauty, Skincare, Sustainability, and more" },
];

const values = [
  {
    icon: Target,
    title: "Precision Over Volume",
    description: "We don't flood you with data. Every insight is curated, verified, and structured for action.",
  },
  {
    icon: Leaf,
    title: "Sustainability First",
    description: "Environmental responsibility isn't a feature — it's a foundation. Every tool we build considers impact.",
  },
  {
    icon: Eye,
    title: "Radical Transparency",
    description: "See exactly how our AI works. Every source cited, every reasoning step visible, every confidence level shown.",
  },
  {
    icon: Sparkles,
    title: "Fashion-Native AI",
    description: "Built by people who understand fashion. Our AI speaks the industry's language — from MOQs to silhouettes.",
  },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* ═══════════════════════════════════════════════════════ */}
      {/* HERO — Bold statement, monochromatic */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative pt-24 lg:pt-32 pb-20 lg:pb-28 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute inset-0 opacity-[0.015]" style={{
            backgroundImage: `repeating-linear-gradient(45deg, transparent, transparent 60px, white 60px, white 61px)`,
          }} />
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full bg-white/[0.015] blur-[120px]" />
        </div>

        <div className="relative z-10 container mx-auto px-6 lg:px-12">
          <div className="max-w-5xl mx-auto">
            <div className="flex justify-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06]">
                <div className="w-1.5 h-1.5 rounded-full bg-white/30 animate-pulse" />
                <span className="text-[11px] text-white/40 uppercase tracking-[0.15em]">About McLeuker AI</span>
              </div>
            </div>

            <h1 className="font-editorial text-5xl md:text-6xl lg:text-[5.5rem] text-center text-white/[0.95] tracking-tight leading-[1.02] mb-6">
              We&apos;re building the<br />
              <span className="text-white/50">intelligence layer</span>
              <br />for fashion
            </h1>

            <p className="text-center text-white/40 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-12">
              Where AI-powered research meets fashion expertise. From one prompt to structured reports, benchmarks, and clear next steps.
            </p>

            {/* Key metrics — monochromatic */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl mx-auto">
              {[
                { value: "10", label: "Specialized Domains" },
                { value: "4+", label: "AI Models in Parallel" },
                { value: "<5min", label: "Prompt to Report" },
                { value: "24/7", label: "Live Intelligence" },
              ].map((m, i) => (
                <div key={i} className="text-center p-4 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                  <div className="text-2xl md:text-3xl font-light text-white/70 mb-1">{m.value}</div>
                  <div className="text-[10px] text-white/25 uppercase tracking-wider">{m.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* MISSION — Split layout */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
              <div>
                <div className="flex items-center gap-3 mb-5">
                  <div className="h-px w-8 bg-white/20" />
                  <span className="text-[11px] text-white/40 uppercase tracking-[0.2em] font-medium">Our Mission</span>
                </div>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight leading-[1.08] mb-6">
                  Empowering fashion with intelligence
                </h2>
                <div className="space-y-5 text-white/45 text-base leading-relaxed">
                  <p>
                    The fashion industry stands at a crossroads. The demand for faster trend cycles,
                    sustainable practices, and data-driven decisions has never been greater — yet the
                    tools available haven&apos;t kept up.
                  </p>
                  <p>
                    McLeuker AI was born from a simple observation: fashion professionals spend 60% of
                    their time on research that could be automated, structured, and delivered in minutes
                    instead of days.
                  </p>
                  <p>
                    We&apos;re building the comprehensive intelligence platform that modern fashion
                    businesses need — where AI handles the research heavy lifting so professionals
                    can focus on what they do best: creating.
                  </p>
                </div>
              </div>

              {/* Right: Visual — Stacked capability cards */}
              <div className="relative">
                <div className="space-y-3">
                  {[
                    { icon: TrendingUp, label: "Trend Forecasting", prompt: "Analyze SS26 denim trends across European markets", time: "3m 42s" },
                    { icon: Users, label: "Supplier Research", prompt: "Find GOTS-certified denim mills in Europe with MOQ < 500", time: "4m 18s" },
                    { icon: BarChart3, label: "Market Analysis", prompt: "Compare luxury handbag pricing across US, EU, and Asia", time: "2m 55s" },
                    { icon: Leaf, label: "Sustainability Audit", prompt: "Map EPR compliance requirements for textile exports to EU", time: "3m 10s" },
                  ].map((item, i) => {
                    const ItemIcon = item.icon;
                    return (
                      <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-[#0d0d0d] border border-white/[0.04] hover:border-white/[0.08] transition-all group">
                        <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 border border-white/[0.06] bg-white/[0.02]">
                          <ItemIcon className="w-5 h-5 text-white/40" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-0.5">
                            <span className="text-xs font-medium text-white/60">{item.label}</span>
                            <span className="text-[10px] text-white/20 font-mono">{item.time}</span>
                          </div>
                          <p className="text-[11px] text-white/30 truncate">&ldquo;{item.prompt}&rdquo;</p>
                        </div>
                        <div className="w-1.5 h-1.5 rounded-full flex-shrink-0 bg-white/20" />
                      </div>
                    );
                  })}
                </div>
                <div className="absolute -top-8 -right-8 w-32 h-32 rounded-full bg-white/[0.01] blur-[60px] pointer-events-none" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* TECHNOLOGY — What powers McLeuker */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="text-center mb-14">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="h-px w-12 bg-gradient-to-r from-transparent to-white/10" />
                <span className="text-[11px] text-white/40 uppercase tracking-[0.2em] font-medium">Technology</span>
                <div className="h-px w-12 bg-gradient-to-l from-transparent to-white/10" />
              </div>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight">
                What Powers McLeuker
              </h2>
              <p className="text-white/35 text-base max-w-xl mx-auto mt-4 leading-relaxed">
                A multi-model AI architecture built specifically for fashion intelligence.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {techStack.map((tech, i) => {
                const TechIcon = tech.icon;
                return (
                  <div key={i} className="group p-6 rounded-2xl bg-[#0a0a0a] border border-white/[0.04] hover:border-white/[0.08] transition-all">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-9 h-9 rounded-lg flex items-center justify-center border border-white/[0.06] bg-white/[0.02]">
                        <TechIcon className="w-4.5 h-4.5 text-white/40" />
                      </div>
                      <h3 className="text-sm font-medium text-white/80">{tech.label}</h3>
                    </div>
                    <p className="text-[13px] text-white/35 leading-relaxed">{tech.desc}</p>
                  </div>
                );
              })}
            </div>

            {/* Architecture visual — monochromatic */}
            <div className="mt-10 p-6 lg:p-8 rounded-2xl bg-[#0a0a0a] border border-white/[0.04]">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-2 h-2 rounded-full bg-white/20" />
                <span className="text-[10px] text-white/25 uppercase tracking-wider font-mono">Architecture Pipeline</span>
              </div>
              <div className="flex flex-col md:flex-row items-stretch gap-3">
                {[
                  { label: "Your Prompt", sub: "Natural language", icon: "→" },
                  { label: "Domain Router", sub: "Context detection", icon: "→" },
                  { label: "Multi-Model AI", sub: "4+ models parallel", icon: "→" },
                  { label: "Source Crawler", sub: "10K+ live sources", icon: "→" },
                  { label: "Analysis Engine", sub: "Structured output", icon: "→" },
                  { label: "Export", sub: ".xlsx .pdf .pptx", icon: "" },
                ].map((step, i) => (
                  <div key={i} className="flex items-center gap-3 flex-1">
                    <div className="flex-1 p-3 rounded-lg border border-white/[0.06] bg-white/[0.02] text-center">
                      <div className="text-xs font-medium text-white/60 mb-0.5">{step.label}</div>
                      <div className="text-[9px] text-white/25">{step.sub}</div>
                    </div>
                    {step.icon && <span className="text-white/10 text-lg hidden md:block">{step.icon}</span>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* TIMELINE — Our journey */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="flex items-center gap-3 mb-5">
              <div className="h-px w-8 bg-white/20" />
              <span className="text-[11px] text-white/40 uppercase tracking-[0.2em] font-medium">Our Journey</span>
            </div>
            <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight mb-12">
              From idea to intelligence
            </h2>

            <div className="relative">
              <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-white/10 via-white/5 to-transparent hidden md:block" />

              <div className="space-y-8 md:space-y-0 md:grid md:grid-cols-4 md:gap-6">
                {timeline.map((item, i) => (
                  <div key={i} className="relative group">
                    <div className="md:hidden absolute left-6 top-6 w-3 h-3 rounded-full border-2 z-10 border-white/20 bg-white/5" />

                    <div className="md:pl-0 pl-14 p-5 rounded-xl bg-[#0d0d0d] border border-white/[0.04] hover:border-white/[0.08] transition-all">
                      <div className="inline-flex px-3 py-1 rounded-md mb-3 text-xs font-mono font-medium bg-white/[0.04] text-white/60">
                        {item.year}
                      </div>
                      <h3 className="text-lg font-medium text-white/85 mb-2">{item.title}</h3>
                      <p className="text-sm text-white/35 leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* VALUES — What drives us */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="text-center mb-14">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="h-px w-12 bg-gradient-to-r from-transparent to-white/10" />
                <span className="text-[11px] text-white/40 uppercase tracking-[0.2em] font-medium">Our Values</span>
                <div className="h-px w-12 bg-gradient-to-l from-transparent to-white/10" />
              </div>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight">
                What Drives Us
              </h2>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {values.map((value, i) => {
                const ValueIcon = value.icon;
                return (
                  <div key={i} className="group relative p-7 rounded-2xl bg-[#0a0a0a] border border-white/[0.04] hover:border-white/[0.08] transition-all overflow-hidden">
                    {/* Subtle top bar */}
                    <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-white/[0.08] via-white/[0.04] to-transparent" />

                    <div className="flex items-start gap-4">
                      <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 border border-white/[0.06] bg-white/[0.02]">
                        <ValueIcon className="w-5 h-5 text-white/40" />
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-white/85 mb-2">{value.title}</h3>
                        <p className="text-sm text-white/35 leading-relaxed">{value.description}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* DOMAINS OVERVIEW — Monochromatic grid */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.95] tracking-tight mb-3">
                10 Specialized Domains
              </h2>
              <p className="text-white/35 text-base">
                Each domain has curated sources, specialized models, and industry-specific analysis.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {[
                { icon: Shirt, name: "Fashion" },
                { icon: Heart, name: "Beauty" },
                { icon: Droplets, name: "Skincare" },
                { icon: Leaf, name: "Sustainability" },
                { icon: Cpu, name: "Fashion Tech" },
                { icon: Sparkles, name: "Catwalks" },
                { icon: Palette, name: "Culture" },
                { icon: Factory, name: "Textile" },
                { icon: Users, name: "Lifestyle" },
                { icon: Globe, name: "Global" },
              ].map((d, i) => {
                const DIcon = d.icon;
                return (
                  <Link
                    key={i}
                    href={d.name === "Global" ? "/dashboard" : `/domain/${d.name.toLowerCase().replace(' ', '-')}`}
                    className="group flex flex-col items-center gap-2 p-4 rounded-xl border border-white/[0.04] bg-white/[0.01] transition-all hover:bg-white/[0.03] hover:border-white/[0.08] hover:scale-105"
                  >
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center border border-white/[0.06] bg-white/[0.02]">
                      <DIcon className="w-5 h-5 text-white/40 group-hover:text-white/60 transition-colors" />
                    </div>
                    <span className="text-xs text-white/40 group-hover:text-white/70 transition-colors">{d.name}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CAPABILITIES — Areas of expertise */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-start">
              <div>
                <div className="flex items-center gap-3 mb-5">
                  <div className="h-px w-8 bg-white/20" />
                  <span className="text-[11px] text-white/40 uppercase tracking-[0.2em] font-medium">Capabilities</span>
                </div>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight leading-[1.08] mb-5">
                  Areas of<br />Expertise
                </h2>
                <p className="text-white/40 text-base leading-relaxed max-w-md">
                  From strategic planning to supply chain intelligence, McLeuker AI covers the full spectrum of fashion research needs.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {[
                  { title: "Strategy & Planning", desc: "Collection planning, market entry, brand positioning" },
                  { title: "Sustainability", desc: "Impact analysis, certification mapping, ESG reporting" },
                  { title: "Circularity", desc: "Circular models, resale analysis, waste reduction" },
                  { title: "Traceability", desc: "Supply chain transparency, due diligence, compliance" },
                  { title: "Sourcing", desc: "Supplier discovery, capability assessment, evaluation" },
                  { title: "Market Intelligence", desc: "Competitive analysis, pricing, consumer trends" },
                ].map((cap, i) => (
                  <div key={i} className="p-4 rounded-xl bg-[#0a0a0a] border border-white/[0.04] hover:border-white/[0.08] transition-all">
                    <div className="w-1.5 h-1.5 rounded-full mb-3 bg-white/20" />
                    <h3 className="text-sm font-medium text-white/75 mb-1.5">{cap.title}</h3>
                    <p className="text-[11px] text-white/30 leading-relaxed">{cap.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* VISION — Looking ahead */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#0a0a0a] relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] rounded-full bg-white/[0.01] blur-[120px]" />
        </div>

        <div className="relative z-10 container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-white/[0.03] border border-white/[0.06] mb-6">
              <Leaf className="w-3.5 h-3.5 text-white/35" />
              <span className="text-[11px] text-white/35 uppercase tracking-wider">Our Vision</span>
            </div>

            <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight leading-[1.08] mb-6">
              A sustainable, intelligent future for fashion
            </h2>

            <p className="text-white/40 text-lg leading-relaxed mb-8 max-w-2xl mx-auto">
              We envision a fashion industry where every decision is informed by intelligent data,
              where sustainability isn&apos;t an afterthought but a foundation, and where professionals
              can focus on creativity while AI handles the research.
            </p>

            <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <Leaf className="w-4 h-4 text-white/40" />
              <span className="text-sm text-white/50 font-medium">Committed to net-zero by 2030</span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CTA */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight leading-[1.08] mb-5">
              Ready to transform<br />your workflow?
            </h2>
            <p className="text-white/40 text-lg mb-10">
              Join fashion professionals using McLeuker AI for smarter, faster research.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-white text-[#070707] font-medium text-sm hover:bg-white/90 transition-all"
              >
                Get Started Free
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/contact"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white/70 text-sm hover:bg-white/[0.08] transition-all"
              >
                Contact Us
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
