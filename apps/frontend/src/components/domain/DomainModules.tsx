"use client";

import { Sector } from "@/contexts/SectorContext";
import { cn } from "@/lib/utils";
import {
  Search,
  TrendingUp,
  Building2,
  FileSpreadsheet,
  Globe,
  Leaf,
  Cpu,
  Palette,
  Users,
  Microscope,
  Shirt,
  Factory,
  Sparkles,
} from "lucide-react";

interface Module {
  id: string;
  label: string;
  description: string;
  prompt: string;
  icon: React.ElementType;
  outputHint?: string;
}

// Domain-specific intelligence modules
const domainModules: Record<Sector, Module[]> = {
  all: [
    {
      id: "trends",
      label: "Cross-Domain Trends",
      description: "Signals across fashion, beauty & lifestyle",
      prompt: "What are the top cross-domain trends emerging in fashion and lifestyle this week?",
      icon: TrendingUp,
    },
    {
      id: "market",
      label: "Market Intelligence",
      description: "Brand positioning & competitive signals",
      prompt: "Give me a market intelligence overview of key luxury brand movements this month.",
      icon: Globe,
    },
  ],
  fashion: [
    {
      id: "runway",
      label: "Runway Analysis",
      description: "Silhouettes, colors & designer signals",
      prompt: "Analyze the key silhouette and color trends from recent fashion weeks.",
      icon: Shirt,
    },
    {
      id: "brands",
      label: "Brand Positioning",
      description: "Luxury brand strategy & movements",
      prompt: "Research current brand positioning shifts among top luxury fashion houses.",
      icon: Building2,
    },
    {
      id: "street",
      label: "Street Style",
      description: "Consumer adoption signals",
      prompt: "What street style trends are gaining momentum in major fashion capitals?",
      icon: Users,
    },
    {
      id: "emerging",
      label: "Emerging Designers",
      description: "New talent to watch",
      prompt: "Who are the emerging designers gaining industry attention this season?",
      icon: Sparkles,
    },
  ],
  textile: [
    {
      id: "mills",
      label: "Find Mills",
      description: "European & Asian textile producers",
      prompt: "Find textile mills in Europe with sustainable certifications and low MOQ options.",
      icon: Factory,
      outputHint: "Excel",
    },
    {
      id: "fibers",
      label: "Fiber Innovation",
      description: "New materials & technologies",
      prompt: "What are the latest fiber innovations gaining adoption in sustainable fashion?",
      icon: Microscope,
    },
    {
      id: "suppliers",
      label: "Supplier Discovery",
      description: "Sourcing with specifications",
      prompt: "Create a supplier comparison for organic cotton producers with pricing and MOQ details.",
      icon: FileSpreadsheet,
      outputHint: "Excel",
    },
    {
      id: "certification",
      label: "Certification Guide",
      description: "GOTS, OEKO-TEX, BCI & more",
      prompt: "Compare textile certifications (GOTS, OEKO-TEX, BCI) with requirements and costs.",
      icon: Leaf,
    },
  ],
  lifestyle: [
    {
      id: "consumer",
      label: "Consumer Signals",
      description: "Behavior shifts & preferences",
      prompt: "What consumer behavior shifts are influencing luxury lifestyle purchases?",
      icon: Users,
    },
    {
      id: "wellness",
      label: "Wellness Trends",
      description: "Health & fashion convergence",
      prompt: "How are wellness trends influencing fashion and lifestyle brand positioning?",
      icon: Sparkles,
    },
    {
      id: "culture",
      label: "Cultural Shifts",
      description: "Social movements & values",
      prompt: "What cultural shifts are shaping luxury consumer values this year?",
      icon: Globe,
    },
    {
      id: "travel",
      label: "Travel & Leisure",
      description: "Destination & experience signals",
      prompt: "How is travel influencing fashion and lifestyle consumption patterns?",
      icon: TrendingUp,
    },
  ],
  beauty: [
    {
      id: "ingredients",
      label: "Ingredient Trends",
      description: "Active ingredients gaining traction",
      prompt: "What beauty ingredients are trending in prestige skincare and makeup?",
      icon: Microscope,
    },
    {
      id: "brands",
      label: "Brand Analysis",
      description: "Market positioning & launches",
      prompt: "Analyze recent beauty brand launches and market positioning strategies.",
      icon: Building2,
    },
    {
      id: "clean",
      label: "Clean Beauty",
      description: "Sustainability in cosmetics",
      prompt: "What clean beauty trends are gaining consumer adoption in North America and Europe?",
      icon: Leaf,
    },
    {
      id: "backstage",
      label: "Backstage Beauty",
      description: "Runway makeup trends",
      prompt: "What makeup trends dominated backstage at recent fashion weeks?",
      icon: Palette,
    },
  ],
  skincare: [
    {
      id: "actives",
      label: "Active Ingredients",
      description: "Science-backed formulations",
      prompt: "What active ingredients are leading in clinical skincare innovation?",
      icon: Microscope,
    },
    {
      id: "regulation",
      label: "Regulatory Updates",
      description: "EU, US & Asian compliance",
      prompt: "What skincare regulatory changes should brands monitor in EU and US markets?",
      icon: FileSpreadsheet,
    },
    {
      id: "claims",
      label: "Claims Analysis",
      description: "Marketing & efficacy claims",
      prompt: "Analyze trending skincare claims and their scientific backing.",
      icon: Search,
    },
    {
      id: "innovation",
      label: "Product Innovation",
      description: "New formats & technologies",
      prompt: "What skincare product innovations are gaining market attention?",
      icon: Sparkles,
    },
  ],
  sustainability: [
    {
      id: "materials",
      label: "Sustainable Materials",
      description: "Circular & regenerative options",
      prompt: "What sustainable materials are gaining adoption in fashion production?",
      icon: Leaf,
    },
    {
      id: "supply",
      label: "Supply Chain",
      description: "Transparency & traceability",
      prompt: "Research supply chain transparency best practices in sustainable fashion.",
      icon: Factory,
    },
    {
      id: "regulations",
      label: "ESG Regulations",
      description: "Compliance & reporting",
      prompt: "What ESG regulations should fashion brands prepare for in 2025-2026?",
      icon: FileSpreadsheet,
      outputHint: "PDF",
    },
    {
      id: "certifications",
      label: "Certifications",
      description: "Standards & verification",
      prompt: "Compare sustainability certifications relevant to fashion and textile brands.",
      icon: Building2,
    },
  ],
  "fashion-tech": [
    {
      id: "ai",
      label: "AI in Fashion",
      description: "Machine learning applications",
      prompt: "How is AI being adopted across the fashion value chain?",
      icon: Cpu,
    },
    {
      id: "startups",
      label: "Startup Landscape",
      description: "Emerging tech companies",
      prompt: "Create a landscape of fashion tech startups to watch in 2025.",
      icon: Building2,
      outputHint: "Excel",
    },
    {
      id: "digital",
      label: "Digital Fashion",
      description: "Virtual & augmented experiences",
      prompt: "What digital fashion innovations are gaining consumer adoption?",
      icon: Globe,
    },
    {
      id: "retail",
      label: "Retail Tech",
      description: "Store & e-commerce innovation",
      prompt: "What retail technologies are transforming the fashion shopping experience?",
      icon: TrendingUp,
    },
  ],
  catwalks: [
    {
      id: "shows",
      label: "Show Summaries",
      description: "Key collections & moments",
      prompt: "Summarize the standout collections from the latest fashion week season.",
      icon: Shirt,
    },
    {
      id: "designers",
      label: "Designer Analysis",
      description: "Creative direction & vision",
      prompt: "Analyze the creative direction of top designers this season.",
      icon: Palette,
    },
    {
      id: "styling",
      label: "Styling Trends",
      description: "Show styling & presentation",
      prompt: "What styling trends defined recent runway presentations?",
      icon: Sparkles,
    },
    {
      id: "emerging",
      label: "Emerging Talent",
      description: "New designers to watch",
      prompt: "Who are the breakout designers from recent fashion weeks?",
      icon: Users,
    },
  ],
  culture: [
    {
      id: "art",
      label: "Art & Fashion",
      description: "Collaborations & exhibitions",
      prompt: "What art-fashion collaborations are shaping brand narratives?",
      icon: Palette,
    },
    {
      id: "social",
      label: "Social Signals",
      description: "Movements & values",
      prompt: "What social movements are influencing fashion brand positioning?",
      icon: Users,
    },
    {
      id: "regional",
      label: "Regional Culture",
      description: "Geographic influences",
      prompt: "How are regional cultural signals influencing global fashion trends?",
      icon: Globe,
    },
    {
      id: "media",
      label: "Media & Influence",
      description: "Cultural narratives",
      prompt: "What media and cultural narratives are shaping fashion consumption?",
      icon: TrendingUp,
    },
  ],
};

