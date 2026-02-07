'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import {
  MessageSquare, Brain, Globe, Layers, Zap, ArrowRight, ArrowDown,
  Sparkles, FileText, BarChart3, Search, Check, Shield, Clock
} from "lucide-react";

const architectureLayers = [
  {
    id: 1,
    icon: MessageSquare,
    title: "Task Interpretation",
    subtitle: "Understanding your intent",
    description: "Your natural language query is parsed, classified by domain, and decomposed into structured research sub-tasks.",
    detail: "Domain classification, intent extraction, task decomposition",
    example: "\"Analyze SS26 womenswear trends from Milan\" → Domain: Fashion, Task: Trend Analysis, Scope: Milan FW SS26",
  },
  {
    id: 2,
    icon: Brain,
    title: "LLM Layer",
    subtitle: "Multi-model intelligence",
    description: "The best AI model is selected per sub-task — GPT-4 for synthesis, Grok for real-time data, Gemini for speed, Kimi for long documents.",
    detail: "GPT-4, Grok, Gemini Flash, Kimi — routed by task type",
    example: "Trend synthesis → GPT-4 | Live signals → Grok | Quick facts → Gemini Flash",
  },
  {
    id: 3,
    icon: Globe,
    title: "Real-Time Web Research",
    subtitle: "Live intelligence gathering",
    description: "AI agents search the web in real-time, pulling data from fashion weeks, trade publications, social media, and industry databases.",
    detail: "Perplexity, Grok Search, curated industry sources",
    example: "47 runway shows analyzed, 2,300 social posts scanned, 15 trade reports cross-referenced",
  },
  {
    id: 4,
    icon: Layers,
    title: "Logic & Structuring",
    subtitle: "Making sense of data",
    description: "Raw intelligence is validated, cross-referenced, and organized into structured formats — tables, charts, comparisons, and narratives.",
    detail: "Validation, deduplication, ranking, formatting",
    example: "Trend heatmap generated, supplier matrix built, competitive landscape mapped",
  },
  {
    id: 5,
    icon: Zap,
    title: "Execution Layer",
    subtitle: "Professional deliverables",
    description: "Final outputs are generated as professional documents — PDF reports, Excel spreadsheets, PowerPoint decks, and Word documents.",
    detail: "PDF, Excel, PPTX, DOCX — formatted and ready to share",
    example: "12-page PDF with executive summary, charts, and source citations",
  },
];

const differentiators = [
  { icon: Sparkles, title: "Multi-Model AI", desc: "Best model selected per task — not one-size-fits-all" },
  { icon: Globe, title: "Real-Time Data", desc: "Live web research, not stale training data" },
  { icon: BarChart3, title: "Structured Outputs", desc: "Tables, charts, and comparisons — not just text" },
  { icon: FileText, title: "Professional Exports", desc: "PDF, Excel, PPTX, Word — ready to share" },
  { icon: Shield, title: "Source Transparency", desc: "Every claim cited, every source traceable" },
  { icon: Clock, title: "Minutes, Not Weeks", desc: "Research that took days, delivered in minutes" },
];

const examplePrompts = [
  { domain: "Fashion", prompt: "Analyze SS26 womenswear trends from Milan and Paris Fashion Weeks", output: "12-page PDF trend report" },
  { domain: "Suppliers", prompt: "Find GOTS-certified denim suppliers in Europe with MOQ under 500", output: "Excel with 30+ suppliers" },
  { domain: "Market", prompt: "Size the European sustainable fashion market for DTC brands", output: "18-page market analysis" },
  { domain: "Sustainability", prompt: "Assess our brand's readiness for CSRD reporting", output: "Gap analysis with roadmap" },
];

