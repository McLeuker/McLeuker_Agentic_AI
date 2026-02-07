"use client";

import { useEffect, useState, useCallback } from "react";
import { Sector } from "@/contexts/SectorContext";
import { cn } from "@/lib/utils";
import {
  ArrowRight,
  Loader2,
  Sparkles,
  BarChart3,
  Layers,
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
} from "lucide-react";
import Image from "next/image";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://web-production-29f3c.up.railway.app";

// Domain images for the Research Modules side panel (different from Weekly Intelligence)
const domainImages: Record<string, string> = {
  fashion: "/images/domains/modules/fashion.jpg",
  beauty: "/images/domains/modules/beauty.jpg",
  skincare: "/images/domains/modules/skincare.jpg",
  sustainability: "/images/domains/modules/sustainability.jpg",
  "fashion-tech": "/images/domains/modules/fashion-tech.jpg",
  catwalks: "/images/domains/modules/catwalks.jpg",
  culture: "/images/domains/modules/culture.jpg",
  textile: "/images/domains/modules/textile.jpg",
  lifestyle: "/images/domains/modules/lifestyle.jpg",
};

// Icon mapping for modules
const moduleIcons: Record<string, React.ElementType> = {
  runway: Shirt,
  brands: Building2,
  street: Users,
  emerging: Sparkles,
  ingredients: Microscope,
  clean: Leaf,
  backstage: Palette,
  actives: Microscope,
  regulation: FileSpreadsheet,
  claims: Search,
  innovation: Sparkles,
  materials: Leaf,
  supply: Factory,
  regulations: FileSpreadsheet,
  certifications: Building2,
  ai: Cpu,
  startups: Building2,
  digital: Globe,
  retail: TrendingUp,
  shows: Shirt,
  designers: Palette,
  styling: Sparkles,
  art: Palette,
  social: Users,
  regional: Globe,
  media: TrendingUp,
  mills: Factory,
  fibers: Microscope,
  suppliers: FileSpreadsheet,
  certification: Leaf,
  consumer: Users,
  wellness: Sparkles,
  culture: Globe,
  travel: TrendingUp,
};

// Static prompts per module (fallback)
const modulePrompts: Record<string, Record<string, string>> = {
  fashion: {
    runway: "Analyze the key silhouette and color trends from recent fashion weeks.",
    brands: "Research current brand positioning shifts among top luxury fashion houses.",
    street: "What street style trends are gaining momentum in major fashion capitals?",
    emerging: "Who are the emerging designers gaining industry attention this season?",
  },
  beauty: {
    ingredients: "What beauty ingredients are trending in prestige skincare and makeup?",
    brands: "Analyze recent beauty brand launches and market positioning strategies.",
    clean: "What clean beauty trends are gaining consumer adoption?",
    backstage: "What makeup trends dominated backstage at recent fashion weeks?",
  },
  skincare: {
    actives: "What active ingredients are leading in clinical skincare innovation?",
    regulation: "What skincare regulatory changes should brands monitor in EU and US?",
    claims: "Analyze trending skincare claims and their scientific backing.",
    innovation: "What skincare product innovations are gaining market attention?",
  },
  sustainability: {
    materials: "What sustainable materials are gaining adoption in fashion production?",
    supply: "Research supply chain transparency best practices in sustainable fashion.",
    regulations: "What ESG regulations should fashion brands prepare for in 2025-2026?",
    certifications: "Compare sustainability certifications relevant to fashion brands.",
  },
  "fashion-tech": {
    ai: "How is AI being adopted across the fashion value chain?",
    startups: "Create a landscape of fashion tech startups to watch.",
    digital: "What digital fashion innovations are gaining consumer adoption?",
    retail: "What retail technologies are transforming the fashion shopping experience?",
  },
  catwalks: {
    shows: "Summarize the standout collections from the latest fashion week season.",
    designers: "Analyze the creative direction of top designers this season.",
    styling: "What styling trends defined recent runway presentations?",
    emerging: "Who are the breakout designers from recent fashion weeks?",
  },
  culture: {
    art: "What art-fashion collaborations are shaping brand narratives?",
    social: "What social movements are influencing fashion brand positioning?",
    regional: "How are regional cultural signals influencing global fashion trends?",
    media: "What media and cultural narratives are shaping fashion consumption?",
  },
  textile: {
    mills: "Find textile mills in Europe with sustainable certifications.",
    fibers: "What are the latest fiber innovations in sustainable fashion?",
    suppliers: "Create a supplier comparison for organic cotton producers.",
    certification: "Compare textile certifications (GOTS, OEKO-TEX, BCI).",
  },
  lifestyle: {
    consumer: "What consumer behavior shifts are influencing luxury lifestyle purchases?",
    wellness: "How are wellness trends influencing fashion and lifestyle?",
    culture: "What cultural shifts are shaping luxury consumer values?",
    travel: "How is travel influencing fashion and lifestyle consumption?",
  },
};

interface ModulePreview {
  id: string;
  label: string;
  description: string;
  live_stat: string;
  preview_headline: string;
  available_insights: number;
}

interface DomainModulesProps {
  sector: Sector;
  onModuleClick: (prompt: string) => void;
}

function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-white/[0.06]", className)}
    />
  );
}

