"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import { Sector } from "@/contexts/SectorContext";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowUp, Sparkles, TrendingUp, Palette, Leaf, Cpu, Camera, Globe, Layers, Heart } from "lucide-react";
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

// Domain-specific theming — each domain is a unique world
const domainThemes: Record<string, {
  tagline: string;
  subtitle: string;
  accent: string;        // Primary accent color
  accentRgb: string;     // RGB for gradients
  gradientFrom: string;  // Gradient start
  gradientVia: string;   // Gradient middle
  icon: typeof Sparkles;
  bgImage: string;       // Domain-specific hero image
  overlayStyle: string;  // Custom overlay gradient
}> = {
  fashion: {
    tagline: "Runway signals, silhouettes & street style intelligence",
    subtitle: "From Paris to Milan — real-time fashion intelligence",
    accent: "#C9A96E",
    accentRgb: "201,169,110",
    gradientFrom: "from-[#C9A96E]/10",
    gradientVia: "via-[#C9A96E]/5",
    icon: Sparkles,
    bgImage: "/images/domains/weekly/fashion.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(30,25,18,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
  beauty: {
    tagline: "Backstage beauty, formulations & brand intelligence",
    subtitle: "Clean beauty · K-beauty · Prestige — decoded by AI",
    accent: "#D4A0B0",
    accentRgb: "212,160,176",
    gradientFrom: "from-[#D4A0B0]/10",
    gradientVia: "via-[#D4A0B0]/5",
    icon: Palette,
    bgImage: "/images/domains/weekly/beauty.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(35,20,28,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
  skincare: {
    tagline: "Clinical aesthetics, ingredients & regulatory insights",
    subtitle: "Ingredients · Regulations · Clinical data — all in one place",
    accent: "#8ECAE6",
    accentRgb: "142,202,230",
    gradientFrom: "from-[#8ECAE6]/10",
    gradientVia: "via-[#8ECAE6]/5",
    icon: Heart,
    bgImage: "/images/domains/weekly/skincare.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.93) 0%, rgba(18,28,35,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
  sustainability: {
    tagline: "Circularity, materials & supply chain transparency",
    subtitle: "Certifications · Impact metrics · Circular models",
    accent: "#6B9E78",
    accentRgb: "107,158,120",
    gradientFrom: "from-[#6B9E78]/10",
    gradientVia: "via-[#6B9E78]/5",
    icon: Leaf,
    bgImage: "/images/domains/weekly/sustainability.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(15,30,18,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
  "fashion-tech": {
    tagline: "Digital innovation, AI & future technologies",
    subtitle: "AI · AR/VR · Digital fashion · Smart textiles",
    accent: "#7B68EE",
    accentRgb: "123,104,238",
    gradientFrom: "from-[#7B68EE]/10",
    gradientVia: "via-[#7B68EE]/5",
    icon: Cpu,
    bgImage: "/images/domains/weekly/fashion-tech.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.93) 0%, rgba(20,16,40,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
  catwalks: {
    tagline: "Live runway coverage, backstage energy & designer analysis",
    subtitle: "Front row intelligence — every show, every season",
    accent: "#E8D5B7",
    accentRgb: "232,213,183",
    gradientFrom: "from-[#E8D5B7]/10",
    gradientVia: "via-[#E8D5B7]/5",
    icon: Camera,
    bgImage: "/images/domains/weekly/catwalks.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(35,30,22,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
  culture: {
    tagline: "Art, exhibitions & social signals shaping fashion",
    subtitle: "Where culture meets commerce — tracked in real time",
    accent: "#E07A5F",
    accentRgb: "224,122,95",
    gradientFrom: "from-[#E07A5F]/10",
    gradientVia: "via-[#E07A5F]/5",
    icon: Globe,
    bgImage: "/images/domains/weekly/culture.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(38,20,15,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
  textile: {
    tagline: "Fibers, mills, material innovation & sourcing",
    subtitle: "From raw fiber to finished fabric — intelligence at every stage",
    accent: "#A3B18A",
    accentRgb: "163,177,138",
    gradientFrom: "from-[#A3B18A]/10",
    gradientVia: "via-[#A3B18A]/5",
    icon: Layers,
    bgImage: "/images/domains/weekly/textile.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(22,28,18,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
  lifestyle: {
    tagline: "Consumer culture, wellness & lifestyle signals",
    subtitle: "Wellness · Travel · Living — the signals that shape demand",
    accent: "#DDA15E",
    accentRgb: "221,161,94",
    gradientFrom: "from-[#DDA15E]/10",
    gradientVia: "via-[#DDA15E]/5",
    icon: TrendingUp,
    bgImage: "/images/domains/weekly/lifestyle.jpg",
    overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(35,28,15,0.85) 50%, rgba(0,0,0,0.95) 100%)",
  },
};

const defaultTheme = {
  tagline: "Cross-domain intelligence for fashion professionals",
  subtitle: "All domains in one place",
  accent: "#5c6652",
  accentRgb: "92,102,82",
  gradientFrom: "from-[#5c6652]/10",
  gradientVia: "via-[#5c6652]/5",
  icon: Sparkles,
  bgImage: "/images/hero-runway.jpg",
  overlayStyle: "linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(15,15,15,0.88) 50%, rgba(0,0,0,0.95) 100%)",
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
  const Icon = theme.icon;
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
      {/* Background image */}
      <div className="absolute inset-0">
        <Image 
          src={theme.bgImage}
          alt={config.label}
          fill
          className="object-cover grayscale contrast-[1.1] brightness-[0.7]"
          priority
        />
        {/* Domain-specific overlay */}
        <div 
          className="absolute inset-0" 
          style={{ background: theme.overlayStyle }}
        />
        {/* Radial glow in domain accent color */}
        <div 
          className="absolute inset-0 opacity-30"
          style={{ 
            background: `radial-gradient(ellipse 60% 40% at 50% 60%, rgba(${theme.accentRgb}, 0.15) 0%, transparent 70%)` 
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-5xl mx-auto px-6 md:px-8 pt-16 md:pt-20 pb-14 md:pb-18">
        {/* Domain badge */}
        <div className="flex justify-center mb-6">
          <div 
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full backdrop-blur-sm border"
            style={{ 
              backgroundColor: `rgba(${theme.accentRgb}, 0.08)`,
              borderColor: `rgba(${theme.accentRgb}, 0.2)`,
            }}
          >
            <Icon className="w-3.5 h-3.5" style={{ color: theme.accent }} />
            <span className="text-xs uppercase tracking-[0.15em]" style={{ color: `rgba(${theme.accentRgb}, 0.8)` }}>
              {config.label} Intelligence
            </span>
          </div>
        </div>

        {/* Title */}
        <h1 className="font-serif text-5xl md:text-7xl lg:text-8xl font-light tracking-tight text-white mb-4 text-center">
          {config.label}
        </h1>

        {/* Tagline */}
        <p className="text-lg md:text-xl text-white/60 max-w-2xl leading-relaxed mb-3 text-center mx-auto">
          {theme.tagline}
        </p>

        {/* Subtitle — domain-specific flavor */}
        <p className="text-sm text-white/35 max-w-xl leading-relaxed mb-12 md:mb-14 text-center mx-auto">
          {theme.subtitle}
        </p>

        {/* Integrated Search Bar */}
        {onSubmit && (
          <div className="max-w-2xl mx-auto">
            {/* Input area */}
            <div className="relative flex items-end gap-3 mb-6">
              <Textarea
                ref={textareaRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                className={cn(
                  "min-h-[56px] max-h-[120px] resize-none pr-14",
                  "bg-gradient-to-b from-[#1B1B1B]/90 to-[#111111]/90 backdrop-blur-sm",
                  "border",
                  "text-white/[0.88] placeholder:text-white/40",
                  "focus-visible:ring-0 focus-visible:ring-offset-0",
                  "text-[15px] rounded-[20px]"
                )}
                style={{
                  borderColor: `rgba(${theme.accentRgb}, 0.15)`,
                }}
                rows={1}
              />
              <Button
                onClick={handleSubmit}
                disabled={!query.trim()}
                size="icon"
                className={cn(
                  "absolute right-3 bottom-3 h-10 w-10 rounded-lg",
                  "text-black",
                  "disabled:opacity-40"
                )}
                style={{
                  backgroundColor: theme.accent,
                }}
              >
                <ArrowUp className="h-4 w-4" />
              </Button>
            </div>

            {/* Suggestion chips — styled with domain accent */}
            {starters.length > 0 && (
              <div className="flex flex-wrap gap-2 justify-center">
                {starters.slice(0, 4).map((starter, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleStarterClick(starter)}
                    className={cn(
                      "text-[13px] px-4 py-2 rounded-full",
                      "backdrop-blur-sm",
                      "transition-all duration-150"
                    )}
                    style={{
                      backgroundColor: `rgba(${theme.accentRgb}, 0.06)`,
                      borderWidth: 1,
                      borderColor: `rgba(${theme.accentRgb}, 0.15)`,
                      color: `rgba(255,255,255,0.75)`,
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = `rgba(${theme.accentRgb}, 0.12)`;
                      e.currentTarget.style.borderColor = `rgba(${theme.accentRgb}, 0.3)`;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = `rgba(${theme.accentRgb}, 0.06)`;
                      e.currentTarget.style.borderColor = `rgba(${theme.accentRgb}, 0.15)`;
                    }}
                  >
                    {starter}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Bottom accent line */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-px"
        style={{
          background: `linear-gradient(90deg, transparent 0%, rgba(${theme.accentRgb}, 0.3) 50%, transparent 100%)`,
        }}
      />
    </section>
  );
}
