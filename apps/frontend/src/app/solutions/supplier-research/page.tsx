'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { Factory, ArrowRight, Check, Sparkles, MapPin, Shield, Scale, FileSpreadsheet, Globe } from "lucide-react";

const supplierData = [
  { name: "Candiani Denim", country: "Italy", moq: "300", cert: "GOTS", lead: "6 wks", tier: "A+" },
  { name: "Tejidos Royo", country: "Spain", moq: "500", cert: "OEKO", lead: "4 wks", tier: "A" },
  { name: "Advance Denim", country: "Portugal", moq: "200", cert: "BCI", lead: "5 wks", tier: "A+" },
  { name: "Orta Anadolu", country: "Turkey", moq: "1,000", cert: "GRS", lead: "3 wks", tier: "A" },
  { name: "Artistic Milliners", country: "Pakistan", moq: "500", cert: "WRAP", lead: "8 wks", tier: "B+" },
];

const capabilities = [
  { icon: MapPin, title: "Global Coverage", desc: "50+ countries, from European ateliers to Asian manufacturing hubs" },
  { icon: Shield, title: "Certification Tracking", desc: "GOTS, OEKO-TEX, BCI, GRS, WRAP, B Corp — all verified and current" },
  { icon: Scale, title: "MOQ & Pricing", desc: "Minimum order quantities, price ranges, and volume discount structures" },
  { icon: FileSpreadsheet, title: "Excel Export", desc: "Structured spreadsheets with filters, tier rankings, and contact details" },
  { icon: Globe, title: "Regional Insights", desc: "Lead times, trade regulations, and logistics by manufacturing region" },
  { icon: Sparkles, title: "AI Matching", desc: "Intelligent supplier recommendations based on your specific requirements" },
];

const workflow = [
  { step: "01", title: "Define", desc: "\"Find sustainable denim suppliers in Europe with MOQ under 500\"", detail: "Specify materials, certifications, regions, and requirements" },
  { step: "02", title: "Research", desc: "AI scans databases, trade directories, and industry sources", detail: "Cross-referencing certifications and capabilities" },
  { step: "03", title: "Compare", desc: "Structured comparison across MOQ, pricing, certifications, and lead times", detail: "Tier-ranked with sustainability scoring" },
  { step: "04", title: "Export", desc: "Ready-to-use Excel with contact details and outreach templates", detail: "Multi-sheet workbook with filters and formulas" },
];