export function DomainModules({ sector, onModuleClick }: DomainModulesProps) {
  const [modules, setModules] = useState<ModulePreview[]>([]);
  const [loading, setLoading] = useState(true);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const fetchModules = useCallback(async () => {
    if (sector === "all") return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/domain-modules`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: sector, force_refresh: false }),
      });
      const data = await res.json();
      if (data.success && data.modules?.length > 0) {
        setModules(data.modules);
      }
    } catch {
      // Silently fail - modules will show without live data
    } finally {
      setLoading(false);
    }
  }, [sector]);

  useEffect(() => {
    if (sector && sector !== "all") {
      fetchModules();
    }
  }, [sector, fetchModules]);

  if (sector === "all") return null;

  const domainImage = domainImages[sector] || domainImages.fashion;
  const prompts = modulePrompts[sector] || modulePrompts.fashion;

  const handleClick = (mod: ModulePreview) => {
    const prompt = prompts[mod.id] || `Research ${mod.label} in ${sector}`;
    onModuleClick(prompt);
  };

  return (
    <section className="w-full bg-[#060606]">
      <div className="max-w-[1200px] mx-auto px-6 md:px-8 py-14 md:py-20">
        {/* Section Header */}
        <div className="flex flex-col gap-2 mb-10 md:mb-14">
          <div className="flex items-center gap-2.5 mb-1">
            <div className="h-px w-8 bg-white/20" />
            <span className="text-[11px] uppercase tracking-[0.2em] text-white/40 font-medium">
              Deep Dive
            </span>
          </div>
          <h2 className="font-serif text-3xl md:text-4xl text-white/[0.95] tracking-tight">
            Research Modules
          </h2>
          <p className="text-[15px] text-white/40 max-w-lg leading-relaxed mt-1">
            Explore specialized research tracks with live data previews.
            Click any module to start an AI-powered deep dive.
          </p>
        </div>

        {/* Layout: modules grid + side image */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
          {/* Modules Grid - Left */}
          <div className="lg:col-span-8">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="p-6 rounded-2xl bg-[#0A0A0A] border border-white/[0.06]"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <Skeleton className="h-10 w-10 rounded-xl" />
                      <div>
                        <Skeleton className="h-5 w-32 mb-1.5" />
                        <Skeleton className="h-3.5 w-24" />
                      </div>
                    </div>
                    <Skeleton className="h-4 w-full mb-3" />
                    <Skeleton className="h-8 w-28 rounded-full" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {modules.map((mod, idx) => {
                  const Icon = moduleIcons[mod.id] || Layers;
                  const isHovered = hoveredIdx === idx;

                  return (
                    <button
                      key={mod.id}
                      onClick={() => handleClick(mod)}
                      onMouseEnter={() => setHoveredIdx(idx)}
                      onMouseLeave={() => setHoveredIdx(null)}
                      className={cn(
                        "group text-left p-6 rounded-2xl relative overflow-hidden",
                        "bg-[#0A0A0A]",
                        "border border-white/[0.06]",
                        "hover:bg-[#0E0E0E] hover:border-white/[0.14]",
                        "transition-all duration-300 ease-out"
                      )}
                    >
                      {/* Subtle gradient on hover */}
                      <div
                        className={cn(
                          "absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 transition-opacity duration-300",
                          isHovered && "opacity-100"
                        )}
                      />

                      <div className="relative z-10">
                        {/* Icon + Label row */}
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center group-hover:bg-white/[0.08] transition-colors">
                              <Icon className="h-4.5 w-4.5 text-white/50 group-hover:text-white/80 transition-colors" />
                            </div>
                            <div>
                              <h3 className="text-[15px] font-medium text-white/[0.90] group-hover:text-white transition-colors">
                                {mod.label}
                              </h3>
                              <p className="text-[12px] text-white/35 mt-0.5">
                                {mod.description}
                              </p>
                            </div>
                          </div>
                          <ArrowRight className="h-4 w-4 text-white/10 group-hover:text-white/50 group-hover:translate-x-0.5 transition-all mt-1" />
                        </div>

                        {/* Preview headline */}
                        <p className="text-[13px] text-white/[0.55] leading-relaxed mb-4 line-clamp-2 min-h-[2.5rem]">
                          {mod.preview_headline}
                        </p>

                        {/* Bottom stats row */}
                        <div className="flex items-center gap-3">
                          {mod.live_stat && (
                            <span className="inline-flex items-center gap-1.5 bg-white/[0.04] border border-white/[0.07] rounded-full px-3 py-1.5 text-[11px] text-white/55 font-medium">
                              <BarChart3 className="h-3 w-3 text-white/40" />
                              {mod.live_stat}
                            </span>
                          )}
                          <span className="text-[11px] text-white/25">
                            {mod.available_insights} insights
                          </span>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Side Image Panel - Right */}
          <div className="lg:col-span-4 relative hidden lg:block">
            <div className="sticky top-24">
              <div className="relative aspect-[3/4] rounded-2xl overflow-hidden">
                <Image
                  src={domainImage}
                  alt={`${sector} research modules`}
                  fill
                  className="object-cover grayscale"
                  sizes="33vw"
                />
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-black/20" />

                {/* Bottom content */}
                <div className="absolute bottom-0 left-0 right-0 p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="h-3.5 w-3.5 text-white/50" />
                    <span className="text-[11px] uppercase tracking-[0.15em] text-white/50 font-medium">
                      Powered by AI
                    </span>
                  </div>
                  <h3 className="font-serif text-xl text-white/85 mb-2 capitalize">
                    {sector.replace("-", " ")} Research
                  </h3>
                  <p className="text-[13px] text-white/40 leading-relaxed">
                    Each module generates a comprehensive research report with
                    real-time data, source citations, and actionable insights.
                  </p>

                  {/* Module count indicator */}
                  <div className="flex items-center gap-2 mt-4 pt-4 border-t border-white/[0.08]">
                    <Layers className="h-3.5 w-3.5 text-white/35" />
                    <span className="text-[12px] text-white/35">
                      {modules.length} modules &middot;{" "}
                      {modules.reduce(
                        (sum, m) => sum + (m.available_insights || 0),
                        0
                      )}{" "}
                      total insights
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
