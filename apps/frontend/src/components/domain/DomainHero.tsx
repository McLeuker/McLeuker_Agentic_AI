"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import { Sector } from "@/contexts/SectorContext";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowUp, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface SectorConfig {
  id: Sector;
  label: string;
  placeholder: string;
  tagline: string;
  imageDirection: string;
}

interface DomainHeroProps {
  sector: Sector;
  config: SectorConfig;
  snapshot: string | null;
  isLoading: boolean;
  placeholder?: string;
  starters?: string[];
  onSubmit?: (query: string) => void;
}

// Domain-specific theming — simple, minimal, matching dark theme
const domainThemes: Record<string, {
  tagline: string;
  subtitle: string;
  bgImage: string;
}> = {
  fashion: {
    tagline: "Runway signals, silhouettes & street style intelligence",
    subtitle: "From Paris to Milan — real-time fashion intelligence",
    bgImage: "/images/domains/hero/fashion.jpg",
  },
  beauty: {
    tagline: "Backstage beauty, formulations & brand intelligence",
    subtitle: "Clean beauty · K-beauty · Prestige — decoded by AI",
    bgImage: "/images/domains/hero/beauty.jpg",
  },
  skincare: {
    tagline: "Clinical aesthetics, ingredients & regulatory insights",
    subtitle: "Ingredients · Regulations · Clinical data — all in one place",
    bgImage: "/images/domains/hero/skincare.jpg",
  },
  sustainability: {
    tagline: "Circularity, materials & supply chain transparency",
    subtitle: "Certifications · Impact metrics · Circular models",
    bgImage: "/images/domains/hero/sustainability.jpg",
  },
  "fashion-tech": {
    tagline: "Digital innovation, AI & future technologies",
    subtitle: "AI · AR/VR · Digital fashion · Smart textiles",
    bgImage: "/images/domains/hero/fashion-tech.jpg",
  },
  catwalks: {
    tagline: "Live runway coverage, backstage energy & designer analysis",
    subtitle: "Front row intelligence — every show, every season",
    bgImage: "/images/domains/hero/catwalks.jpg",
  },
  culture: {
    tagline: "Art, exhibitions & social signals shaping fashion",
    subtitle: "Where culture meets commerce — tracked in real time",
    bgImage: "/images/domains/hero/culture.jpg",
  },
  textile: {
    tagline: "Fibers, mills, material innovation & sourcing",
    subtitle: "From raw fiber to finished fabric — intelligence at every stage",
    bgImage: "/images/domains/hero/textile.jpg",
  },
  lifestyle: {
    tagline: "Consumer culture, wellness & lifestyle signals",
    subtitle: "Wellness · Travel · Living — the signals that shape demand",
    bgImage: "/images/domains/hero/lifestyle.jpg",
  },
};

const defaultTheme = {
  tagline: "Cross-domain intelligence for fashion professionals",
  subtitle: "All domains in one place",
  bgImage: "/images/hero-runway.jpg",
};

export function DomainHero({ 
  sector, 
  config, 
  snapshot, 
  isLoading,
  placeholder = "Ask anything...",
  starters = [],
  onSubmit,
}: DomainHeroProps) {
  const theme = domainThemes[sector] || defaultTheme;
  const [query, setQuery] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!query.trim() || !onSubmit) return;
    onSubmit(query.trim());
    setQuery("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleStarterClick = (starter: string) => {
    if (onSubmit) {
      onSubmit(starter);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        120
      )}px`;
    }
  }, [query]);

  return (
    <section className="relative w-full overflow-hidden">
      {/* Background image — clean, grayscale, dark */}
      <div className="absolute inset-0">
        <Image 
          src={theme.bgImage}
          alt={config.label}
          fill
          className="object-cover grayscale brightness-[0.35] contrast-[1.1]"
          priority
        />
        {/* Simple dark overlay — no colored gradients */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/70 to-[#070707]" />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-5xl mx-auto px-6 md:px-8 pt-16 md:pt-20 pb-14 md:pb-18">
        {/* Domain label — simple, no colored badge */}
        <div className="flex justify-center mb-5">
          <span className="text-xs text-white/30 uppercase tracking-[0.2em]">
            {config.label} Intelligence
          </span>
        </div>

        {/* Title — large, clean */}
        <h1 className="font-serif text-5xl md:text-7xl lg:text-8xl font-light tracking-tight text-white/95 mb-4 text-center">
          {config.label}
        </h1>

        {/* Tagline */}
        <p className="text-lg md:text-xl text-white/50 max-w-2xl leading-relaxed mb-2 text-center mx-auto">
          {theme.tagline}
        </p>

        {/* Subtitle */}
        <p className="text-sm text-white/25 max-w-xl leading-relaxed mb-12 md:mb-14 text-center mx-auto">
          {theme.subtitle}
        </p>

        {/* Search Bar — clean, minimal */}
        {onSubmit && (
          <div className="max-w-2xl mx-auto">
            <div className="relative flex items-end gap-3 mb-8">
              <Textarea
                ref={textareaRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                className={cn(
                  "min-h-[56px] max-h-[120px] resize-none pr-14",
                  "bg-white/[0.04] backdrop-blur-sm",
                  "border border-white/[0.08]",
                  "text-white/[0.88] placeholder:text-white/30",
                  "focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white/[0.15]",
                  "text-[15px] rounded-[20px]"
                )}
                rows={1}
              />
              <Button
                onClick={handleSubmit}
                disabled={!query.trim()}
                size="icon"
                className={cn(
                  "absolute right-3 bottom-3 h-10 w-10 rounded-lg",
                  "bg-white/90 text-black hover:bg-white",
                  "disabled:opacity-30 disabled:bg-white/50"
                )}
              >
                <ArrowUp className="h-4 w-4" />
              </Button>
            </div>

            {/* Suggestion cards — matching the section card style */}
            {starters.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {starters.slice(0, 4).map((starter, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleStarterClick(starter)}
                    className={cn(
                      "group flex items-center gap-3 text-left",
                      "px-4 py-3.5 rounded-xl",
                      "bg-white/[0.03] border border-white/[0.06]",
                      "hover:bg-white/[0.06] hover:border-white/[0.12]",
                      "transition-all duration-200"
                    )}
                  >
                    <span className="text-[13px] text-white/55 leading-snug flex-1 line-clamp-2">
                      {starter}
                    </span>
                    <ArrowRight className="w-3.5 h-3.5 text-white/20 group-hover:text-white/50 flex-shrink-0 transition-colors" />
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Bottom fade into page */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-white/[0.04]" />
    </section>
  );
}
