"use client";

import { useState, useRef, useEffect } from "react";
import { Sector } from "@/contexts/SectorContext";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowUp } from "lucide-react";
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

// One-liner real-time insights per domain
const domainTaglines: Record<Sector, string> = {
  all: "Cross-domain intelligence for fashion professionals",
  fashion: "Runway signals, silhouettes & street style intelligence",
  beauty: "Backstage beauty, formulations & brand intelligence",
  skincare: "Clinical aesthetics, ingredients & regulatory insights",
  sustainability: "Circularity, materials & supply chain transparency",
  "fashion-tech": "Digital innovation, AI & future technologies",
  catwalks: "Live runway coverage, backstage energy & designer analysis",
  culture: "Art, exhibitions & social signals shaping fashion",
  textile: "Fibers, mills, material innovation & sourcing",
  lifestyle: "Consumer culture, wellness & lifestyle signals",
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
  const tagline = domainTaglines[sector] || config.tagline;
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
    <section className="relative w-full bg-black">
      {/* Content */}
      <div className="relative z-10 w-full max-w-5xl mx-auto px-6 md:px-8 pt-12 md:pt-16 pb-12 md:pb-16">
        {/* Title and tagline */}
        <h1 className="font-serif text-5xl md:text-7xl lg:text-8xl font-light tracking-tight text-white mb-4 text-center">
          {config.label}
        </h1>
        <p className="text-lg md:text-xl text-white/60 max-w-2xl leading-relaxed mb-12 md:mb-16 text-center mx-auto">
          {tagline}
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
                  "bg-gradient-to-b from-[#1B1B1B] to-[#111111]",
                  "border border-white/[0.10]",
                  "text-white/[0.88] placeholder:text-white/40",
                  "focus:border-white/[0.18] focus-visible:ring-0 focus-visible:ring-offset-0",
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
                  "bg-white text-black hover:bg-white/90",
                  "disabled:opacity-40 disabled:bg-white/50"
                )}
              >
                <ArrowUp className="h-4 w-4" />
              </Button>
            </div>

            {/* Suggestion chips */}
            {starters.length > 0 && (
              <div className="flex flex-wrap gap-2 justify-center">
                {starters.slice(0, 4).map((starter, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleStarterClick(starter)}
                    className={cn(
                      "text-[13px] px-4 py-2 rounded-full",
                      "bg-[#141414] border border-white/[0.10]",
                      "text-white/[0.78]",
                      "hover:bg-[#1A1A1A] hover:border-white/[0.15]",
                      "active:bg-[#1C1C1C] active:border-white/[0.18]",
                      "transition-all duration-150"
                    )}
                  >
                    {starter}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