export default function HowItWorksPage() {
  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* Hero */}
      <section className="relative pt-20 lg:pt-28 pb-12 lg:pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent" />
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-white/[0.01] rounded-full blur-[120px]" />
        
        <div className="container mx-auto px-6 lg:px-12 relative">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] mb-6">
              <Sparkles className="w-3.5 h-3.5 text-white/50" />
              <span className="text-xs text-white/50 uppercase tracking-[0.15em]">5-Layer Architecture</span>
            </div>
            <h1 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-5 leading-[1.1]">
              How McLeuker AI works
            </h1>
            <p className="text-white/55 text-lg lg:text-xl max-w-2xl mx-auto mb-6">
              A purpose-built agentic architecture that transforms natural language questions into structured, professional intelligence — in minutes.
            </p>
            <p className="text-white/35 text-sm max-w-xl mx-auto">
              Five specialized layers work in sequence: understanding your intent, selecting the best AI model, gathering live data, structuring findings, and generating professional deliverables.
            </p>
          </div>
        </div>
      </section>

      {/* Architecture Visualization — Monochromatic */}
      <section className="py-8 lg:py-12">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8 text-center">The 5-Layer Pipeline</h2>
            
            <div className="space-y-0">
              {architectureLayers.map((layer, i) => {
                const Icon = layer.icon;
                return (
                  <div key={layer.id}>
                    {/* Layer card */}
                    <div className="relative rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.06] hover:border-white/[0.12] transition-all duration-300 group">
                      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity bg-white/[0.01]" />
                      
                      <div className="relative p-6 lg:p-8">
                        <div className="flex flex-col lg:flex-row lg:items-start gap-6">
                          {/* Left: Icon + Number */}
                          <div className="flex items-center gap-4 lg:w-48 shrink-0">
                            <div className="w-12 h-12 rounded-xl flex items-center justify-center bg-white/[0.03] border border-white/[0.06]">
                              <Icon className="w-5 h-5 text-white/45" />
                            </div>
                            <div>
                              <span className="text-[10px] text-white/25 uppercase tracking-wider">Layer {layer.id}</span>
                              <h3 className="text-lg font-medium text-white/[0.85]">{layer.title}</h3>
                            </div>
                          </div>

                          {/* Right: Content */}
                          <div className="flex-1 space-y-3">
                            <p className="text-xs uppercase tracking-wider text-white/40">{layer.subtitle}</p>
                            <p className="text-white/55 leading-relaxed">{layer.description}</p>
                            
                            {/* Technical detail */}
                            <div className="flex items-start gap-2 pt-1">
                              <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 bg-white/25" />
                              <span className="text-xs text-white/35">{layer.detail}</span>
                            </div>

                            {/* Example */}
                            <div className="bg-white/[0.02] rounded-lg p-3 border border-white/[0.04]">
                              <span className="text-[10px] text-white/25 uppercase tracking-wider">Example</span>
                              <p className="text-xs text-white/45 mt-1 font-mono">{layer.example}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Connector arrow */}
                    {i < architectureLayers.length - 1 && (
                      <div className="flex justify-center py-2">
                        <div className="flex flex-col items-center">
                          <div className="w-px h-4 bg-white/[0.08]" />
                          <ArrowDown className="w-4 h-4 text-white/15" />
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* What makes it different */}
      <section className="py-12 lg:py-16 border-y border-white/[0.04]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">What makes it different</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {differentiators.map((item, i) => {
                const Icon = item.icon;
                return (
                  <div key={i} className="group p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-white/[0.12] transition-all">
                    <Icon className="w-5 h-5 text-white/40 group-hover:text-white/60 transition-colors mb-3" />
                    <h3 className="text-sm font-medium text-white/[0.8] mb-1.5">{item.title}</h3>
                    <p className="text-xs text-white/40 leading-relaxed">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Example Prompts → Outputs */}
      <section className="py-12 lg:py-16">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">From question to deliverable</h2>
            <div className="space-y-3">
              {examplePrompts.map((item, i) => (
                <div key={i} className="group flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-white/[0.1] transition-all">
                  <span className="text-[10px] text-white/25 uppercase tracking-wider shrink-0 w-20">{item.domain}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white/60 truncate">&ldquo;{item.prompt}&rdquo;</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <ArrowRight className="w-3 h-3 text-white/20" />
                    <span className="text-xs text-white/40 bg-white/[0.04] px-3 py-1 rounded-full">{item.output}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Methodology */}
      <section className="py-12 lg:py-16 border-t border-white/[0.04]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">Our methodology</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                <h3 className="text-sm font-medium text-white/[0.8] mb-3">Domain-Specific Intelligence</h3>
                <p className="text-xs text-white/45 leading-relaxed">
                  McLeuker AI combines large language models with curated fashion industry data sources. Our systems understand domain-specific terminology, frameworks, and context — from Pantone references to certification standards.
                </p>
              </div>
              <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                <h3 className="text-sm font-medium text-white/[0.8] mb-3">Continuous Validation</h3>
                <p className="text-xs text-white/45 leading-relaxed">
                  Every output is validated against primary sources and industry benchmarks. When data is uncertain or unavailable, we clearly indicate limitations. Source citations are included in every report.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 lg:py-24">
        <div className="container mx-auto px-6 lg:px-12 text-center">
          <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.92] mb-4">
            See it in action
          </h2>
          <p className="text-white/50 text-lg mb-8 max-w-xl mx-auto">
            Try your first research query. No setup required.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
              Start Research <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/solutions" className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full border border-white/[0.15] text-white/80 hover:bg-white/[0.06] transition-colors">
              View Solutions
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