interface DomainModulesProps {
  sector: Sector;
  onModuleClick: (prompt: string) => void;
}

export function DomainModules({ sector, onModuleClick }: DomainModulesProps) {
  const modules = domainModules[sector] || domainModules.all;

  return (
    <div className="bg-[#0A0A0A]">
      <section className="max-w-[1120px] mx-auto px-7 py-10 md:py-12">
        <h2 className="font-serif text-2xl md:text-3xl text-white/[0.92] mb-10">
          Intelligence Modules
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <button
                key={module.id}
                onClick={() => onModuleClick(module.prompt)}
                className={cn(
                  "group text-left p-5 rounded-[18px]",
                  "bg-gradient-to-b from-[#1A1A1A] to-[#141414]",
                  "border border-white/[0.10]",
                  "transition-all duration-200",
                  "hover:from-[#202020] hover:to-[#181818]",
                  "hover:border-white/[0.18]"
                )}
              >
                <div className="flex items-start justify-between mb-4">
                  <Icon className="h-5 w-5 text-white/50 group-hover:text-white transition-colors" />
                  {module.outputHint && (
                    <span className="text-[11px] uppercase tracking-widest text-white/60">
                      {module.outputHint}
                    </span>
                  )}
                </div>
                <h3 className="text-base font-medium text-white/[0.92] mb-1.5">
                  {module.label}
                </h3>
                <p className="text-[13px] text-white/60 leading-relaxed">
                  {module.description}
                </p>
              </button>
            );
          })}
        </div>
      </section>
    </div>
  );
}
