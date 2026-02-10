"use client";

import { useState, useEffect, useCallback } from "react";
import { 
  TrendingUp, 
  ArrowUp, 
  ArrowDown, 
  Minus, 
  RefreshCw,
  Crown,
  Hash,
  BarChart3,
  Globe,
  Sparkles
} from "lucide-react";
import { cn } from "@/lib/utils";

// =============================================================================
// Types
// =============================================================================

interface TrendingTag {
  category: string;
  tag: string;
  growth_pct: number;
  source: string;
}

interface BrandRanking {
  rank: number;
  name: string;
  change: number;
  mentions: number;
}

interface TrendsData {
  trending_tags: TrendingTag[];
  brand_rankings: BrandRanking[];
  social_platforms: string[];
  date_range: string;
  domain: string;
  cached_at?: string;
  data_sources?: string[];
}

// =============================================================================
// Social Platform Icons
// =============================================================================

const PlatformIcon = ({ platform, className }: { platform: string; className?: string }) => {
  const iconMap: Record<string, string> = {
    "Instagram": "IG",
    "TikTok": "TT",
    "X": "𝕏",
    "LinkedIn": "in",
    "Pinterest": "P",
  };
  return (
    <span className={cn("text-[9px] font-mono uppercase tracking-wider", className)}>
      {iconMap[platform] || platform.charAt(0)}
    </span>
  );
};

// =============================================================================
// Mini Sparkline Component
// =============================================================================

