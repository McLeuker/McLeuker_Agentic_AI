"use client";

import { useEffect, useState, useCallback } from "react";
import { Sector } from "@/contexts/SectorContext";
import { cn } from "@/lib/utils";
import {
  RefreshCw,
  Zap,
  TrendingUp,
  ArrowUpRight,
  Clock,
  Signal,
  Loader2,
  AlertCircle,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://web-production-29f3c.up.railway.app";

export interface IntelligenceItem {
  title: string;
  description: string;
  source: string;
  sourceUrl?: string;
  date: string;
  confidence: "high" | "medium" | "low";
  category?: string;
}

interface LiveSignal {
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  category: string;
  source: string;
  metric: string;
  timestamp: string;
}

interface DomainInsightsProps {
  sector: Sector;
  onSignalClick?: (prompt: string) => void;
}

const impactConfig = {
  high: {
    dot: "bg-white",
    glow: "shadow-[0_0_8px_rgba(255,255,255,0.3)]",
    border: "border-white/[0.15]",
    label: "High Impact",
    pulse: true,
  },
  medium: {
    dot: "bg-white/60",
    glow: "",
    border: "border-white/[0.10]",
    label: "Medium",
    pulse: false,
  },
  low: {
    dot: "bg-white/40",
    glow: "",
    border: "border-white/[0.08]",
    label: "Low",
    pulse: false,
  },
};

function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-white/[0.06]", className)}
    />
  );
}

