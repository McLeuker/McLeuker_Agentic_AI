"use client";

import { Sector } from "@/contexts/SectorContext";
import { RefreshCw, AlertCircle, Signal, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface IntelligenceItem {
  title: string;
  description: string;
  source: string;
  sourceUrl?: string;
  date: string;
  confidence: 'high' | 'medium' | 'low';
  category?: string;
}

interface DomainInsightsProps {
  sector: Sector;
  items: IntelligenceItem[];
  isLoading: boolean;
  error?: string | null;
  source?: 'perplexity' | 'grok' | 'fallback' | null;
  seasonContext?: string | null;
  onRefresh?: () => void;
}

function extractSourceName(sourceStr: string, url?: string): string {
  if (sourceStr && !sourceStr.includes('http') && !sourceStr.includes('.com')) {
    return sourceStr;
  }

  if (!url) return sourceStr || 'Source';

  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.replace('www.', '');
    
    const domainNames: Record<string, string> = {
      'vogue.com': 'Vogue',
      'wwd.com': 'WWD',
      'fashionunited.com': 'Fashion United',
      'fashionunited.uk': 'Fashion United',
      'whowhatwear.com': 'Who What Wear',
      'marieclaire.com': 'Marie Claire',
      'harpersbazaar.com': 'Harper\'s Bazaar',
      'elle.com': 'ELLE',
      'businessoffashion.com': 'BoF',
      'highsnobiety.com': 'Highsnobiety',
      'hypebeast.com': 'Hypebeast',
      'complex.com': 'Complex',
      'refinery29.com': 'Refinery29',
      'glamour.com': 'Glamour',
      'instyle.com': 'InStyle',
      'cosmopolitan.com': 'Cosmopolitan',
      'allure.com': 'Allure',
      'byrdie.com': 'Byrdie',
      'nylon.com': 'NYLON',
      'thecut.com': 'The Cut',
      'gq.com': 'GQ',
      'esquire.com': 'Esquire',
      'forbes.com': 'Forbes',
      'bloomberg.com': 'Bloomberg',
      'reuters.com': 'Reuters',
      'bbc.com': 'BBC',
      'theguardian.com': 'The Guardian',
      'nytimes.com': 'NY Times',
      'wsj.com': 'WSJ',
    };

    if (domainNames[hostname]) {
      return domainNames[hostname];
    }

    for (const [domain, name] of Object.entries(domainNames)) {
      if (hostname.includes(domain.split('.')[0])) {
        return name;
      }
    }

    return hostname
      .split('.')[0]
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  } catch {
    return sourceStr || 'Source';
  }
}

function getConfidenceBadge(confidence: 'high' | 'medium' | 'low') {
  const styles = {
    high: 'bg-[#141414] text-white/[0.78] border-white/[0.12]',
    medium: 'bg-[#141414] text-white/[0.65] border-white/[0.10]',
    low: 'bg-[#141414] text-white/50 border-white/[0.08]',
  };
  return styles[confidence] || styles.medium;
}

// Skeleton component
function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn("animate-pulse rounded-md bg-white/10", className)} />
  );
}

// Badge component
function Badge({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold", className)}>
      {children}
    </span>
  );
}

export function DomainInsights({ 
  sector, 
  items, 
  isLoading, 
  error,
  source,
  seasonContext,
  onRefresh 
}: DomainInsightsProps) {

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) return 'Today';
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays} days ago`;
      
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const displayItems = items.slice(0, 6);

  return (
    <section className="w-full bg-[#0B0B0B]">
      <div className="max-w-[1120px] mx-auto px-7 py-12 md:py-14">
        <div className="flex items-center justify-between mb-10">
          <div className="flex flex-col gap-2">
            <h2 className="font-serif text-2xl md:text-3xl text-white/[0.92]">
              What&apos;s Happening Now
            </h2>
            <div className="flex items-center gap-3">
              {source === 'perplexity' && !isLoading && items.length > 0 && (
                <Badge className="text-[11px] px-2 py-0.5 h-5 bg-[#141414] text-white/[0.78] border-white/[0.12]">
                  <Signal className="h-3 w-3 mr-1.5" />
                  Live
                </Badge>
              )}
              {source === 'fallback' && !isLoading && items.length > 0 && (
                <Badge className="text-[11px] px-2 py-0.5 h-5 bg-[#141414] text-white/[0.65] border-white/[0.10]">
                  <TrendingUp className="h-3 w-3 mr-1.5" />
                  Predictive
                </Badge>
              )}
              {seasonContext && !isLoading && (
                <span className="text-[11px] uppercase tracking-widest text-white/50">
                  {seasonContext}
                </span>
              )}
            </div>
          </div>
          
          {onRefresh && !isLoading && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRefresh}
              className="h-9 px-3 bg-[#141414] border border-white/[0.10] text-white/70 hover:bg-[#1A1A1A] hover:text-white/90 rounded-lg"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              <span className="text-[13px]">Refresh</span>
            </Button>
          )}
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="p-6 rounded-[20px] bg-gradient-to-b from-[#232323] to-[#191919] border border-white/[0.12]">
                <Skeleton className="h-5 w-20 mb-3" />
                <Skeleton className="h-5 w-3/4 mb-3" />
                <Skeleton className="h-4 w-full mb-4" />
                <div className="flex items-center gap-3">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <AlertCircle className="h-10 w-10 text-white/50 mb-4" />
            <p className="text-white/60 text-[15px] mb-6">{error}</p>
            {onRefresh && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onRefresh} 
                className="h-10 px-5 bg-[#141414] border-white/[0.10] text-white/70 hover:bg-[#1A1A1A] hover:text-white"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            )}
          </div>
        ) : items.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayItems.map((item, idx) => (
              <article
                key={idx}
                className={cn(
                  "group p-6 rounded-[20px]",
                  "bg-gradient-to-b from-[#232323] to-[#191919]",
                  "border border-white/[0.12]",
                  "shadow-[0_14px_40px_rgba(0,0,0,0.55)]",
                  "transition-all duration-200",
                  "hover:border-white/[0.18]"
                )}
              >
                <div className="mb-3">
                  <Badge 
                    className={cn(
                      "text-[11px] px-2 py-0.5 h-5",
                      getConfidenceBadge(item.confidence)
                    )}
                  >
                    {item.confidence.charAt(0).toUpperCase() + item.confidence.slice(1)}
                  </Badge>
                </div>
                
                {item.sourceUrl ? (
                  <a
                    href={item.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-base font-medium text-white/[0.92] leading-snug mb-3 hover:underline underline-offset-2 transition-colors"
                  >
                    {item.title}
                  </a>
                ) : (
                  <h3 className="text-base font-medium text-white/[0.92] leading-snug mb-3">
                    {item.title}
                  </h3>
                )}
                
                <p className="text-[15px] text-white/[0.72] leading-relaxed mb-4">
                  {item.description}
                </p>
                
                <div className="text-[13px] text-white/50 mb-1">
                  🕐 {formatDate(item.date)}
                </div>
                
                <div className="text-[13px] text-white/50">
                  {extractSourceName(item.source, item.sourceUrl)}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-white/60 text-[15px]">
              No recent updates found for {sector}. Check back soon!
            </p>
            {onRefresh && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onRefresh} 
                className="mt-6 h-10 px-5 bg-[#141414] border-white/[0.10] text-white/70 hover:bg-[#1A1A1A] hover:text-white"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