const MiniSparkline = ({ trend }: { trend: "up" | "down" | "flat" }) => {
  const points = trend === "up" 
    ? "0,12 4,10 8,8 12,9 16,6 20,7 24,4 28,5 32,2 36,1"
    : trend === "down"
    ? "0,2 4,3 8,4 12,3 16,6 20,5 24,8 28,7 32,10 36,11"
    : "0,6 4,7 8,5 12,6 16,7 20,5 24,6 28,7 32,6 36,5";
  
  return (
    <svg width="40" height="14" viewBox="0 0 40 14" className="opacity-40">
      <polyline
        points={points}
        fill="none"
        stroke={trend === "up" ? "#4ade80" : trend === "down" ? "#f87171" : "#94a3b8"}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

// =============================================================================
// Format Numbers
// =============================================================================

const formatMentions = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`;
  return num.toString();
};

// =============================================================================
// Trending Tags Section
// =============================================================================

function TrendingTagsSection({ tags, dateRange }: { tags: TrendingTag[]; dateRange: string }) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-[#0a0a0a]/80 backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-1 h-4 rounded-full bg-emerald-500/60" />
            <h3 className="text-[15px] font-medium text-white/90 tracking-tight">
              The most growing tags of the week
            </h3>
          </div>
          <span className="text-[10px] text-white/30 font-mono">{dateRange}</span>
        </div>
        <p className="text-[11px] text-white/30 mt-1 ml-3">
          Based on social media engagement across Instagram, TikTok, X, LinkedIn & Pinterest
        </p>
      </div>
      
      {/* Tags Grid */}
      <div className="grid grid-cols-4 gap-px bg-white/[0.03]">
        {tags.map((tag, i) => (
          <div 
            key={i}
            className="px-4 py-4 bg-[#0a0a0a] hover:bg-white/[0.02] transition-colors group"
          >
            {/* Category Label */}
            <div className="flex items-center gap-1.5 mb-2">
              <span className="text-[9px] font-semibold tracking-[0.15em] text-white/25 uppercase">
                {tag.category}
              </span>
            </div>
            
            {/* Tag Name */}
            <p className="text-[15px] font-medium text-white/85 leading-tight mb-2 group-hover:text-white transition-colors">
              {tag.tag}
            </p>
            
            {/* Growth + Source */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1">
                <ArrowUp className="w-3 h-3 text-emerald-400/70" />
                <span className="text-[13px] font-semibold text-emerald-400/70">
                  {tag.growth_pct}%
                </span>
              </div>
              <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-white/[0.04]">
                <PlatformIcon platform={tag.source} className="text-white/30" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Brand Rankings Section
// =============================================================================

function BrandRankingsSection({ 
  brands, 
  dateRange, 
  domain 
}: { 
  brands: BrandRanking[]; 
  dateRange: string;
  domain: string;
}) {
  const domainLabel = domain.charAt(0).toUpperCase() + domain.slice(1).replace("-", " ");
  
  return (
    <div className="rounded-xl border border-white/[0.06] bg-[#0a0a0a]/80 backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-1 h-4 rounded-full bg-amber-500/60" />
            <h3 className="text-[15px] font-medium text-white/90 tracking-tight">
              {domainLabel} Brand Rankings
            </h3>
          </div>
          <span className="text-[10px] text-white/30 font-mono">{dateRange}</span>
        </div>
        <p className="text-[11px] text-white/30 mt-1 ml-3">
          Based on social media mentions & engagement
        </p>
      </div>
      
      {/* Rankings List */}
      <div className="px-3 pb-3">
        {brands.map((brand, i) => (
          <div 
            key={i}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors hover:bg-white/[0.02] group",
              i === 0 && "bg-white/[0.02]"
            )}
          >
            {/* Rank Number */}
            <div className={cn(
              "w-7 h-7 rounded-lg flex items-center justify-center text-[13px] font-bold flex-shrink-0",
              i === 0 ? "bg-amber-500/10 text-amber-400/80" :
              i === 1 ? "bg-white/[0.04] text-white/50" :
              i === 2 ? "bg-white/[0.03] text-white/40" :
              "bg-transparent text-white/25"
            )}>
              {brand.rank}
            </div>
            
            {/* Brand Name */}
            <div className="flex-1 min-w-0">
              <p className={cn(
                "text-[14px] font-medium truncate transition-colors",
                i === 0 ? "text-white/90" : "text-white/70 group-hover:text-white/85"
              )}>
                {brand.name}
              </p>
            </div>
            
            {/* Sparkline */}
            <div className="flex-shrink-0 hidden sm:block">
              <MiniSparkline trend={brand.change > 0 ? "up" : brand.change < 0 ? "down" : "flat"} />
            </div>
            
            {/* Mentions */}
            <div className="flex-shrink-0 text-right w-12">
              <span className="text-[11px] text-white/25 font-mono">
                {formatMentions(brand.mentions)}
              </span>
            </div>
            
            {/* Position Change */}
            <div className="flex items-center gap-0.5 flex-shrink-0 w-10 justify-end">
              {brand.change > 0 ? (
                <>
                  <ArrowUp className="w-3 h-3 text-emerald-400/60" />
                  <span className="text-[11px] font-medium text-emerald-400/60">{brand.change}</span>
                </>
              ) : brand.change < 0 ? (
                <>
                  <ArrowDown className="w-3 h-3 text-red-400/60" />
                  <span className="text-[11px] font-medium text-red-400/60">{Math.abs(brand.change)}</span>
                </>
              ) : (
                <Minus className="w-3 h-3 text-white/20" />
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* Footer - Social Platforms */}
      <div className="px-5 py-3 border-t border-white/[0.04]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe className="w-3 h-3 text-white/20" />
            <span className="text-[10px] text-white/20">
              Data from Instagram · TikTok · X · LinkedIn · Pinterest
            </span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400/40 animate-pulse" />
            <span className="text-[9px] text-white/20 font-mono">LIVE</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main DomainTrends Component
// =============================================================================

interface DomainTrendsProps {
  domain: string;
  className?: string;
}

export function DomainTrends({ domain, className }: DomainTrendsProps) {
  const [trendsData, setTrendsData] = useState<TrendsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://web-production-29f3c.up.railway.app";

  const fetchTrends = useCallback(async (forceRefresh = false) => {
    if (domain === "all") return; // No trends for Global domain
    
    try {
      if (forceRefresh) setRefreshing(true);
      else setLoading(true);
      
      const endpoint = forceRefresh 
        ? `${API_BASE}/api/v1/trends/refresh/${domain}`
        : `${API_BASE}/api/v1/trends/${domain}`;
      
      const options: RequestInit = forceRefresh 
        ? { method: "POST", headers: { "Content-Type": "application/json" } }
        : { method: "GET" };
      
      const res = await fetch(endpoint, options);
      
      if (!res.ok) throw new Error(`Failed to fetch trends: ${res.status}`);
      
      const data = await res.json();
      setTrendsData(data);
      setError(null);
    } catch (err: any) {
      console.error("Error fetching trends:", err);
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [domain, API_BASE]);

  useEffect(() => {
    fetchTrends();
  }, [fetchTrends]);

  // Don't render for Global domain
  if (domain === "all") return null;

  // Loading state
  if (loading) {
    return (
      <div className={cn("space-y-4", className)}>
        <div className="rounded-xl border border-white/[0.06] bg-[#0a0a0a]/80 p-6">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-full border-2 border-white/10 border-t-white/40 animate-spin" />
            <span className="text-sm text-white/30">Loading real-time trends...</span>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !trendsData) {
    return (
      <div className={cn("space-y-4", className)}>
        <div className="rounded-xl border border-white/[0.06] bg-[#0a0a0a]/80 p-6">
          <p className="text-sm text-white/30">Unable to load trends. Please try again later.</p>
        </div>
      </div>
    );
  }

  if (!trendsData) return null;

  return (
    <div className={cn("space-y-4", className)}>
      {/* Section Header with Refresh */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-white/20" />
          <span className="text-[12px] font-medium text-white/40 uppercase tracking-wider">
            Real-time Intelligence
          </span>
        </div>
        <button
          onClick={() => fetchTrends(true)}
          disabled={refreshing}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] text-white/30 hover:text-white/50 hover:bg-white/[0.03] transition-all disabled:opacity-50"
        >
          <RefreshCw className={cn("w-3 h-3", refreshing && "animate-spin")} />
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* Trending Tags */}
      <TrendingTagsSection 
        tags={trendsData.trending_tags} 
        dateRange={trendsData.date_range} 
      />

      {/* Brand Rankings */}
      <BrandRankingsSection 
        brands={trendsData.brand_rankings} 
        dateRange={trendsData.date_range}
        domain={trendsData.domain}
      />
    </div>
  );
}
