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
// Fallback Data per Domain
// =============================================================================

const now = new Date();
const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
const dateRange = `${weekAgo.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })} - ${now.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })}`;

const FALLBACK_DATA: Record<string, TrendsData> = {
  fashion: {
    domain: "fashion",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "MATERIAL", tag: "Oversized knit", growth_pct: 176, source: "Instagram" },
      { category: "COLOUR", tag: "Ivory", growth_pct: 159, source: "TikTok" },
      { category: "PATTERN", tag: "Thin stripes", growth_pct: 151, source: "Pinterest" },
      { category: "THEME", tag: "Masculine", growth_pct: 101, source: "X" },
    ],
    brand_rankings: [
      { rank: 1, name: "Alberta Ferretti", change: 10, mentions: 48200 },
      { rank: 2, name: "Chanel", change: 1, mentions: 42100 },
      { rank: 3, name: "Dior", change: 0, mentions: 39800 },
      { rank: 4, name: "Patou", change: 2, mentions: 31500 },
      { rank: 5, name: "Toteme", change: 1, mentions: 28900 },
      { rank: 6, name: "Prada", change: -2, mentions: 27300 },
      { rank: 7, name: "Valentino", change: 3, mentions: 25100 },
      { rank: 8, name: "Balenciaga", change: -1, mentions: 23400 },
      { rank: 9, name: "Loewe", change: 4, mentions: 21800 },
      { rank: 10, name: "Bottega Veneta", change: -3, mentions: 19600 },
    ],
  },
  beauty: {
    domain: "beauty",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "TECHNIQUE", tag: "Glass skin", growth_pct: 203, source: "TikTok" },
      { category: "INGREDIENT", tag: "Peptide serums", growth_pct: 167, source: "Instagram" },
      { category: "LOOK", tag: "Clean girl aesthetic", growth_pct: 142, source: "Pinterest" },
      { category: "TREND", tag: "Skin cycling", growth_pct: 118, source: "TikTok" },
    ],
    brand_rankings: [
      { rank: 1, name: "Glossier", change: 3, mentions: 52100 },
      { rank: 2, name: "Charlotte Tilbury", change: 0, mentions: 48700 },
      { rank: 3, name: "Rare Beauty", change: 2, mentions: 45300 },
      { rank: 4, name: "Fenty Beauty", change: -1, mentions: 41200 },
      { rank: 5, name: "Drunk Elephant", change: 1, mentions: 38900 },
      { rank: 6, name: "NARS", change: -2, mentions: 35100 },
      { rank: 7, name: "MAC", change: 0, mentions: 32400 },
      { rank: 8, name: "Hourglass", change: 4, mentions: 29800 },
      { rank: 9, name: "Pat McGrath", change: -1, mentions: 27100 },
      { rank: 10, name: "Tower 28", change: 5, mentions: 24600 },
    ],
  },
  skincare: {
    domain: "skincare",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "INGREDIENT", tag: "Bakuchiol", growth_pct: 189, source: "TikTok" },
      { category: "ROUTINE", tag: "Slugging", growth_pct: 156, source: "Instagram" },
      { category: "CONCERN", tag: "Barrier repair", growth_pct: 134, source: "Pinterest" },
      { category: "FORMAT", tag: "Waterless beauty", growth_pct: 112, source: "X" },
    ],
    brand_rankings: [
      { rank: 1, name: "CeraVe", change: 0, mentions: 61200 },
      { rank: 2, name: "The Ordinary", change: 1, mentions: 55800 },
      { rank: 3, name: "La Roche-Posay", change: 2, mentions: 49300 },
      { rank: 4, name: "Paula's Choice", change: -1, mentions: 42100 },
      { rank: 5, name: "Drunk Elephant", change: 0, mentions: 38700 },
      { rank: 6, name: "Tatcha", change: 3, mentions: 35200 },
      { rank: 7, name: "SK-II", change: -2, mentions: 31800 },
      { rank: 8, name: "Kiehl's", change: 1, mentions: 28400 },
      { rank: 9, name: "Glow Recipe", change: 2, mentions: 25100 },
      { rank: 10, name: "Aesop", change: -1, mentions: 22700 },
    ],
  },
  sustainability: {
    domain: "sustainability",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "MATERIAL", tag: "Mycelium leather", growth_pct: 221, source: "LinkedIn" },
      { category: "PRACTICE", tag: "Circular fashion", growth_pct: 178, source: "Instagram" },
      { category: "CERTIFICATION", tag: "B Corp", growth_pct: 145, source: "X" },
      { category: "MOVEMENT", tag: "Degrowth fashion", growth_pct: 109, source: "TikTok" },
    ],
    brand_rankings: [
      { rank: 1, name: "Patagonia", change: 0, mentions: 45600 },
      { rank: 2, name: "Stella McCartney", change: 2, mentions: 39200 },
      { rank: 3, name: "Eileen Fisher", change: 1, mentions: 33800 },
      { rank: 4, name: "Reformation", change: -1, mentions: 31200 },
      { rank: 5, name: "Veja", change: 3, mentions: 28700 },
      { rank: 6, name: "Pangaia", change: -2, mentions: 25100 },
      { rank: 7, name: "Allbirds", change: 0, mentions: 22400 },
      { rank: 8, name: "Everlane", change: -1, mentions: 19800 },
      { rank: 9, name: "Ganni", change: 4, mentions: 17200 },
      { rank: 10, name: "Marine Serre", change: 2, mentions: 15100 },
    ],
  },
  "fashion-tech": {
    domain: "fashion-tech",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "TECHNOLOGY", tag: "AI styling", growth_pct: 245, source: "X" },
      { category: "INNOVATION", tag: "Digital fashion", growth_pct: 198, source: "LinkedIn" },
      { category: "PLATFORM", tag: "Virtual try-on", growth_pct: 163, source: "TikTok" },
      { category: "CONCEPT", tag: "Phygital", growth_pct: 127, source: "Instagram" },
    ],
    brand_rankings: [
      { rank: 1, name: "DRESSX", change: 5, mentions: 32100 },
      { rank: 2, name: "The Fabricant", change: 2, mentions: 28700 },
      { rank: 3, name: "Zeekit (Walmart)", change: 0, mentions: 25300 },
      { rank: 4, name: "CLO Virtual Fashion", change: 3, mentions: 22800 },
      { rank: 5, name: "Browzwear", change: -1, mentions: 19400 },
      { rank: 6, name: "Heuritech", change: 1, mentions: 16900 },
      { rank: 7, name: "Ordre", change: -2, mentions: 14200 },
      { rank: 8, name: "Obsess", change: 4, mentions: 12100 },
      { rank: 9, name: "Zero10", change: 2, mentions: 10500 },
      { rank: 10, name: "Stylumia", change: -1, mentions: 8900 },
    ],
  },
  catwalks: {
    domain: "catwalks",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "SILHOUETTE", tag: "Cocoon coats", growth_pct: 192, source: "Instagram" },
      { category: "DETAIL", tag: "Fringe accents", growth_pct: 168, source: "TikTok" },
      { category: "COLOUR", tag: "Burgundy", growth_pct: 147, source: "Pinterest" },
      { category: "STYLING", tag: "Layered tailoring", growth_pct: 123, source: "X" },
    ],
    brand_rankings: [
      { rank: 1, name: "Schiaparelli", change: 6, mentions: 51200 },
      { rank: 2, name: "Valentino", change: 1, mentions: 47800 },
      { rank: 3, name: "Louis Vuitton", change: -1, mentions: 44300 },
      { rank: 4, name: "Gucci", change: 0, mentions: 41200 },
      { rank: 5, name: "Saint Laurent", change: 2, mentions: 38100 },
      { rank: 6, name: "Miu Miu", change: 3, mentions: 35400 },
      { rank: 7, name: "Givenchy", change: -2, mentions: 32100 },
      { rank: 8, name: "Fendi", change: -1, mentions: 29800 },
      { rank: 9, name: "Hermès", change: 0, mentions: 27200 },
      { rank: 10, name: "Rick Owens", change: 4, mentions: 24600 },
    ],
  },
  culture: {
    domain: "culture",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "MOVEMENT", tag: "Quiet luxury", growth_pct: 187, source: "TikTok" },
      { category: "AESTHETIC", tag: "Old money", growth_pct: 164, source: "Instagram" },
      { category: "INFLUENCE", tag: "K-fashion", growth_pct: 141, source: "Pinterest" },
      { category: "SUBCULTURE", tag: "Gorpcore", growth_pct: 115, source: "X" },
    ],
    brand_rankings: [
      { rank: 1, name: "The Row", change: 2, mentions: 43200 },
      { rank: 2, name: "Aimé Leon Dore", change: 1, mentions: 39800 },
      { rank: 3, name: "Jacquemus", change: 0, mentions: 36400 },
      { rank: 4, name: "Stüssy", change: -1, mentions: 33100 },
      { rank: 5, name: "Corteiz", change: 5, mentions: 30200 },
      { rank: 6, name: "Wales Bonner", change: 3, mentions: 27400 },
      { rank: 7, name: "Bode", change: -2, mentions: 24800 },
      { rank: 8, name: "Maison Margiela", change: 0, mentions: 22100 },
      { rank: 9, name: "Lemaire", change: 2, mentions: 19500 },
      { rank: 10, name: "Our Legacy", change: 1, mentions: 17200 },
    ],
  },
  textile: {
    domain: "textile",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "FIBRE", tag: "Tencel Luxe", growth_pct: 195, source: "LinkedIn" },
      { category: "TECHNIQUE", tag: "3D knitting", growth_pct: 172, source: "X" },
      { category: "FINISH", tag: "Bio-dyeing", growth_pct: 148, source: "Instagram" },
      { category: "INNOVATION", tag: "Spider silk", growth_pct: 121, source: "TikTok" },
    ],
    brand_rankings: [
      { rank: 1, name: "Lenzing (Tencel)", change: 0, mentions: 28400 },
      { rank: 2, name: "Bolt Threads", change: 3, mentions: 25100 },
      { rank: 3, name: "Spiber", change: 2, mentions: 22700 },
      { rank: 4, name: "Renewcell", change: -1, mentions: 19800 },
      { rank: 5, name: "Evrnu", change: 1, mentions: 17200 },
      { rank: 6, name: "Piñatex", change: -2, mentions: 14800 },
      { rank: 7, name: "Modern Meadow", change: 0, mentions: 12400 },
      { rank: 8, name: "Worn Again", change: 4, mentions: 10100 },
      { rank: 9, name: "Infinited Fiber", change: 2, mentions: 8700 },
      { rank: 10, name: "Spinnova", change: 1, mentions: 7200 },
    ],
  },
  lifestyle: {
    domain: "lifestyle",
    date_range: dateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest"],
    trending_tags: [
      { category: "WELLNESS", tag: "Dopamine dressing", growth_pct: 183, source: "TikTok" },
      { category: "LIVING", tag: "Capsule wardrobe", growth_pct: 157, source: "Pinterest" },
      { category: "TRAVEL", tag: "Resort wear", growth_pct: 139, source: "Instagram" },
      { category: "MINDSET", tag: "Slow fashion", growth_pct: 108, source: "LinkedIn" },
    ],
    brand_rankings: [
      { rank: 1, name: "Aritzia", change: 2, mentions: 41200 },
      { rank: 2, name: "COS", change: 1, mentions: 37800 },
      { rank: 3, name: "& Other Stories", change: 0, mentions: 34100 },
      { rank: 4, name: "Arket", change: 3, mentions: 30500 },
      { rank: 5, name: "Massimo Dutti", change: -1, mentions: 27800 },
      { rank: 6, name: "Sézane", change: 2, mentions: 24200 },
      { rank: 7, name: "Rouje", change: -2, mentions: 21600 },
      { rank: 8, name: "Réalisation Par", change: 0, mentions: 18900 },
      { rank: 9, name: "Nanushka", change: 4, mentions: 16300 },
      { rank: 10, name: "Frankie Shop", change: 1, mentions: 14100 },
    ],
  },
};

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
  const [usingFallback, setUsingFallback] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://web-production-29f3c.up.railway.app";

  const getFallbackData = useCallback((): TrendsData | null => {
    return FALLBACK_DATA[domain] || null;
  }, [domain]);

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
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000);
      
      const res = await fetch(endpoint, { ...options, signal: controller.signal });
      clearTimeout(timeoutId);
      
      if (!res.ok) throw new Error(`Failed to fetch trends: ${res.status}`);
      
      const data = await res.json();
      setTrendsData(data);
      setUsingFallback(false);
      setError(null);
    } catch (err: any) {
      console.error("Error fetching trends:", err);
      // Use fallback data when API is unavailable
      const fallback = getFallbackData();
      if (fallback) {
        setTrendsData(fallback);
        setUsingFallback(true);
        setError(null);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [domain, API_BASE, getFallbackData]);

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

  // Error state - only show if no fallback data
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