export function DomainInsights({ sector, onSignalClick }: DomainInsightsProps) {
  const [signals, setSignals] = useState<LiveSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchSignals = useCallback(
    async (forceRefresh = false) => {
      if (sector === "all") return;
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_URL}/api/v1/live-signals`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            domain: sector,
            force_refresh: forceRefresh,
          }),
        });
        const data = await res.json();
        if (data.success && data.signals?.length > 0) {
          setSignals(data.signals.slice(0, 6));
          setLastUpdated(new Date());
        } else {
          setError(data.error || "No live signals available.");
        }
      } catch {
        setError("Failed to fetch live signals.");
      } finally {
        setLoading(false);
      }
    },
    [sector]
  );

  useEffect(() => {
    if (sector && sector !== "all") {
      fetchSignals();
    }
  }, [sector, fetchSignals]);

  const handleSignalClick = (signal: LiveSignal) => {
    if (onSignalClick) {
      onSignalClick(
        `Tell me more about: ${signal.title}. ${signal.description}`
      );
    }
  };

  const formatTimestamp = (ts: string) => {
    try {
      const date = new Date(ts);
      const now = new Date();
      const diffHours = Math.floor(
        (now.getTime() - date.getTime()) / (1000 * 60 * 60)
      );
      if (diffHours < 1) return "Just now";
      if (diffHours < 24) return `${diffHours}h ago`;
      return "Yesterday";
    } catch {
      return "";
    }
  };

  if (sector === "all") return null;

  const highImpactCount = signals.filter((s) => s.impact === "high").length;

  return (
    <section className="w-full bg-[#080808]">
      <div className="max-w-[1200px] mx-auto px-6 md:px-8 py-14 md:py-20">
        {/* Section Header */}
        <div className="flex items-start justify-between mb-10 md:mb-14">
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <div className="h-2 w-2 rounded-full bg-white animate-pulse" />
                  <div className="absolute inset-0 h-2 w-2 rounded-full bg-white/50 animate-ping" />
                </div>
                <span className="text-[11px] uppercase tracking-[0.2em] text-white/50 font-medium">
                  Live Intelligence
                </span>
              </div>
              {!loading && signals.length > 0 && (
                <span className="text-[11px] text-white/30 border border-white/[0.08] rounded-full px-2.5 py-0.5">
                  {highImpactCount} high impact
                </span>
              )}
            </div>
            <h2 className="font-serif text-3xl md:text-4xl text-white/[0.95] tracking-tight">
              What&apos;s Happening Now
            </h2>
            {lastUpdated && !loading && (
              <p className="text-[13px] text-white/30 flex items-center gap-1.5">
                <Clock className="h-3 w-3" />
                Updated{" "}
                {lastUpdated.toLocaleTimeString("en-US", {
                  hour: "numeric",
                  minute: "2-digit",
                })}
              </p>
            )}
          </div>

          {!loading && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => fetchSignals(true)}
              className="h-9 px-3 bg-[#111] border border-white/[0.08] text-white/50 hover:bg-[#1A1A1A] hover:text-white/80 rounded-lg mt-2"
            >
              <RefreshCw className="h-3.5 w-3.5 mr-2" />
              <span className="text-[12px]">Refresh</span>
            </Button>
          )}
        </div>

        {loading ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-6">
              <Loader2 className="h-4 w-4 text-white/40 animate-spin" />
              <span className="text-[13px] text-white/40">
                Scanning live sources...
              </span>
            </div>
            {/* Featured skeleton */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
              <div className="p-7 rounded-2xl bg-[#0C0C0C] border border-white/[0.06]">
                <Skeleton className="h-5 w-20 mb-4" />
                <Skeleton className="h-6 w-4/5 mb-3" />
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-3/4 mb-5" />
                <div className="flex gap-3">
                  <Skeleton className="h-8 w-24 rounded-full" />
                  <Skeleton className="h-8 w-16 rounded-full" />
                </div>
              </div>
              <div className="p-7 rounded-2xl bg-[#0C0C0C] border border-white/[0.06]">
                <Skeleton className="h-5 w-20 mb-4" />
                <Skeleton className="h-6 w-4/5 mb-3" />
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-3/4 mb-5" />
                <div className="flex gap-3">
                  <Skeleton className="h-8 w-24 rounded-full" />
                  <Skeleton className="h-8 w-16 rounded-full" />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="p-5 rounded-xl bg-[#0C0C0C] border border-white/[0.06]"
                >
                  <Skeleton className="h-4 w-16 mb-3" />
                  <Skeleton className="h-5 w-full mb-2" />
                  <Skeleton className="h-4 w-3/4" />
                </div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <AlertCircle className="h-8 w-8 text-white/30 mb-4" />
            <p className="text-white/50 text-[15px] mb-4">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchSignals(true)}
              className="h-10 px-5 bg-[#111] border-white/[0.08] text-white/60 hover:bg-[#1A1A1A] hover:text-white"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Featured signals (first 2) - large cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {signals.slice(0, 2).map((signal, idx) => {
                const impact = impactConfig[signal.impact] || impactConfig.medium;
                return (
                  <button
                    key={idx}
                    onClick={() => handleSignalClick(signal)}
                    className={cn(
                      "group text-left p-7 rounded-2xl relative overflow-hidden",
                      "bg-[#0C0C0C]",
                      "border",
                      impact.border,
                      "hover:bg-[#101010] hover:border-white/[0.18]",
                      "transition-all duration-200 ease-out"
                    )}
                  >
                    {/* Top row */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2.5">
                        <div className="flex items-center gap-1.5">
                          <div
                            className={cn(
                              "h-1.5 w-1.5 rounded-full",
                              impact.dot,
                              impact.glow,
                              impact.pulse && "animate-pulse"
                            )}
                          />
                          <span className="text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium">
                            {impact.label}
                          </span>
                        </div>
                        <span className="text-[10px] uppercase tracking-[0.15em] text-white/30 border border-white/[0.08] rounded-full px-2 py-0.5">
                          {signal.category}
                        </span>
                      </div>
                      <span className="text-[11px] text-white/25 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatTimestamp(signal.timestamp)}
                      </span>
                    </div>

                    {/* Title */}
                    <h3 className="text-lg font-medium text-white/[0.92] leading-snug mb-3 group-hover:text-white transition-colors">
                      {signal.title}
                    </h3>

                    {/* Description */}
                    <p className="text-[14px] text-white/[0.50] leading-relaxed mb-5">
                      {signal.description}
                    </p>

                    {/* Bottom: metric + source + arrow */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {signal.metric && (
                          <span className="inline-flex items-center gap-1.5 bg-white/[0.06] border border-white/[0.08] rounded-full px-3 py-1.5 text-[12px] text-white/70 font-medium">
                            <Activity className="h-3 w-3 text-white/50" />
                            {signal.metric}
                          </span>
                        )}
                        <span className="text-[12px] text-white/30 font-medium">
                          {signal.source}
                        </span>
                      </div>
                      <ArrowUpRight className="h-4 w-4 text-white/15 group-hover:text-white/50 transition-all" />
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Secondary signals (3-6) - compact row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {signals.slice(2, 6).map((signal, idx) => {
                const impact = impactConfig[signal.impact] || impactConfig.medium;
                return (
                  <button
                    key={idx + 2}
                    onClick={() => handleSignalClick(signal)}
                    className={cn(
                      "group text-left p-5 rounded-xl relative",
                      "bg-[#0A0A0A]",
                      "border border-white/[0.06]",
                      "hover:bg-[#0E0E0E] hover:border-white/[0.12]",
                      "transition-all duration-200"
                    )}
                  >
                    {/* Category + impact */}
                    <div className="flex items-center gap-2 mb-3">
                      <div
                        className={cn(
                          "h-1.5 w-1.5 rounded-full",
                          impact.dot,
                          impact.pulse && "animate-pulse"
                        )}
                      />
                      <span className="text-[10px] uppercase tracking-[0.12em] text-white/35 font-medium">
                        {signal.category}
                      </span>
                    </div>

                    {/* Title */}
                    <h4 className="text-[13px] font-medium text-white/[0.85] leading-snug mb-2 group-hover:text-white transition-colors line-clamp-2">
                      {signal.title}
                    </h4>

                    {/* Metric or source */}
                    <div className="flex items-center justify-between mt-auto">
                      {signal.metric ? (
                        <span className="text-[11px] text-white/40 font-medium flex items-center gap-1">
                          <TrendingUp className="h-3 w-3" />
                          {signal.metric}
                        </span>
                      ) : (
                        <span className="text-[11px] text-white/25">
                          {signal.source}
                        </span>
                      )}
                      <ArrowUpRight className="h-3 w-3 text-white/10 group-hover:text-white/40 transition-all" />
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Live pulse bar */}
            <div className="flex items-center justify-center gap-3 pt-2">
              <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.05]">
                <Signal className="h-3 w-3 text-white/30" />
                <span className="text-[11px] text-white/25">
                  {signals.length} live signals across{" "}
                  {new Set(signals.map((s) => s.source)).size} sources
                </span>
              </div>
              <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
