"use client";

import { useEffect, useCallback, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSector, Sector, DOMAIN_STARTERS } from "@/contexts/SectorContext";
import { DomainHero } from "@/components/domain/DomainHero";
import { DomainInsights, IntelligenceItem } from "@/components/domain/DomainInsights";
import { DomainModules } from "@/components/domain/DomainModules";
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

// Sample intelligence items for demo
const getSampleIntelligence = (sector: Sector): IntelligenceItem[] => {
  const baseItems: IntelligenceItem[] = [
    {
      title: "Emerging trends signal shift in consumer preferences",
      description: "Industry analysts report significant changes in how consumers approach purchasing decisions in this sector.",
      source: "Industry Report",
      date: new Date().toISOString(),
      confidence: "high",
    },
    {
      title: "Major brands announce sustainability initiatives",
      description: "Leading companies are committing to new environmental standards and transparency measures.",
      source: "Business News",
      date: new Date(Date.now() - 86400000).toISOString(),
      confidence: "high",
    },
    {
      title: "Technology adoption accelerates across the industry",
      description: "Digital transformation continues to reshape operations and customer experiences.",
      source: "Tech Analysis",
      date: new Date(Date.now() - 172800000).toISOString(),
      confidence: "medium",
    },
  ];

  return baseItems;
};

export default function DomainLandingPage() {
  const params = useParams();
  const router = useRouter();
  const domain = params.domain as string;
  const { currentSector, setSector, getSectorConfig } = useSector();
  const [intelligenceItems, setIntelligenceItems] = useState<IntelligenceItem[]>([]);
  const [intelligenceLoading, setIntelligenceLoading] = useState(true);

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

  // Fetch intelligence on mount/domain change
  useEffect(() => {
    if (resolvedSector) {
      setIntelligenceLoading(true);
      // Simulate API call
      setTimeout(() => {
        setIntelligenceItems(getSampleIntelligence(resolvedSector));
        setIntelligenceLoading(false);
      }, 1000);
    }
  }, [resolvedSector]);

  const sectorConfig = getSectorConfig();
  const starters = DOMAIN_STARTERS[currentSector] || [];

  // Handle refresh
  const handleRefresh = useCallback(() => {
    if (resolvedSector) {
      setIntelligenceLoading(true);
      setTimeout(() => {
        setIntelligenceItems(getSampleIntelligence(resolvedSector));
        setIntelligenceLoading(false);
      }, 1000);
    }
  }, [resolvedSector]);

  // Handle module click - navigate to dashboard with pre-filled prompt and auto-execute
  const handleModuleClick = useCallback(
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

        {/* What's Happening Now - Real-time Intelligence */}
        <DomainInsights
          sector={currentSector}
          items={intelligenceItems}
          isLoading={intelligenceLoading}
          error={null}
          source="fallback"
          seasonContext="SS26"
          onRefresh={handleRefresh}
        />

        {/* Intelligence Modules */}
        <DomainModules
          sector={currentSector}
          onModuleClick={handleModuleClick}
        />
      </main>
    </div>
  );
}