export default function SupplierResearchPage() {
  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* Hero */}
      <section className="relative pt-20 lg:pt-28 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-500/[0.03] to-transparent" />
        <div className="absolute top-40 left-0 w-[500px] h-[500px] bg-blue-500/[0.02] rounded-full blur-[120px]" />
        
        <div className="container mx-auto px-6 lg:px-12 relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
                <Factory className="w-3.5 h-3.5 text-blue-400" />
                <span className="text-xs text-blue-400/80 uppercase tracking-[0.15em]">Supplier Research</span>
              </div>
              <h1 className="font-editorial text-4xl md:text-5xl lg:text-[3.5rem] text-white/[0.92] mb-5 leading-[1.1]">
                Find the right<br />partners, faster
              </h1>
              <p className="text-white/55 text-lg leading-relaxed mb-8 max-w-lg">
                AI-powered supplier discovery and due diligence. From certification verification to MOQ analysis — get structured data on manufacturing partners worldwide.
              </p>
              <div className="flex flex-wrap gap-4 mb-10">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
                  Try Supplier Research <ArrowRight className="w-4 h-4" />
                </Link>
                <Link href="/solutions" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full border border-white/[0.12] text-white/70 hover:bg-white/[0.04] transition-colors">
                  All Solutions
                </Link>
              </div>
              <div className="flex gap-8">
                {[
                  { value: "50+", label: "Countries" },
                  { value: "15+", label: "Certifications" },
                  { value: "Excel", label: "Export ready" },
                ].map((s, i) => (
                  <div key={i}>
                    <div className="text-2xl font-semibold text-white/[0.85]">{s.value}</div>
                    <div className="text-xs text-white/35">{s.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Excel preview mockup */}
            <div className="relative">
              <div className="rounded-2xl overflow-hidden bg-[#0C0C0C] border border-blue-500/10 shadow-2xl shadow-blue-500/5">
                <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] bg-[#0A0A0A]">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                  </div>
                  <span className="text-[10px] text-white/20 font-mono mx-auto">supplier_analysis.xlsx</span>
                </div>
                {/* Sheet tabs */}
                <div className="flex gap-0 border-b border-white/[0.06]">
                  {["Suppliers", "Pricing Matrix", "Certifications"].map((tab, i) => (
                    <div key={i} className={cn(
                      "px-4 py-2 text-[10px]",
                      i === 0 ? "bg-white/[0.04] text-white/60 border-b-2 border-blue-400/40" : "text-white/25"
                    )}>{tab}</div>
                  ))}
                </div>
                <div className="p-4 overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/[0.06]">
                        {["#", "Supplier", "Country", "MOQ", "Cert.", "Lead", "Tier"].map((h, i) => (
                          <th key={i} className="text-[9px] text-white/30 uppercase tracking-wider text-left pb-2 pr-3">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {supplierData.map((row, i) => (
                        <tr key={i} className="border-b border-white/[0.03]">
                          <td className="text-[10px] text-white/20 py-2 pr-3">{i + 1}</td>
                          <td className="text-[11px] text-white/60 py-2 pr-3">{row.name}</td>
                          <td className="text-[10px] text-white/40 py-2 pr-3">{row.country}</td>
                          <td className="text-[10px] text-white/40 py-2 pr-3">{row.moq}</td>
                          <td className="py-2 pr-3"><span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/15 text-blue-400/70">{row.cert}</span></td>
                          <td className="text-[10px] text-white/40 py-2 pr-3">{row.lead}</td>
                          <td className="py-2"><span className="text-[9px] px-1.5 py-0.5 rounded bg-green-500/15 text-green-400/70">{row.tier}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="text-[10px] text-white/15 mt-3">+ 27 more rows across 3 sheets</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Grid */}
      <section className="py-12 lg:py-16 border-y border-white/[0.04]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">What you get</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {capabilities.map((cap, i) => {
                const Icon = cap.icon;
                return (
                  <div key={i} className="group p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-blue-500/20 hover:bg-blue-500/[0.02] transition-all">
                    <Icon className="w-5 h-5 text-white/40 group-hover:text-blue-400/70 transition-colors mb-3" />
                    <h3 className="text-sm font-medium text-white/[0.8] mb-1.5">{cap.title}</h3>
                    <p className="text-xs text-white/40 leading-relaxed">{cap.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section className="py-12 lg:py-16">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">How it works</h2>
            <div className="space-y-0">
              {workflow.map((step, i) => (
                <div key={i} className="flex gap-6 relative">
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
                      <span className="text-xs font-mono text-blue-400/80">{step.step}</span>
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

      {/* Who it's for */}
      <section className="py-12 lg:py-16 border-t border-white/[0.04]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xs text-white/40 uppercase tracking-[0.2em] mb-8">Who it&apos;s for</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                "Sourcing Teams",
                "Procurement Managers",
                "Supply Chain Leaders",
                "Sustainability Officers",
                "Fashion Startups",
                "Independent Designers",
              ].map((role, i) => (
                <div key={i} className="flex items-center gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                  <Check className="w-4 h-4 text-blue-400/60 shrink-0" />
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
            Your next supplier list, in minutes
          </h2>
          <p className="text-white/50 text-lg mb-8 max-w-xl mx-auto">
            Stop spending weeks on manual supplier research. Get structured, exportable data now.
          </p>
          <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white text-black font-medium hover:bg-white/90 transition-colors">
            Try Supplier Research <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
