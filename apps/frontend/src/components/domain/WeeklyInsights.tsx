"use client";

import { useEffect, useState, useCallback } from "react";
import { Sector } from "@/contexts/SectorContext";
import { cn } from "@/lib/utils";
import { RefreshCw, ArrowRight, Clock, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import Image from "next/image";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://web-production-29f3c.up.railway.app";

// Domain-specific images (black & white)
const domainImages: Record<string, string> = {
  fashion: "/images/domains/fashion.jpg",
  beauty: "/images/domains/beauty.jpg",
  skincare: "/images/domains/skincare.jpg",
  sustainability: "/images/domains/sustainability.jpg",
  "fashion-tech": "/images/domains/fashion-tech.jpg",
  catwalks: "/images/domains/catwalks.jpg",
  culture: "/images/domains/culture.jpg",
  textile: "/images/domains/textile.jpg",
  lifestyle: "/images/domains/lifestyle.jpg",
};

// Category color accents (subtle, on-brand)
const categoryColors: Record<string, string> = {
  Runway: "bg-white/[0.08] text-white/70 border-white/[0.12]",
  Business: "bg-white/[0.08] text-white/70 border-white/[0.12]",
  Trend: "bg-white/[0.08] text-white/70 border-white/[0.12]",
  Innovation: "bg-white/[0.08] text-white/70 border-white/[0.12]",
  Launch: "bg-white/[0.08] text-white/70 border-white/[0.12]",
  Culture: "bg-white/[0.08] text-white/70 border-white/[0.12]",
  Regulation: "bg-white/[0.08] text-white/70 border-white/[0.12]",
  Celebrity: "bg-white/[0.08] text-white/70 border-white/[0.12]",
  Default: "bg-white/[0.08] text-white/70 border-white/[0.12]",
};

interface InsightItem {
  title: string;
  summary: string;
  source: string;
  category: string;
  date: string;
}

interface WeeklyInsightsProps {
  sector: Sector;
  onInsightClick: (prompt: string) => void;
}

function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn("animate-pulse rounded-md bg-white/[0.06]", className)} />
  );
}

