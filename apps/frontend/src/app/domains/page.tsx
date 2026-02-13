'use client';

import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import {
  Globe, Sparkles, Leaf, Cpu, Heart, Droplets, ArrowRight,
  Shirt, Palette, Users, Factory, Search, Brain, Zap, FileText,
  Layers
} from "lucide-react";

const DOMAINS = [
  {
    id: "fashion",
    slug: "fashion",
    name: "Fashion",
    icon: Shirt,
    image: "/images/domains/fashion.jpg",
    tagline: "Runway to Retail",
    description: "Runway analysis, trend forecasting, silhouette tracking, and market intelligence for apparel and accessories.",
    stats: { sources: "2,400+", reports: "180+", signals: "Real-time" },
    queries: [
      "Analyze SS26 womenswear trends from Milan Fashion Week",
      "Compare pricing strategies of European luxury houses",
      "What silhouettes are emerging for Resort 2026?"
    ]
  },
  {
    id: "beauty",
    slug: "beauty",
    name: "Beauty",
    icon: Heart,
    image: "/images/domains/beauty.jpg",
    tagline: "Formulas & Futures",
    description: "Cosmetics, fragrance market intelligence with ingredient analysis, brand strategy, and regulatory insights.",
    stats: { sources: "1,800+", reports: "120+", signals: "Real-time" },
    queries: [
      "What are the trending active ingredients in K-beauty?",
      "Analyze clean beauty market growth in North America",
      "Compare Gen Z vs Millennial beauty purchasing patterns"
    ]
  },
  {
    id: "skincare",
    slug: "skincare",
    name: "Skincare",
    icon: Droplets,
    image: "/images/domains/skincare.jpg",
    tagline: "Science Meets Skin",
    description: "Deep-dive analysis on skincare formulations, efficacy claims, clinical data, and consumer preferences.",
    stats: { sources: "1,200+", reports: "90+", signals: "Real-time" },
    queries: [
      "What peptides are trending in anti-aging products?",
      "Analyze the barrier repair category growth",
      "Compare retinol alternatives in clean skincare"
    ]
  },
  {
    id: "sustainability",
    slug: "sustainability",
    name: "Sustainability",
    icon: Leaf,
    image: "/images/domains/sustainability.jpg",
    tagline: "Impact & Integrity",
    description: "Environmental impact, certifications, circular economy models, and regulatory compliance intelligence.",
    stats: { sources: "900+", reports: "75+", signals: "Real-time" },
    queries: [
      "Map sustainability certifications for European brands",
      "What are the leading circular fashion initiatives?",
      "Analyze EPR regulations across EU markets"
    ]
  },
  {
    id: "fashion-tech",
    slug: "fashion-tech",
    name: "Fashion Tech",
    icon: Cpu,
    image: "/images/domains/fashion-tech.jpg",
    tagline: "Digital Innovation",
    description: "Technology adoption, digital transformation, AI tools, and innovation reshaping fashion and retail.",
    stats: { sources: "800+", reports: "60+", signals: "Real-time" },
    queries: [
      "Research AI adoption in fashion supply chains",
      "What 3D design tools are brands adopting?",
      "Analyze virtual try-on technology providers"
    ]
  },
  {
    id: "catwalks",
    slug: "catwalks",
    name: "Catwalks",
    icon: Sparkles,
    image: "/images/domains/catwalks.jpg",
    tagline: "Front Row Access",
    description: "Live runway coverage, backstage energy, designer analysis, and collection breakdowns from global fashion weeks.",
    stats: { sources: "600+", reports: "50+", signals: "Real-time" },
    queries: [
      "Key moments from Paris Fashion Week SS26",
      "Designer collections making headlines this season",
      "Runway styling trends and emerging designers"
    ]
  },
  {
    id: "culture",
    slug: "culture",
    name: "Culture",
    icon: Palette,
    image: "/images/domains/culture.jpg",
    tagline: "Art Meets Fashion",
    description: "Art, exhibitions, music, and social signals shaping fashion narratives and brand positioning.",
    stats: { sources: "700+", reports: "45+", signals: "Real-time" },
    queries: [
      "Cultural shifts influencing luxury positioning",
      "Art collaborations in fashion this year",
      "Social movements shaping brand narratives"
    ]
  },
  {
    id: "textile",
    slug: "textile",
    name: "Textile",
    icon: Factory,
    image: "/images/domains/textile.jpg",
    tagline: "Material Intelligence",
    description: "Fibers, mills, material innovation, sourcing intelligence, and production capabilities worldwide.",
    stats: { sources: "500+", reports: "40+", signals: "Real-time" },
    queries: [
      "Find European mills with sustainable certifications",
      "Innovative materials in development for 2026",
      "Textile sourcing trends across Asia-Pacific"
    ]
  },
  {
    id: "lifestyle",
    slug: "lifestyle",
    name: "Lifestyle",
    icon: Users,
    image: "/images/domains/lifestyle.jpg",
    tagline: "Culture & Commerce",
    description: "Consumer culture, wellness, travel, and lifestyle signals influencing fashion consumption patterns.",
    stats: { sources: "600+", reports: "35+", signals: "Real-time" },
    queries: [
      "Wellness and fashion convergence trends",
      "Luxury consumer behavior shifts post-2025",
      "Travel and leisure influencing global style"
    ]
  }
];

