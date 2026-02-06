'use client';

import Link from "next/link";
import { WorkspaceNavigation } from "@/components/workspace/WorkspaceNavigation";
import { Globe, Sparkles, Leaf, Cpu, Heart, Droplets, ArrowRight, Shirt, Palette, Users, Factory } from "lucide-react";

const DOMAINS = [
  {
    id: "all",
    slug: "dashboard",
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
    slug: "fashion",
    name: "Fashion",
    icon: Shirt,
    description: "Runway analysis, trend forecasting, and market intelligence for apparel and accessories.",
    examples: [
      "Analyze SS26 womenswear trends from Milan Fashion Week",
      "What silhouettes are emerging for Resort 2026?",
      "Compare pricing strategies of European luxury houses"
    ]
  },
  {
    id: "beauty",
    slug: "beauty",
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
    slug: "skincare",
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
    slug: "sustainability",
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
    slug: "fashion-tech",
    name: "Fashion Tech",
    icon: Cpu,
    description: "Technology adoption, digital transformation, and innovation in fashion and retail.",
    examples: [
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
    description: "Live runway coverage, backstage energy, and designer analysis from global fashion weeks.",
    examples: [
      "Key moments from Paris Fashion Week",
      "Designer collections making headlines",
      "Runway styling trends this season"
    ]
  },
  {
    id: "culture",
    slug: "culture",
    name: "Culture",
    icon: Palette,
    description: "Art, exhibitions, and social signals shaping fashion narratives and brand positioning.",
    examples: [
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
    description: "Fibers, mills, material innovation, and sourcing intelligence for production.",
    examples: [
      "Find European mills with sustainable certifications",
      "Innovative materials in development",
      "Textile sourcing trends in Asia"
    ]
  },
  {
    id: "lifestyle",
    slug: "lifestyle",
    name: "Lifestyle",
    icon: Users,
    description: "Consumer culture, wellness, and lifestyle signals influencing fashion consumption.",
    examples: [
      "Wellness and fashion convergence",
      "Luxury consumer behavior shifts",
      "Travel and leisure influencing style"
    ]
  }
];

export default function DomainsPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <WorkspaceNavigation showSectorTabs={false} />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          {/* Hero */}
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h1 className="font-serif text-4xl md:text-5xl text-white mb-6">
              Intelligence Domains
            </h1>
            <p className="text-white/70 text-lg leading-relaxed">
              McLeuker AI organizes intelligence into specialized domains, each with curated data sources 
              and domain-specific analysis capabilities. Choose a domain to focus your research.
            </p>
          </div>

          {/* Domain Grid */}
          <div className="max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
            {DOMAINS.map((domain) => {
              const IconComponent = domain.icon;
              return (
                <Link
                  key={domain.id}
                  href={domain.id === "all" ? "/dashboard" : `/domain/${domain.slug}`}
                  className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-6 border border-white/[0.08] hover:border-white/[0.15] transition-colors group"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-white/[0.06] flex items-center justify-center group-hover:bg-white/[0.10] transition-colors">
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
                </Link>
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


    </div>
  );
}