export function WeeklyInsights({ sector, onInsightClick }: WeeklyInsightsProps) {
  const [insights, setInsights] = useState<InsightItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/weekly-insights`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: sector, force_refresh: forceRefresh }),
      });
      const data = await res.json();
      if (data.success && data.insights?.length > 0) {
        setInsights(data.insights.slice(0, 10));
      } else {
        setError(data.error || "No insights available right now.");
      }
    } catch (e) {
      setError("Failed to load insights. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [sector]);

  useEffect(() => {
    if (sector && sector !== "all") {
      fetchInsights();
    }
  }, [sector, fetchInsights]);

  const handleInsightClick = (insight: InsightItem) => {
    const prompt = `Tell me more about: ${insight.title}. ${insight.summary}`;
    onInsightClick(prompt);
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diffDays = Math.floor(
        (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
      );
      if (diffDays === 0) return "Today";
      if (diffDays === 1) return "Yesterday";
      if (diffDays < 7) return `${diffDays}d ago`;
      return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    } catch {
      return "";
    }
  };

  if (sector === "all") return null;

  const domainImage = domainImages[sector] || domainImages.fashion;

  return (
    <section className="w-full bg-[#070707] overflow-hidden">
      <div className="max-w-[1200px] mx-auto px-6 md:px-8 py-14 md:py-20">
        {/* Section Header */}
        <div className="flex items-start justify-between mb-10 md:mb-14">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2.5 mb-1">
              <div className="h-px w-8 bg-white/20" />
              <span className="text-[11px] uppercase tracking-[0.2em] text-white/40 font-medium">
                Last 7 Days
              </span>
            </div>
            <h2 className="font-serif text-3xl md:text-4xl text-white/[0.95] tracking-tight">
              Weekly Intelligence
            </h2>
            <p className="text-[15px] text-white/50 max-w-md leading-relaxed mt-1">
              The most significant developments shaping{" "}
              <span className="text-white/70">{sector.replace("-", " ")}</span>{" "}
              this week.
            </p>
          </div>

          {!loading && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => fetchInsights(true)}
              className="h-9 px-3 bg-[#111] border border-white/[0.08] text-white/50 hover:bg-[#1A1A1A] hover:text-white/80 rounded-lg mt-2"
            >
              <RefreshCw className="h-3.5 w-3.5 mr-2" />
              <span className="text-[12px]">Refresh</span>
            </Button>
          )}
        </div>

        {/* Main Layout: Image + Insights Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
          {/* Domain Image - Left Column */}
          <div className="lg:col-span-4 relative">
            <div className="relative aspect-[3/4] lg:aspect-[3/5] rounded-2xl overflow-hidden">
              <Image
                src={domainImage}
                alt={`${sector} intelligence`}
                fill
                className="object-cover grayscale"
                sizes="(max-width: 1024px) 100vw, 33vw"
              />
              {/* Dark overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-black/10" />
              {/* Bottom label */}
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="h-3.5 w-3.5 text-white/60" />
                  <span className="text-[11px] uppercase tracking-[0.15em] text-white/60 font-medium">
                    AI-Curated
                  </span>
                </div>
                <h3 className="font-serif text-2xl text-white/90 capitalize">
                  {sector.replace("-", " ")}
                </h3>
                <p className="text-[13px] text-white/50 mt-1">
                  {insights.length > 0
                    ? `${insights.length} insights this week`
                    : "Loading intelligence..."}
                </p>
              </div>
            </div>
          </div>

          {/* Insights Grid - Right Column */}
          <div className="lg:col-span-8">
            {loading ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3 mb-6">
                  <Loader2 className="h-4 w-4 text-white/40 animate-spin" />
                  <span className="text-[13px] text-white/40">
                    Gathering intelligence...
                  </span>
                </div>
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div
                    key={i}
                    className="p-5 rounded-xl bg-[#0E0E0E] border border-white/[0.06]"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <Skeleton className="h-5 w-16" />
                      <Skeleton className="h-4 w-12" />
                    </div>
                    <Skeleton className="h-5 w-4/5 mb-2" />
                    <Skeleton className="h-4 w-full" />
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <p className="text-white/50 text-[15px] mb-4">{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fetchInsights(true)}
                  className="h-10 px-5 bg-[#111] border-white/[0.08] text-white/60 hover:bg-[#1A1A1A] hover:text-white"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {insights.map((insight, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleInsightClick(insight)}
                    className={cn(
                      "group text-left p-5 rounded-xl",
                      "bg-[#0C0C0C]",
                      "border border-white/[0.06]",
                      "hover:bg-[#111] hover:border-white/[0.12]",
                      "transition-all duration-200 ease-out",
                      "cursor-pointer relative overflow-hidden"
                    )}
                  >
                    {/* Top row: category + date */}
                    <div className="flex items-center justify-between mb-3">
                      <span
                        className={cn(
                          "inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider",
                          categoryColors[insight.category] ||
                            categoryColors.Default
                        )}
                      >
                        {insight.category}
                      </span>
                      <span className="flex items-center gap-1 text-[11px] text-white/30">
                        <Clock className="h-3 w-3" />
                        {formatDate(insight.date)}
                      </span>
                    </div>

                    {/* Title */}
                    <h4 className="text-[14px] font-medium text-white/[0.88] leading-snug mb-2 group-hover:text-white transition-colors line-clamp-2">
                      {insight.title}
                    </h4>

                    {/* Summary */}
                    <p className="text-[13px] text-white/[0.45] leading-relaxed mb-3 line-clamp-2">
                      {insight.summary}
                    </p>

                    {/* Bottom: source + arrow */}
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] text-white/30 font-medium">
                        {insight.source}
                      </span>
                      <ArrowRight className="h-3.5 w-3.5 text-white/20 group-hover:text-white/50 group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
