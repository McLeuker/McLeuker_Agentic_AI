"use client";

import { useEffect, useCallback, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSector, Sector, DOMAIN_STARTERS } from "@/contexts/SectorContext";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/integrations/supabase/client";
import { DomainHero } from "@/components/domain/DomainHero";
import { DomainInsights } from "@/components/domain/DomainInsights";
import { DomainModules } from "@/components/domain/DomainModules";
import { WeeklyInsights } from "@/components/domain/WeeklyInsights";
import { WorkspaceNavigation } from "@/components/workspace/WorkspaceNavigation";
import { Footer } from "@/components/layout/Footer";
import { MoodBoard } from "@/components/domain/MoodBoard";
import { Lock, ArrowRight } from "lucide-react";
import Link from "next/link";

// Map URL slugs to sector IDs
const slugToSector: Record<string, Sector> = {
  fashion: "fashion",
  beauty: "beauty",
  skincare: "skincare",
  sustainability: "sustainability",
  "fashion-tech": "fashion-tech",
  catwalks: "catwalks",
  culture: "culture",
  textile: "textile",
  lifestyle: "lifestyle",
};

// Domain access by plan — all domains unlocked for all users
const ALL_DOMAINS = ['all', 'fashion', 'beauty', 'skincare', 'sustainability', 'fashion-tech', 'catwalks', 'culture', 'textile', 'lifestyle'];
const DOMAIN_ACCESS: Record<string, string[]> = {
  free: ALL_DOMAINS,
  standard: ALL_DOMAINS,
  pro: ALL_DOMAINS,
  enterprise: ALL_DOMAINS,
};

export default function DomainLandingPage() {
  const params = useParams();
  const router = useRouter();
  const domain = params.domain as string;
  const { currentSector, setSector, getSectorConfig } = useSector();
  const { user } = useAuth();
  const [userPlan, setUserPlan] = useState<string>('free');
  const [checkingAccess, setCheckingAccess] = useState(true);

  // Resolve sector from URL
  const resolvedSector = domain ? slugToSector[domain] : undefined;

  // Fetch user plan
  useEffect(() => {
    const fetchPlan = async () => {
      if (!user) {
        setCheckingAccess(false);
        return;
      }
      try {
        const { data, error } = await supabase
          .from('users')
          .select('subscription_plan')
          .eq('id', user.id)
          .single();
        if (!error && data?.subscription_plan) {
          setUserPlan(data.subscription_plan);
        }
      } catch {
        // Default to free
      }
      setCheckingAccess(false);
    };
    fetchPlan();
  }, [user]);

  // Sync URL param to sector context
  useEffect(() => {
    if (resolvedSector && resolvedSector !== currentSector) {
      setSector(resolvedSector);
    } else if (!resolvedSector && domain) {
      // Invalid domain, redirect to dashboard
      router.push("/dashboard");
    }
  }, [resolvedSector, currentSector, setSector, domain, router]);

  const sectorConfig = getSectorConfig();
  const starters = DOMAIN_STARTERS[currentSector] || [];

  // Check domain access
  const accessibleDomains = DOMAIN_ACCESS[userPlan] || DOMAIN_ACCESS.free;
  const hasAccess = resolvedSector ? accessibleDomains.includes(resolvedSector) : false;

  // Handle module/insight click - navigate to dashboard with pre-filled prompt and auto-execute
  const handlePromptClick = useCallback(
    (prompt: string) => {
      sessionStorage.setItem("domainPrompt", prompt);
      sessionStorage.setItem("domainContext", currentSector);
      sessionStorage.setItem("autoExecute", "true");
      router.push("/dashboard");
    },
    [currentSector, router]
  );

  // Handle ask AI submission - auto-execute on dashboard
  const handleAskSubmit = useCallback(
    (query: string) => {
      sessionStorage.setItem("domainPrompt", query);
      sessionStorage.setItem("domainContext", currentSector);
      sessionStorage.setItem("autoExecute", "true");
      router.push("/dashboard");
    },
    [currentSector, router]
  );

  if (!resolvedSector) {
    return null;
  }

  // Show loading while checking access
  if (checkingAccess) {
    return (
      <div className="min-h-screen bg-[#070707] flex items-center justify-center">
        <div className="w-6 h-6 rounded-full border-2 border-white/10 border-t-white/40 animate-spin" />
      </div>
    );
  }

  // Locked domain — user doesn't have access
  if (!hasAccess) {
    const domainLabel = domain.charAt(0).toUpperCase() + domain.slice(1).replace("-", " ");
    const requiredPlan = ['skincare', 'sustainability', 'fashion-tech'].includes(domain) ? 'Standard' : 'Pro';
    
    return (
      <div className="min-h-screen bg-[#070707] flex flex-col overflow-x-hidden">
        <WorkspaceNavigation showSectorTabs={true} />
        <div className="h-14 lg:h-[72px]" />
        
        <main className="flex-1 flex items-center justify-center px-6">
          <div className="max-w-md w-full text-center">
            <div className="w-16 h-16 rounded-2xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
              <Lock className="w-7 h-7 text-white/30" />
            </div>
            <h1 className="text-2xl md:text-3xl font-serif text-white/90 mb-3">
              {domainLabel} Intelligence
            </h1>
            <p className="text-white/40 text-sm leading-relaxed mb-2">
              This domain requires a <span className="text-white/70 font-medium">{requiredPlan}</span> plan or higher.
            </p>
            <p className="text-white/25 text-xs mb-8">
              Upgrade your plan to unlock {domainLabel.toLowerCase()} intelligence, real-time trends, weekly insights, and AI-powered research modules.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                href="/pricing"
                className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-[#2E3524] text-white text-sm font-medium hover:bg-[#3a4530] transition-colors"
              >
                View Plans
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/dashboard"
                className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/60 text-sm hover:bg-white/[0.08] transition-colors"
              >
                Back to Dashboard
              </Link>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#070707] flex flex-col overflow-x-hidden">
      <WorkspaceNavigation showSectorTabs={true} />
      
      <div className="h-14 lg:h-[72px]" />

      <main className="flex-1 overflow-y-auto">
        {/* Hero Section with integrated search */}
        <DomainHero
          sector={currentSector}
          config={sectorConfig}
          snapshot={null}
          isLoading={false}
          placeholder={sectorConfig.placeholder}
          starters={starters}
          onSubmit={handleAskSubmit}
        />

        {/* What's Happening Now - Real-time live signals */}
        <DomainInsights
          sector={currentSector}
          onSignalClick={handlePromptClick}
        />

        {/* Last Week's Insights - AI-curated weekly intelligence */}
        <WeeklyInsights
          sector={currentSector}
          onInsightClick={handlePromptClick}
        />

        {/* Curated Mood Board - AI-generated visual references */}
        <MoodBoard sector={currentSector} />

        {/* Research Modules - Deep dive research tracks */}
        <DomainModules
          sector={currentSector}
          onModuleClick={handlePromptClick}
        />
      </main>

      {/* Footer for all domain pages */}
      <Footer />
    </div>
  );
}