export default function DomainsPage() {
  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* ═══════════════════════════════════════════════════════ */}
      {/* HERO — Monochromatic */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative py-24 lg:py-32 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute inset-0 grid grid-cols-3 md:grid-cols-5 gap-1 opacity-[0.04]">
            {DOMAINS.map((d, i) => (
              <div key={i} className="relative aspect-square overflow-hidden">
                <Image src={d.image} alt="" fill className="object-cover grayscale" />
              </div>
            ))}
          </div>
          <div className="absolute inset-0 bg-gradient-to-b from-[#070707] via-[#070707]/80 to-[#070707]" />
        </div>

        <div className="relative z-10 container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06] mb-8">
              <Globe className="w-3.5 h-3.5 text-white/30" />
              <span className="text-[11px] text-white/40 uppercase tracking-[0.15em]">Specialized Intelligence</span>
            </div>

            <h1 className="font-editorial text-5xl md:text-6xl lg:text-7xl text-white/[0.95] tracking-tight leading-[1.05] mb-6">
              10 Domains.<br />
              <span className="text-white/50">One Intelligence.</span>
            </h1>

            <p className="text-white/40 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-10">
              Each domain is powered by curated data sources, specialized AI models, and industry-specific analysis frameworks. Choose your world.
            </p>

            {/* Domain pills — monochromatic */}
            <div className="flex flex-wrap justify-center gap-2 mb-8">
              {DOMAINS.map((d) => (
                <a
                  key={d.id}
                  href={`#${d.id}`}
                  className="group flex items-center gap-2 px-4 py-2 rounded-full border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/[0.12] transition-all duration-300 hover:scale-105"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-white/30 group-hover:bg-white/60 transition-colors" />
                  <span className="text-sm text-white/40 group-hover:text-white/70 transition-colors">{d.name}</span>
                </a>
              ))}
            </div>

            {/* Live counter */}
            <div className="flex items-center justify-center gap-6 text-center">
              {[
                { value: "10K+", label: "Data Sources" },
                { value: "9", label: "Domains" },
                { value: "24/7", label: "Live Signals" },
              ].map((s, i) => (
                <div key={i} className="px-4">
                  <div className="text-2xl font-light text-white/70">{s.value}</div>
                  <div className="text-[10px] text-white/25 uppercase tracking-wider mt-0.5">{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* DOMAIN CARDS — Monochromatic, B&W images */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative pb-16 lg:pb-24">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto space-y-6">
            {DOMAINS.map((domain, index) => {
              const Icon = domain.icon;
              const isEven = index % 2 === 0;
              return (
                <div
                  key={domain.id}
                  id={domain.id}
                  className="group relative rounded-2xl overflow-hidden border border-white/[0.04] hover:border-white/[0.10] transition-all duration-500 bg-[#0a0a0a]"
                >
                  <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-white/[0.08] via-white/[0.03] to-transparent" />

                  <div className={cn(
                    "grid lg:grid-cols-5 gap-0",
                    !isEven && "lg:direction-rtl"
                  )}>
                    {/* Image column — B&W */}
                    <div className={cn(
                      "relative lg:col-span-2 aspect-[16/10] lg:aspect-auto overflow-hidden",
                      !isEven && "lg:order-2"
                    )}>
                      <Image
                        src={domain.image}
                        alt={domain.name}
                        fill
                        className="object-cover grayscale brightness-[0.4] group-hover:brightness-[0.5] transition-all duration-700 group-hover:scale-105"
                      />
                      <div className={cn(
                        "absolute inset-0",
                        isEven
                          ? "bg-gradient-to-r from-transparent via-transparent to-[#0a0a0a]"
                          : "bg-gradient-to-l from-transparent via-transparent to-[#0a0a0a]"
                      )} />
                      <div className="absolute bottom-4 left-4 lg:bottom-6 lg:left-6">
                        <span className="text-6xl lg:text-7xl font-editorial text-white/[0.06]">
                          {String(index + 1).padStart(2, '0')}
                        </span>
                      </div>
                    </div>

                    {/* Content column — monochromatic */}
                    <div className={cn(
                      "lg:col-span-3 p-6 lg:p-10 flex flex-col justify-center",
                      !isEven && "lg:order-1"
                    )}>
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl flex items-center justify-center border bg-white/[0.03] border-white/[0.08]">
                          <Icon className="w-5 h-5 text-white/40" />
                        </div>
                        <div>
                          <span className="text-[10px] uppercase tracking-wider text-white/30">{domain.tagline}</span>
                          <h3 className="text-2xl font-editorial text-white/90">{domain.name}</h3>
                        </div>
                      </div>

                      <p className="text-white/40 text-sm leading-relaxed mb-5 max-w-lg">
                        {domain.description}
                      </p>

                      {/* Stats row — monochromatic */}
                      <div className="flex gap-4 mb-5">
                        {[
                          { label: "Sources", value: domain.stats.sources },
                          { label: "Reports", value: domain.stats.reports },
                          { label: "Signals", value: domain.stats.signals },
                        ].map((s, i) => (
                          <div key={i} className="px-3 py-2 rounded-lg border border-white/[0.06] bg-white/[0.02]">
                            <div className="text-sm font-medium text-white/60">{s.value}</div>
                            <div className="text-[9px] text-white/25 uppercase tracking-wider">{s.label}</div>
                          </div>
                        ))}
                      </div>

                      {/* Example queries */}
                      <div className="space-y-1.5 mb-6">
                        <span className="text-[9px] text-white/25 uppercase tracking-wider">Example Queries</span>
                        {domain.queries.map((q, i) => (
                          <div key={i} className="flex items-start gap-2">
                            <Search className="w-3 h-3 text-white/15 mt-1 flex-shrink-0" />
                            <span className="text-[12px] text-white/35 leading-relaxed">&ldquo;{q}&rdquo;</span>
                          </div>
                        ))}
                      </div>

                      {/* CTA — monochromatic */}
                      <Link
                        href={`/domain/${domain.slug}`}
                        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all w-fit group/btn bg-white/[0.05] border border-white/[0.10] text-white/60 hover:bg-white/[0.08] hover:text-white/80 hover:border-white/[0.15]"
                      >
                        Explore {domain.name}
                        <ArrowRight className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* HOW DOMAINS WORK — Monochromatic pipeline */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="text-center mb-14">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="h-px w-12 bg-gradient-to-r from-transparent to-white/[0.10]" />
                <span className="text-[11px] text-white/30 uppercase tracking-[0.2em] font-medium">How It Works</span>
                <div className="h-px w-12 bg-gradient-to-l from-transparent to-white/[0.10]" />
              </div>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight">
                Domain-Specific Intelligence
              </h2>
              <p className="text-white/40 text-base max-w-xl mx-auto mt-4 leading-relaxed">
                Each domain has its own curated pipeline — from specialized data sources to tailored analysis frameworks.
              </p>
            </div>

            <div className="grid md:grid-cols-4 gap-4">
              {[
                { icon: Search, title: "Curated Sources", desc: "Each domain pulls from vetted, industry-specific data sources — trade publications, runway feeds, regulatory databases." },
                { icon: Brain, title: "Domain Models", desc: "AI models fine-tuned for each domain's vocabulary, context, and analytical requirements." },
                { icon: Layers, title: "Structured Analysis", desc: "Domain-specific frameworks transform raw data into comparisons, matrices, and actionable insights." },
                { icon: FileText, title: "Professional Output", desc: "Reports formatted for each domain's stakeholders — from buyer decks to sustainability audits." },
              ].map((step, i) => {
                const StepIcon = step.icon;
                return (
                  <div key={i} className="relative group">
                    {i < 3 && (
                      <div className="hidden md:block absolute top-12 right-0 translate-x-1/2 w-8 h-px bg-white/[0.06] z-10" />
                    )}
                    <div className="p-6 rounded-2xl bg-[#0d0d0d] border border-white/[0.04] hover:border-white/[0.10] transition-all h-full">
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4 border bg-white/[0.03] border-white/[0.08]">
                        <StepIcon className="w-5 h-5 text-white/40" />
                      </div>
                      <div className="text-[10px] font-mono text-white/20 mb-2">0{i + 1}</div>
                      <h3 className="text-base font-medium text-white/85 mb-2">{step.title}</h3>
                      <p className="text-sm text-white/35 leading-relaxed">{step.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CROSS-DOMAIN — Monochromatic */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-white/[0.03] border border-white/[0.06] mb-5">
                  <Globe className="w-3.5 h-3.5 text-white/30" />
                  <span className="text-[11px] text-white/35 uppercase tracking-wider">Cross-Domain</span>
                </div>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight leading-[1.08] mb-5">
                  Or research<br />across all domains
                </h2>
                <p className="text-white/40 text-base leading-relaxed mb-6 max-w-lg">
                  Don&apos;t limit yourself to one domain. Our Global mode combines intelligence from all 9 specialized domains for cross-industry analysis.
                </p>
                <div className="space-y-3 mb-8">
                  {[
                    "How is sustainability impacting luxury fashion pricing?",
                    "Compare AI adoption across beauty, fashion, and textile sectors",
                    "What cultural trends are driving Gen Z purchasing in 2026?"
                  ].map((q, i) => (
                    <div key={i} className="flex items-start gap-2 px-4 py-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04]">
                      <Search className="w-3.5 h-3.5 text-white/20 mt-0.5 flex-shrink-0" />
                      <span className="text-[12px] text-white/40">{q}</span>
                    </div>
                  ))}
                </div>
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-2 px-7 py-3 rounded-xl bg-white/[0.08] border border-white/[0.12] text-white/80 font-medium text-sm hover:bg-white/[0.12] hover:border-white/[0.18] transition-all"
                >
                  Try Global Research
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>

              {/* Visual: Domain constellation — monochromatic */}
              <div className="relative h-[400px] lg:h-[500px]">
                <div className="absolute inset-0 flex items-center justify-center">
                  {/* Center hub */}
                  <div className="absolute w-20 h-20 rounded-full bg-white/[0.03] border border-white/[0.08] flex items-center justify-center z-10">
                    <Brain className="w-8 h-8 text-white/30" />
                  </div>
                  {/* Orbiting domains — monochromatic */}
                  {DOMAINS.map((d, i) => {
                    const angle = (i / DOMAINS.length) * 2 * Math.PI - Math.PI / 2;
                    const radius = 160;
                    const x = Math.cos(angle) * radius;
                    const y = Math.sin(angle) * radius;
                    const DIcon = d.icon;
                    return (
                      <div
                        key={d.id}
                        className="absolute flex flex-col items-center gap-1 group/orb"
                        style={{ transform: `translate(${x}px, ${y}px)` }}
                      >
                        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ overflow: 'visible' }}>
                          <line x1="50%" y1="50%" x2={-x} y2={-y} stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
                        </svg>
                        <div className="relative z-10 w-11 h-11 rounded-xl flex items-center justify-center border transition-all group-hover/orb:scale-110 bg-white/[0.03] border-white/[0.08] group-hover/orb:bg-white/[0.06] group-hover/orb:border-white/[0.15]">
                          <DIcon className="w-5 h-5 text-white/35 group-hover/orb:text-white/60 transition-colors" />
                        </div>
                        <span className="text-[9px] text-white/25 group-hover/orb:text-white/50 transition-colors">{d.name}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CTA — Monochromatic */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#0a0a0a]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.95] tracking-tight leading-[1.08] mb-5">
              Start exploring your domain
            </h2>
            <p className="text-white/40 text-lg mb-10">
              Choose a domain and get your first research report in under 5 minutes.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-white/[0.08] border border-white/[0.12] text-white/90 font-medium text-sm hover:bg-white/[0.12] hover:border-white/[0.18] transition-all"
              >
                Get Started Free
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white/70 text-sm hover:bg-white/[0.08] transition-all"
              >
                Try the Dashboard
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
