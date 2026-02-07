"use client";

import { useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSector, Sector, DOMAIN_STARTERS } from "@/contexts/SectorContext";
import { DomainHero } from "@/components/domain/DomainHero";
import { DomainInsights } from "@/components/domain/DomainInsights";
import { DomainModules } from "@/components/domain/DomainModules";
import { WeeklyInsights } from "@/components/domain/WeeklyInsights";
import { WorkspaceNavigation } from "@/components/workspace/WorkspaceNavigation";

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

export default function DomainLandingPage() {
  const params = useParams();
  const router = useRouter();
  const domain = params.domain as string;
  const { currentSector, setSector, getSectorConfig } = useSector();

  // Resolve sector from URL
  const resolvedSector = domain ? slugToSector[domain] : undefined;

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

        {/* Research Modules - Deep dive research tracks */}
        <DomainModules
          sector={currentSector}
          onModuleClick={handlePromptClick}
        />
      </main>
    </div>
  );
}
