'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { Leaf, ArrowRight, Check, Sparkles, Shield, Recycle, FileCheck, Globe, BarChart3 } from "lucide-react";

const complianceData = [
  { label: "GOTS Compliance", value: 94 },
  { label: "Carbon Reduction", value: 67 },
  { label: "Circular Design", value: 45 },
  { label: "Fair Labor Score", value: 88 },
  { label: "Water Stewardship", value: 72 },
  { label: "Traceability Index", value: 61 },
];

const capabilities = [
  { icon: Shield, title: "Certification Tracking", desc: "GOTS, OEKO-TEX, B Corp, Cradle to Cradle, EU Ecolabel — all mapped and monitored" },
  { icon: FileCheck, title: "Regulatory Compliance", desc: "CSRD, EU Green Claims Directive, ESPR — stay ahead of evolving regulations" },
  { icon: BarChart3, title: "Impact Measurement", desc: "Carbon footprint, water usage, waste metrics with industry benchmarking" },
  { icon: Recycle, title: "Circular Models", desc: "Resale, rental, repair, and recycling program analysis and best practices" },
  { icon: Globe, title: "Supply Chain Mapping", desc: "Tier 1-4 visibility with risk assessment and improvement recommendations" },
  { icon: Sparkles, title: "Gap Analysis", desc: "AI-powered gap identification between current state and target certifications" },
];

const frameworks = [
  { name: "GOTS", full: "Global Organic Textile Standard", status: "Tracked" },
  { name: "OEKO-TEX", full: "Standard 100 & STeP", status: "Tracked" },
  { name: "B Corp", full: "B Corporation Certification", status: "Tracked" },
  { name: "CSRD", full: "Corporate Sustainability Reporting", status: "Monitored" },
  { name: "GRS", full: "Global Recycled Standard", status: "Tracked" },
  { name: "BCI", full: "Better Cotton Initiative", status: "Tracked" },
  { name: "ESPR", full: "Ecodesign for Sustainable Products", status: "Monitored" },
  { name: "SBTi", full: "Science Based Targets initiative", status: "Tracked" },
];

const workflow = [
  { step: "01", title: "Define Scope", desc: "\"Assess our brand's readiness for CSRD reporting and GOTS certification\"", detail: "Specify certifications, regulations, and sustainability goals" },
  { step: "02", title: "Audit", desc: "AI analyzes current practices against certification requirements and regulations", detail: "Cross-referencing 20+ frameworks and standards" },
  { step: "03", title: "Gap Analysis", desc: "Detailed gap identification with prioritized action items and timelines", detail: "Risk-weighted recommendations" },
  { step: "04", title: "Report", desc: "Stakeholder-ready sustainability report with metrics, benchmarks, and roadmap", detail: "PDF with executive summary and detailed appendices" },
];

export default function SustainabilityInsightsPage() {
  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* Hero — Monochromatic */}
      <section className="relative pt-20 lg:pt-28 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent" />
        <div className="absolute top-40 left-0 w-[500px] h-[500px] bg-white/[0.01] rounded-full blur-[120px]" />
        
        <div className="container mx-auto px-6 lg:px-12 relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] mb-6">
                <Leaf className="w-3.5 h-3.5 text-white/50" />
                <span className="text-xs text-white/50 uppercase tracking-[0.15em]">Sustainability Insights</span>
              </div>
              <h1 className="font-editorial text-4xl md:text-5xl lg:text-[3.5rem] text-white/[0.92] mb-5 leading-[1.1]">
                Responsible fashion,<br />measured
              </h1>
              <p className="text-white/55 text-lg leading-relaxed mb-8 max-w-lg">
                Navigate certifications, regulations, and impact metrics with AI-powered analysis. From GOTS compliance to CSRD readiness — get clarity on your sustainability journey.
              </p>
              <div className="flex flex-wrap gap-4 mb-10">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
                  Try Sustainability Insights <ArrowRight className="w-4 h-4" />
                </Link>
                <Link href="/solutions" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full border border-white/[0.12] text-white/70 hover:bg-white/[0.04] transition-colors">
                  All Solutions
                </Link>
              </div>
              <div className="flex gap-8">
                {[
                  { value: "20+", label: "Frameworks" },
                  { value: "100%", label: "Transparency" },
                  { value: "Gap", label: "Analysis incl." },
                ].map((s, i) => (
                  <div key={i}>
                    <div className="text-2xl font-semibold text-white/[0.85]">{s.value}</div>
                    <div className="text-xs text-white/35">{s.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Compliance dashboard mockup — Monochromatic */}
            <div className="relative">
              <div className="rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.08] shadow-2xl shadow-black/40">
                <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] bg-[#0A0A0A]">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                  </div>
                  <span className="text-[10px] text-white/20 font-mono mx-auto">sustainability_audit.pdf</span>
                </div>
                <div className="p-6">
                  <p className="text-[10px] text-white/30 uppercase tracking-wider mb-1">McLeuker AI Report</p>
                  <h3 className="text-lg font-medium text-white/80 mb-5">Compliance Dashboard</h3>
                  
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    {complianceData.map((item, i) => (
                      <div key={i} className="bg-white/[0.03] rounded-xl p-3 border border-white/[0.04]">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] text-white/40">{item.label}</span>
                          <span className="text-sm font-semibold text-white/70">{item.value}%</span>
                        </div>
                        <div className="h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full bg-white/25"
                            style={{ width: `${item.value}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-[10px] text-white/15">Benchmarked against 150+ brands</span>
                    <span className="text-[10px] text-white/30">Page 2 of 14</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Frameworks Tracked — Monochromatic */}
      <section className="py-8 border-y border-white/[0.04] overflow-hidden">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center gap-8 overflow-x-auto pb-2 scrollbar-hide">
              <span className="text-[10px] text-white/25 uppercase tracking-wider whitespace-nowrap shrink-0">Frameworks tracked</span>
              {frameworks.map((fw, i) => (
                <div key={i} className="flex items-center gap-2 shrink-0">
                  <span className="text-xs font-medium text-white/50">{fw.name}</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/[0.05] text-white/40">{fw.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Grid — Monochromatic */}
      <section className="py-12 lg:py-16">
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
      <section className="py-12 lg:py-16 border-t border-white/[0.04]">
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
                "Sustainability Officers",
                "CSR Managers",
                "Compliance Teams",
                "Supply Chain Leaders",
                "Brand Directors",
                "Impact Investors",
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
            Your sustainability roadmap, in minutes
          </h2>
          <p className="text-white/50 text-lg mb-8 max-w-xl mx-auto">
            Stop guessing about compliance. Get structured, actionable sustainability intelligence.
          </p>
          <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
            Try Sustainability Insights <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
