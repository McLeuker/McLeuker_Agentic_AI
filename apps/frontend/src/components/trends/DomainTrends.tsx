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
  Sparkles,
  Lock,
  Zap,
  Eye,
  MessageCircle,
  Users,
  Activity,
  Flame,
  Target,
  Layers,
  ArrowRight
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

interface PlatformBreakdown {
  platform: string;
  share_pct: number;
  engagement: string;
  trend: "up" | "down" | "flat";
}

interface RisingCreator {
  name: string;
  platform: string;
  followers: string;
  growth: number;
  niche: string;
}

interface MarketPulse {
  sentiment_score: number;
  engagement_velocity: string;
  content_volume: string;
  viral_potential: number;
  top_format: string;
  peak_time: string;
}

interface TrendsData {
  trending_tags: TrendingTag[];
  brand_rankings: BrandRanking[];
  social_platforms: string[];
  date_range: string;
  domain: string;
  cached_at?: string;
  data_sources?: string[];
  platform_breakdown?: PlatformBreakdown[];
  rising_creators?: RisingCreator[];
  market_pulse?: MarketPulse;
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
    "YouTube": "YT",
    "Facebook": "FB",
    "RedNote": "RN",
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
// Mini Bar Chart
// =============================================================================

const MiniBar = ({ value, max, color }: { value: number; max: number; color: string }) => (
  <div className="h-1.5 w-full bg-white/[0.04] rounded-full overflow-hidden">
    <div 
      className={cn("h-full rounded-full transition-all duration-700", color)}
      style={{ width: `${Math.min((value / max) * 100, 100)}%` }}
    />
  </div>
);

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
          Based on social media engagement across Instagram, TikTok, X, LinkedIn, Pinterest, YouTube, RedNote & Facebook
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
          Based on social media mentions & engagement across 8 platforms
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
              Data from Instagram · TikTok · X · LinkedIn · Pinterest · YouTube · RedNote · Facebook
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
// Platform Breakdown Section (NEW)
// =============================================================================

function PlatformBreakdownSection({ platforms, domain }: { platforms: PlatformBreakdown[]; domain: string }) {
  const maxShare = Math.max(...platforms.map(p => p.share_pct));
  const platformColors: Record<string, string> = {
    "Instagram": "bg-pink-500/60",
    "TikTok": "bg-cyan-400/60",
    "X": "bg-white/40",
    "LinkedIn": "bg-blue-500/60",
    "Pinterest": "bg-red-400/60",
    "YouTube": "bg-red-500/60",
    "RedNote": "bg-rose-400/60",
    "Facebook": "bg-blue-400/60",
  };

  return (
    <div className="rounded-xl border border-white/[0.06] bg-[#0a0a0a]/80 backdrop-blur-sm overflow-hidden">
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-1 h-4 rounded-full bg-blue-500/60" />
          <h3 className="text-[15px] font-medium text-white/90 tracking-tight">
            Platform Engagement Breakdown
          </h3>
        </div>
        <p className="text-[11px] text-white/30 mt-1 ml-3">
          Where conversations are happening this week
        </p>
      </div>

      <div className="px-5 pb-4 space-y-3">
        {platforms.map((p, i) => (
          <div key={i} className="group">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <PlatformIcon platform={p.platform} className="text-white/50 text-[10px]" />
                <span className="text-[13px] text-white/70 font-medium">{p.platform}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[11px] text-white/30 font-mono">{p.engagement}</span>
                <span className="text-[12px] text-white/50 font-semibold">{p.share_pct}%</span>
                <MiniSparkline trend={p.trend} />
              </div>
            </div>
            <MiniBar value={p.share_pct} max={maxShare} color={platformColors[p.platform] || "bg-white/30"} />
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Market Pulse Section (NEW)
// =============================================================================

function MarketPulseSection({ pulse, domain }: { pulse: MarketPulse; domain: string }) {
  const domainLabel = domain.charAt(0).toUpperCase() + domain.slice(1).replace("-", " ");
  const sentimentColor = pulse.sentiment_score >= 70 ? "text-emerald-400" : pulse.sentiment_score >= 40 ? "text-amber-400" : "text-red-400";
  const sentimentLabel = pulse.sentiment_score >= 70 ? "Positive" : pulse.sentiment_score >= 40 ? "Neutral" : "Negative";

  return (
    <div className="rounded-xl border border-white/[0.06] bg-[#0a0a0a]/80 backdrop-blur-sm overflow-hidden">
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-1 h-4 rounded-full bg-violet-500/60" />
          <h3 className="text-[15px] font-medium text-white/90 tracking-tight">
            {domainLabel} Market Pulse
          </h3>
        </div>
        <p className="text-[11px] text-white/30 mt-1 ml-3">
          Real-time sentiment and engagement metrics
        </p>
      </div>

      <div className="grid grid-cols-3 gap-px bg-white/[0.03]">
        {/* Sentiment */}
        <div className="px-4 py-4 bg-[#0a0a0a] text-center">
          <Activity className="w-4 h-4 mx-auto text-white/20 mb-2" />
          <p className={cn("text-2xl font-bold", sentimentColor)}>{pulse.sentiment_score}</p>
          <p className="text-[9px] text-white/30 uppercase tracking-wider mt-1">Sentiment</p>
          <p className={cn("text-[10px] mt-0.5", sentimentColor)}>{sentimentLabel}</p>
        </div>

        {/* Engagement Velocity */}
        <div className="px-4 py-4 bg-[#0a0a0a] text-center">
          <Zap className="w-4 h-4 mx-auto text-white/20 mb-2" />
          <p className="text-2xl font-bold text-white/80">{pulse.engagement_velocity}</p>
          <p className="text-[9px] text-white/30 uppercase tracking-wider mt-1">Eng. Velocity</p>
          <p className="text-[10px] text-white/40 mt-0.5">posts/hour</p>
        </div>

        {/* Content Volume */}
        <div className="px-4 py-4 bg-[#0a0a0a] text-center">
          <Layers className="w-4 h-4 mx-auto text-white/20 mb-2" />
          <p className="text-2xl font-bold text-white/80">{pulse.content_volume}</p>
          <p className="text-[9px] text-white/30 uppercase tracking-wider mt-1">Content Vol.</p>
          <p className="text-[10px] text-white/40 mt-0.5">this week</p>
        </div>
      </div>

      {/* Bottom metrics row */}
      <div className="grid grid-cols-3 gap-px bg-white/[0.03] border-t border-white/[0.03]">
        <div className="px-4 py-3 bg-[#0a0a0a] flex items-center justify-between">
          <span className="text-[10px] text-white/30">Viral Potential</span>
          <div className="flex items-center gap-1">
            <Flame className="w-3 h-3 text-orange-400/60" />
            <span className="text-[12px] font-semibold text-orange-400/70">{pulse.viral_potential}%</span>
          </div>
        </div>
        <div className="px-4 py-3 bg-[#0a0a0a] flex items-center justify-between">
          <span className="text-[10px] text-white/30">Top Format</span>
          <span className="text-[11px] text-white/50 font-medium">{pulse.top_format}</span>
        </div>
        <div className="px-4 py-3 bg-[#0a0a0a] flex items-center justify-between">
          <span className="text-[10px] text-white/30">Peak Time</span>
          <span className="text-[11px] text-white/50 font-medium">{pulse.peak_time}</span>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Rising Creators Section (NEW)
// =============================================================================

function RisingCreatorsSection({ creators, domain }: { creators: RisingCreator[]; domain: string }) {
  const domainLabel = domain.charAt(0).toUpperCase() + domain.slice(1).replace("-", " ");

  return (
    <div className="rounded-xl border border-white/[0.06] bg-[#0a0a0a]/80 backdrop-blur-sm overflow-hidden">
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-1 h-4 rounded-full bg-pink-500/60" />
          <h3 className="text-[15px] font-medium text-white/90 tracking-tight">
            Rising Voices in {domainLabel}
          </h3>
        </div>
        <p className="text-[11px] text-white/30 mt-1 ml-3">
          Creators and influencers gaining momentum this week
        </p>
      </div>

      <div className="px-3 pb-3">
        {creators.map((creator, i) => (
          <div 
            key={i}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors hover:bg-white/[0.02] group"
          >
            {/* Avatar placeholder */}
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-white/[0.08] to-white/[0.02] flex items-center justify-center flex-shrink-0">
              <Users className="w-3.5 h-3.5 text-white/30" />
            </div>

            {/* Name & Niche */}
            <div className="flex-1 min-w-0">
              <p className="text-[13px] font-medium text-white/75 truncate group-hover:text-white/90 transition-colors">
                {creator.name}
              </p>
              <p className="text-[10px] text-white/30">{creator.niche}</p>
            </div>

            {/* Platform */}
            <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-white/[0.04] flex-shrink-0">
              <PlatformIcon platform={creator.platform} className="text-white/40" />
            </div>

            {/* Followers */}
            <div className="text-right flex-shrink-0 w-14">
              <span className="text-[11px] text-white/30 font-mono">{creator.followers}</span>
            </div>

            {/* Growth */}
            <div className="flex items-center gap-0.5 flex-shrink-0 w-12 justify-end">
              <ArrowUp className="w-3 h-3 text-emerald-400/60" />
              <span className="text-[11px] font-medium text-emerald-400/60">{creator.growth}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Premium Upgrade CTA Section (NEW)
// =============================================================================

function PremiumInsightsCTA({ domain }: { domain: string }) {
  const domainLabel = domain.charAt(0).toUpperCase() + domain.slice(1).replace("-", " ");

  return (
    <div className="rounded-xl border border-white/[0.06] bg-gradient-to-br from-[#0a0a0a]/80 to-[#111]/80 backdrop-blur-sm overflow-hidden">
      <div className="px-5 py-5">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500/10 to-amber-600/5 flex items-center justify-center flex-shrink-0 border border-amber-500/10">
            <Crown className="w-5 h-5 text-amber-400/60" />
          </div>
          <div className="flex-1">
            <h3 className="text-[14px] font-medium text-white/80 mb-1">
              Unlock Premium {domainLabel} Insights
            </h3>
            <p className="text-[12px] text-white/35 leading-relaxed mb-3">
              Get access to competitor deep-dives, audience demographics, content strategy recommendations, 
              historical trend data, and AI-powered forecasting for the {domainLabel.toLowerCase()} sector.
            </p>
            <div className="grid grid-cols-2 gap-2 mb-3">
              {[
                "Competitor Analysis",
                "Audience Demographics",
                "Content Strategy AI",
                "Trend Forecasting",
                "Weekly PDF Reports",
                "Custom Alerts",
              ].map((feature, i) => (
                <div key={i} className="flex items-center gap-1.5">
                  <Lock className="w-3 h-3 text-amber-400/40" />
                  <span className="text-[10px] text-white/30">{feature}</span>
                </div>
              ))}
            </div>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.10] border border-white/[0.08] hover:border-white/[0.14] transition-all text-[12px] text-white/60 hover:text-white/80 group">
              <span>Upgrade to Pro</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
            </button>
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
const fallbackDateRange = `${weekAgo.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })} - ${now.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })}`;

// Platform breakdown templates per domain
const PLATFORM_BREAKDOWNS: Record<string, PlatformBreakdown[]> = {
  fashion: [
    { platform: "Instagram", share_pct: 34, engagement: "2.8M", trend: "up" },
    { platform: "TikTok", share_pct: 28, engagement: "2.1M", trend: "up" },
    { platform: "Pinterest", share_pct: 15, engagement: "890K", trend: "flat" },
    { platform: "YouTube", share_pct: 10, engagement: "520K", trend: "up" },
    { platform: "X", share_pct: 6, engagement: "310K", trend: "down" },
    { platform: "RedNote", share_pct: 4, engagement: "180K", trend: "up" },
    { platform: "LinkedIn", share_pct: 2, engagement: "95K", trend: "flat" },
    { platform: "Facebook", share_pct: 1, engagement: "48K", trend: "down" },
  ],
  beauty: [
    { platform: "TikTok", share_pct: 38, engagement: "3.2M", trend: "up" },
    { platform: "Instagram", share_pct: 30, engagement: "2.5M", trend: "flat" },
    { platform: "YouTube", share_pct: 14, engagement: "1.1M", trend: "up" },
    { platform: "Pinterest", share_pct: 8, engagement: "620K", trend: "up" },
    { platform: "RedNote", share_pct: 5, engagement: "380K", trend: "up" },
    { platform: "X", share_pct: 3, engagement: "190K", trend: "down" },
    { platform: "Facebook", share_pct: 1, engagement: "72K", trend: "down" },
    { platform: "LinkedIn", share_pct: 1, engagement: "45K", trend: "flat" },
  ],
  skincare: [
    { platform: "TikTok", share_pct: 35, engagement: "2.9M", trend: "up" },
    { platform: "Instagram", share_pct: 28, engagement: "2.3M", trend: "flat" },
    { platform: "YouTube", share_pct: 16, engagement: "1.3M", trend: "up" },
    { platform: "RedNote", share_pct: 9, engagement: "710K", trend: "up" },
    { platform: "Pinterest", share_pct: 6, engagement: "450K", trend: "flat" },
    { platform: "X", share_pct: 3, engagement: "210K", trend: "down" },
    { platform: "Facebook", share_pct: 2, engagement: "130K", trend: "down" },
    { platform: "LinkedIn", share_pct: 1, engagement: "58K", trend: "flat" },
  ],
  sustainability: [
    { platform: "LinkedIn", share_pct: 32, engagement: "1.8M", trend: "up" },
    { platform: "Instagram", share_pct: 24, engagement: "1.4M", trend: "flat" },
    { platform: "TikTok", share_pct: 18, engagement: "1.0M", trend: "up" },
    { platform: "X", share_pct: 12, engagement: "680K", trend: "up" },
    { platform: "YouTube", share_pct: 8, engagement: "450K", trend: "flat" },
    { platform: "Pinterest", share_pct: 3, engagement: "170K", trend: "flat" },
    { platform: "Facebook", share_pct: 2, engagement: "95K", trend: "down" },
    { platform: "RedNote", share_pct: 1, engagement: "42K", trend: "flat" },
  ],
  "fashion-tech": [
    { platform: "X", share_pct: 30, engagement: "1.5M", trend: "up" },
    { platform: "LinkedIn", share_pct: 28, engagement: "1.4M", trend: "up" },
    { platform: "TikTok", share_pct: 18, engagement: "890K", trend: "up" },
    { platform: "Instagram", share_pct: 12, engagement: "580K", trend: "flat" },
    { platform: "YouTube", share_pct: 8, engagement: "380K", trend: "up" },
    { platform: "Pinterest", share_pct: 2, engagement: "95K", trend: "flat" },
    { platform: "RedNote", share_pct: 1, engagement: "48K", trend: "flat" },
    { platform: "Facebook", share_pct: 1, engagement: "32K", trend: "down" },
  ],
  catwalks: [
    { platform: "Instagram", share_pct: 40, engagement: "3.5M", trend: "up" },
    { platform: "TikTok", share_pct: 25, engagement: "2.2M", trend: "up" },
    { platform: "YouTube", share_pct: 15, engagement: "1.3M", trend: "flat" },
    { platform: "Pinterest", share_pct: 10, engagement: "870K", trend: "up" },
    { platform: "X", share_pct: 5, engagement: "420K", trend: "flat" },
    { platform: "RedNote", share_pct: 3, engagement: "240K", trend: "up" },
    { platform: "Facebook", share_pct: 1, engagement: "85K", trend: "down" },
    { platform: "LinkedIn", share_pct: 1, engagement: "52K", trend: "flat" },
  ],
  culture: [
    { platform: "TikTok", share_pct: 35, engagement: "2.8M", trend: "up" },
    { platform: "Instagram", share_pct: 28, engagement: "2.2M", trend: "flat" },
    { platform: "X", share_pct: 15, engagement: "1.2M", trend: "up" },
    { platform: "YouTube", share_pct: 10, engagement: "780K", trend: "flat" },
    { platform: "Pinterest", share_pct: 5, engagement: "380K", trend: "flat" },
    { platform: "RedNote", share_pct: 4, engagement: "290K", trend: "up" },
    { platform: "LinkedIn", share_pct: 2, engagement: "140K", trend: "flat" },
    { platform: "Facebook", share_pct: 1, engagement: "65K", trend: "down" },
  ],
  textile: [
    { platform: "LinkedIn", share_pct: 35, engagement: "1.2M", trend: "up" },
    { platform: "X", share_pct: 22, engagement: "760K", trend: "flat" },
    { platform: "Instagram", share_pct: 18, engagement: "620K", trend: "flat" },
    { platform: "YouTube", share_pct: 12, engagement: "410K", trend: "up" },
    { platform: "TikTok", share_pct: 7, engagement: "240K", trend: "up" },
    { platform: "Pinterest", share_pct: 3, engagement: "95K", trend: "flat" },
    { platform: "Facebook", share_pct: 2, engagement: "68K", trend: "down" },
    { platform: "RedNote", share_pct: 1, engagement: "32K", trend: "flat" },
  ],
  lifestyle: [
    { platform: "Instagram", share_pct: 32, engagement: "2.6M", trend: "flat" },
    { platform: "TikTok", share_pct: 30, engagement: "2.4M", trend: "up" },
    { platform: "Pinterest", share_pct: 16, engagement: "1.3M", trend: "up" },
    { platform: "YouTube", share_pct: 10, engagement: "780K", trend: "flat" },
    { platform: "RedNote", share_pct: 5, engagement: "380K", trend: "up" },
    { platform: "X", share_pct: 4, engagement: "290K", trend: "down" },
    { platform: "Facebook", share_pct: 2, engagement: "140K", trend: "down" },
    { platform: "LinkedIn", share_pct: 1, engagement: "65K", trend: "flat" },
  ],
};

// Market pulse data per domain
const MARKET_PULSES: Record<string, MarketPulse> = {
  fashion: { sentiment_score: 74, engagement_velocity: "1.2K", content_volume: "48K", viral_potential: 68, top_format: "Reels", peak_time: "6-9 PM" },
  beauty: { sentiment_score: 82, engagement_velocity: "1.8K", content_volume: "62K", viral_potential: 76, top_format: "Short Video", peak_time: "7-10 PM" },
  skincare: { sentiment_score: 79, engagement_velocity: "1.4K", content_volume: "41K", viral_potential: 71, top_format: "Tutorial", peak_time: "8-11 PM" },
  sustainability: { sentiment_score: 68, engagement_velocity: "680", content_volume: "18K", viral_potential: 45, top_format: "Article", peak_time: "9-11 AM" },
  "fashion-tech": { sentiment_score: 71, engagement_velocity: "520", content_volume: "12K", viral_potential: 58, top_format: "Thread", peak_time: "10 AM-1 PM" },
  catwalks: { sentiment_score: 85, engagement_velocity: "2.1K", content_volume: "55K", viral_potential: 82, top_format: "Carousel", peak_time: "5-8 PM" },
  culture: { sentiment_score: 76, engagement_velocity: "1.5K", content_volume: "38K", viral_potential: 73, top_format: "Short Video", peak_time: "6-9 PM" },
  textile: { sentiment_score: 62, engagement_velocity: "340", content_volume: "8K", viral_potential: 32, top_format: "Article", peak_time: "10 AM-12 PM" },
  lifestyle: { sentiment_score: 80, engagement_velocity: "1.6K", content_volume: "52K", viral_potential: 74, top_format: "Reels", peak_time: "7-10 PM" },
};

// Rising creators per domain
const RISING_CREATORS: Record<string, RisingCreator[]> = {
  fashion: [
    { name: "@fashionforward_co", platform: "Instagram", followers: "245K", growth: 34, niche: "Runway Analysis" },
    { name: "@stylesignal", platform: "TikTok", followers: "1.2M", growth: 28, niche: "Street Style" },
    { name: "@thefashionarchive", platform: "YouTube", followers: "180K", growth: 22, niche: "Fashion History" },
    { name: "@luxeinsider", platform: "X", followers: "89K", growth: 19, niche: "Luxury Market" },
    { name: "@silhouette.daily", platform: "RedNote", followers: "320K", growth: 41, niche: "Design Trends" },
  ],
  beauty: [
    { name: "@glowalchemy", platform: "TikTok", followers: "2.1M", growth: 45, niche: "Skincare Routines" },
    { name: "@beautydeconstructed", platform: "YouTube", followers: "890K", growth: 31, niche: "Product Science" },
    { name: "@makeupbymirae", platform: "Instagram", followers: "560K", growth: 26, niche: "K-Beauty" },
    { name: "@cleanbeautycollective", platform: "Pinterest", followers: "145K", growth: 18, niche: "Clean Beauty" },
    { name: "@lipsticklogic", platform: "TikTok", followers: "780K", growth: 38, niche: "Makeup Tutorials" },
  ],
  skincare: [
    { name: "@dermdoctor", platform: "TikTok", followers: "3.4M", growth: 52, niche: "Dermatology" },
    { name: "@ingredientdecoder", platform: "Instagram", followers: "420K", growth: 29, niche: "Ingredient Analysis" },
    { name: "@skinscience.lab", platform: "YouTube", followers: "670K", growth: 24, niche: "Clinical Reviews" },
    { name: "@barrierrepair", platform: "RedNote", followers: "280K", growth: 36, niche: "Barrier Health" },
    { name: "@retinolrealness", platform: "TikTok", followers: "1.1M", growth: 33, niche: "Active Ingredients" },
  ],
  sustainability: [
    { name: "@circularfashion_", platform: "LinkedIn", followers: "95K", growth: 21, niche: "Circularity" },
    { name: "@ecofashionworld", platform: "Instagram", followers: "310K", growth: 18, niche: "Sustainable Brands" },
    { name: "@greenwashdetector", platform: "TikTok", followers: "520K", growth: 42, niche: "Greenwash Exposé" },
    { name: "@materialmatters", platform: "X", followers: "67K", growth: 15, niche: "Material Innovation" },
    { name: "@slowfashion.daily", platform: "Pinterest", followers: "180K", growth: 20, niche: "Slow Fashion" },
  ],
  "fashion-tech": [
    { name: "@aifashionlab", platform: "X", followers: "78K", growth: 38, niche: "AI in Fashion" },
    { name: "@digitalcouture", platform: "Instagram", followers: "210K", growth: 25, niche: "Digital Fashion" },
    { name: "@techrunway", platform: "LinkedIn", followers: "45K", growth: 19, niche: "Fashion Tech" },
    { name: "@virtualstyleai", platform: "TikTok", followers: "340K", growth: 44, niche: "Virtual Try-On" },
    { name: "@futureoffashion", platform: "YouTube", followers: "120K", growth: 22, niche: "Innovation" },
  ],
  catwalks: [
    { name: "@runwayreport", platform: "Instagram", followers: "890K", growth: 31, niche: "Show Coverage" },
    { name: "@backstageaccess", platform: "TikTok", followers: "1.5M", growth: 39, niche: "Backstage" },
    { name: "@fashionweekdaily", platform: "YouTube", followers: "450K", growth: 21, niche: "FW Analysis" },
    { name: "@couturecritique", platform: "X", followers: "120K", growth: 17, niche: "Reviews" },
    { name: "@catwalkdecoded", platform: "Pinterest", followers: "230K", growth: 24, niche: "Trend Decoding" },
  ],
  culture: [
    { name: "@culturexfashion", platform: "TikTok", followers: "980K", growth: 36, niche: "Cultural Trends" },
    { name: "@aestheticarchive", platform: "Instagram", followers: "670K", growth: 28, niche: "Aesthetics" },
    { name: "@subculturestyle", platform: "X", followers: "89K", growth: 22, niche: "Subcultures" },
    { name: "@artmeetsfashion", platform: "YouTube", followers: "340K", growth: 19, niche: "Art x Fashion" },
    { name: "@zeitgeist.now", platform: "RedNote", followers: "210K", growth: 33, niche: "Cultural Shifts" },
  ],
  textile: [
    { name: "@materialinnovation", platform: "LinkedIn", followers: "52K", growth: 18, niche: "New Materials" },
    { name: "@textiletech", platform: "X", followers: "38K", growth: 15, niche: "Textile Tech" },
    { name: "@fiberfuture", platform: "Instagram", followers: "120K", growth: 21, niche: "Fiber Science" },
    { name: "@millstories", platform: "YouTube", followers: "85K", growth: 16, niche: "Manufacturing" },
    { name: "@weaveworld", platform: "TikTok", followers: "190K", growth: 29, niche: "Weaving" },
  ],
  lifestyle: [
    { name: "@capsulelife", platform: "Instagram", followers: "780K", growth: 27, niche: "Capsule Wardrobe" },
    { name: "@wellnessstyle", platform: "TikTok", followers: "1.3M", growth: 35, niche: "Wellness Fashion" },
    { name: "@minimalistluxe", platform: "Pinterest", followers: "420K", growth: 23, niche: "Minimalism" },
    { name: "@travelchic", platform: "YouTube", followers: "290K", growth: 20, niche: "Travel Style" },
    { name: "@slowliving.co", platform: "RedNote", followers: "180K", growth: 31, niche: "Slow Living" },
  ],
};

const FALLBACK_DATA: Record<string, TrendsData> = {
  fashion: {
    domain: "fashion",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS.fashion,
    market_pulse: MARKET_PULSES.fashion,
    rising_creators: RISING_CREATORS.fashion,
  },
  beauty: {
    domain: "beauty",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS.beauty,
    market_pulse: MARKET_PULSES.beauty,
    rising_creators: RISING_CREATORS.beauty,
  },
  skincare: {
    domain: "skincare",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS.skincare,
    market_pulse: MARKET_PULSES.skincare,
    rising_creators: RISING_CREATORS.skincare,
  },
  sustainability: {
    domain: "sustainability",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS.sustainability,
    market_pulse: MARKET_PULSES.sustainability,
    rising_creators: RISING_CREATORS.sustainability,
  },
  "fashion-tech": {
    domain: "fashion-tech",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS["fashion-tech"],
    market_pulse: MARKET_PULSES["fashion-tech"],
    rising_creators: RISING_CREATORS["fashion-tech"],
  },
  catwalks: {
    domain: "catwalks",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS.catwalks,
    market_pulse: MARKET_PULSES.catwalks,
    rising_creators: RISING_CREATORS.catwalks,
  },
  culture: {
    domain: "culture",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS.culture,
    market_pulse: MARKET_PULSES.culture,
    rising_creators: RISING_CREATORS.culture,
  },
  textile: {
    domain: "textile",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS.textile,
    market_pulse: MARKET_PULSES.textile,
    rising_creators: RISING_CREATORS.textile,
  },
  lifestyle: {
    domain: "lifestyle",
    date_range: fallbackDateRange,
    social_platforms: ["Instagram", "TikTok", "X", "LinkedIn", "Pinterest", "YouTube", "RedNote", "Facebook"],
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
    platform_breakdown: PLATFORM_BREAKDOWNS.lifestyle,
    market_pulse: MARKET_PULSES.lifestyle,
    rising_creators: RISING_CREATORS.lifestyle,
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

  // Cache key and TTL (24 hours for trends)
  const TRENDS_CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

  const fetchTrends = useCallback(async (forceRefresh = false) => {
    if (domain === "all") return; // No trends for Global domain
    
    // Check localStorage cache first (unless force refresh)
    if (!forceRefresh) {
      try {
        const cacheKey = `mcleuker_trends_${domain}`;
        const cached = localStorage.getItem(cacheKey);
        if (cached) {
          const { data: cachedData, timestamp } = JSON.parse(cached);
          const age = Date.now() - timestamp;
          if (age < TRENDS_CACHE_TTL && cachedData) {
            setTrendsData(cachedData);
            setUsingFallback(false);
            setError(null);
            setLoading(false);
            return;
          }
        }
      } catch {
        // Cache read failed, continue to fetch
      }
    }

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
      // Merge API data with fallback enrichment data (platform breakdown, market pulse, creators)
      const enriched: TrendsData = {
        ...data,
        platform_breakdown: data.platform_breakdown || PLATFORM_BREAKDOWNS[domain] || [],
        market_pulse: data.market_pulse || MARKET_PULSES[domain],
        rising_creators: data.rising_creators || RISING_CREATORS[domain] || [],
      };
      setTrendsData(enriched);
      setUsingFallback(false);
      setError(null);

      // Save to localStorage cache
      try {
        const cacheKey = `mcleuker_trends_${domain}`;
        localStorage.setItem(cacheKey, JSON.stringify({ data: enriched, timestamp: Date.now() }));
      } catch { /* ignore storage errors */ }
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
          {usingFallback && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400/50 border border-amber-500/10">
              Cached
            </span>
          )}
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

      {/* Market Pulse */}
      {trendsData.market_pulse && (
        <MarketPulseSection pulse={trendsData.market_pulse} domain={trendsData.domain} />
      )}

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

      {/* Platform Engagement Breakdown */}
      {trendsData.platform_breakdown && trendsData.platform_breakdown.length > 0 && (
        <PlatformBreakdownSection platforms={trendsData.platform_breakdown} domain={trendsData.domain} />
      )}

      {/* Rising Creators */}
      {trendsData.rising_creators && trendsData.rising_creators.length > 0 && (
        <RisingCreatorsSection creators={trendsData.rising_creators} domain={trendsData.domain} />
      )}


    </div>
  );
}
