"use client";

import { useState } from "react";
import { useSector } from "@/contexts/SectorContext";
import { cn } from "@/lib/utils";
import { ArrowRight, Zap, Microscope } from "lucide-react";
import { Input } from "@/components/ui/input";

type ResearchMode = "quick" | "deep";

interface DomainStarterPanelProps {
  onSelectPrompt: (prompt: string, mode?: ResearchMode) => void;
  className?: string;
}

export function DomainStarterPanel({
  onSelectPrompt,
  className,
}: DomainStarterPanelProps) {
  const { currentSector, getSectorConfig, getStarters } = useSector();
  const config = getSectorConfig();
  const starters = getStarters();
  const [searchValue, setSearchValue] = useState("");
  const [researchMode, setResearchMode] = useState<ResearchMode>("quick");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchValue.trim()) {
      onSelectPrompt(searchValue.trim(), researchMode);
      setSearchValue("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (searchValue.trim()) {
        onSelectPrompt(searchValue.trim(), researchMode);
        setSearchValue("");
      }
    }
  };

  // All Domains - Hero style centered interface
  if (currentSector === "all") {
    return (
      <div className={cn("flex flex-col h-full min-h-[calc(100vh-200px)] bg-black", className)}>
        <div className="flex-1 flex flex-col items-center justify-center px-6">
          {/* Title */}
          <h1 className="text-4xl md:text-5xl font-serif text-white mb-3 text-center">
            Where is my mind?
          </h1>
          
          {/* Subtitle */}
          <p className="text-white/60 text-sm mb-8 text-center">
            Powered by McLeuker AI • All Domains Intelligence Mode
          </p>

          {/* Mode Toggle */}
          <div className="flex items-center gap-1 bg-white/[0.05] rounded-lg p-1 mb-6">
            <button
              onClick={() => setResearchMode("quick")}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all",
                researchMode === "quick" 
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" 
                  : "text-white/60 hover:text-white hover:bg-white/[0.08]"
              )}
            >
              <Zap className="w-3.5 h-3.5" />
              Quick
            </button>
            <button
              onClick={() => setResearchMode("deep")}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all",
                researchMode === "deep" 
                  ? "bg-purple-600 text-white shadow-lg shadow-purple-600/20" 
                  : "text-white/60 hover:text-white hover:bg-white/[0.08]"
              )}
            >
              <Microscope className="w-3.5 h-3.5" />
              Deep
            </button>
          </div>

          {/* Search Bubble */}
          <form onSubmit={handleSubmit} className="w-full max-w-2xl mb-4">
            <div className="relative">
              <Input
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything across all domains..."
                className={cn(
                  "w-full h-14 px-6 rounded-full",
                  "bg-white/10 border-white/20",
                  "text-white placeholder:text-white/40",
                  "focus:bg-white/15 focus:border-white/30",
                  "transition-all duration-200"
                )}
              />
            </div>
          </form>

          {/* Credit Hint */}
          <div className="text-center mb-8">
            <p className="text-white/50 text-xs">
              {researchMode === "quick" ? "4-12" : "50"} credits • Press Enter to send
            </p>
            <p className="text-white/40 text-xs mt-1 hidden sm:block">
              Shift + Enter for new line
            </p>
          </div>

          {/* Trending Topics */}
          <div className="flex flex-wrap justify-center gap-3 max-w-2xl">
            {starters.map((topic, index) => (
              <button
                key={index}
                onClick={() => onSelectPrompt(topic, researchMode)}
                className={cn(
                  "px-4 py-2 rounded-full",
                  "border border-white/30",
                  "text-white/80 text-sm",
                  "hover:bg-white/10 hover:border-white/50",
                  "transition-all duration-200"
                )}
              >
                {topic}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Standard domain view
  return (
    <div className={cn("flex flex-col animate-fade-in", className)}>
      {/* Domain Header */}
      <div className="text-center py-12 px-6">
        <h1 className="text-3xl md:text-4xl font-serif text-white mb-3">
          {config.label}
        </h1>
        <p className="text-white/60 text-sm max-w-lg mx-auto">
          {config.tagline}
        </p>
      </div>

      {/* Content Area */}
      <div className="px-6 py-6 max-w-3xl mx-auto w-full">
        {/* Starter Questions */}
        <div>
          <h3 className="text-sm font-medium text-white/50 mb-4 uppercase tracking-wide">
            Explore {config.label}
          </h3>
          
          <div className="grid gap-2">
            {starters.map((question, index) => (
              <button
                key={index}
                onClick={() => onSelectPrompt(question)}
                className={cn(
                  "group flex items-center justify-between gap-4 p-4 rounded-lg",
                  "bg-white/[0.03] border border-white/[0.08]",
                  "hover:border-white/[0.15] hover:bg-white/[0.06]",
                  "transition-all duration-200",
                  "text-left"
                )}
              >
                <span className="text-[15px] text-white/90">
                  {question}
                </span>
                <ArrowRight className={cn(
                  "h-4 w-4 text-white/40 shrink-0",
                  "group-hover:text-white group-hover:translate-x-0.5",
                  "transition-all duration-200"
                )} />
              </button>
            ))}
          </div>
        </div>

        {/* Minimal branding */}
        <div className="mt-8 pt-6 border-t border-white/[0.08]">
          <p className="text-xs text-white/40 text-center">
            Powered by McLeuker AI • {config.label} Intelligence Mode
          </p>
        </div>
      </div>
    </div>
  );
}
