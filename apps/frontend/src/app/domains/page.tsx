'use client';

import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { Globe, Sparkles, Leaf, Cpu, Heart, Droplets, ArrowRight } from "lucide-react";

const DOMAINS = [
  {
    id: "global",
    name: "Global",
    icon: Globe,
    description: "Cross-industry intelligence spanning fashion, beauty, sustainability, and emerging technologies.",
    examples: [
      "What are the top consumer trends for 2026?",
      "Compare sustainability strategies across luxury brands",
      "Analyze the impact of AI on retail operations"
    ]
  },
  {
    id: "fashion",
    name: "Fashion",
    icon: Sparkles,
    description: "Runway analysis, trend forecasting, and market intelligence for apparel and accessories.",
    examples: [
      "Analyze SS26 womenswear trends from Milan Fashion Week",
      "What silhouettes are emerging for Resort 2026?",
      "Compare pricing strategies of European luxury houses"
    ]
  },
  {
    id: "beauty",
    name: "Beauty",
    icon: Heart,
    description: "Cosmetics, skincare, and fragrance market intelligence with ingredient and regulatory insights.",
    examples: [
      "What are the trending active ingredients in K-beauty?",
      "Analyze clean beauty market growth in North America",
      "Compare Gen Z vs Millennial beauty purchasing patterns"
    ]
  },
  {
    id: "skincare",
    name: "Skincare",
    icon: Droplets,
    description: "Deep-dive analysis on skincare formulations, efficacy claims, and consumer preferences.",
    examples: [
      "What peptides are trending in anti-aging products?",
      "Analyze the barrier repair category growth",
      "Compare retinol alternatives in clean skincare"
    ]
  },
  {
    id: "sustainability",
    name: "Sustainability",
    icon: Leaf,
    description: "Environmental impact, certifications, circular economy, and regulatory compliance intelligence.",
    examples: [
      "Map sustainability certifications for European brands",
      "What are the leading circular fashion initiatives?",
      "Analyze EPR regulations across EU markets"
    ]
  },
  {
    id: "fashion-tech",
    name: "Fashion Tech",
    icon: Cpu,
    description: "Technology adoption, digital transformation, and innovation in fashion and retail.",
    examples: [
      "Research AI adoption in fashion supply chains",
      "What 3D design tools are brands adopting?",
      "Analyze virtual try-on technology providers"
    ]
  }
];

export default function DomainsPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          {/* Hero */}
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Intelligence Domains
            </h1>
            <p className="text-white/70 text-lg leading-relaxed">
              McLeuker AI organizes intelligence into specialized domains, each with curated data sources 
              and domain-specific analysis capabilities. Choose a domain to focus your research.
            </p>
          </div>

          {/* Domain Grid */}
          <div className="max-w-5xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
            {DOMAINS.map((domain) => {
              const IconComponent = domain.icon;
              return (
                <div
                  key={domain.id}
                  className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-6 border border-white/[0.08] hover:border-white/[0.15] transition-colors"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-white/[0.06] flex items-center justify-center">
                      <IconComponent className="h-5 w-5 text-white/80" />
                    </div>
                    <h3 className="text-lg font-medium text-white">{domain.name}</h3>
                  </div>
                  <p className="text-white/60 text-sm leading-relaxed mb-4">
                    {domain.description}
                  </p>
                  <div className="space-y-2">
                    <p className="text-white/40 text-xs uppercase tracking-wider">Example queries</p>
                    {domain.examples.map((example, i) => (
                      <p key={i} className="text-white/50 text-sm">
                        &ldquo;{example}&rdquo;
                      </p>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* CTA */}
          <div className="text-center">
            <Link 
              href="/dashboard"
              className="inline-flex items-center bg-white text-black hover:bg-white/90 px-8 py-4 rounded-lg text-base font-medium transition-colors"
            >
              Try the Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
