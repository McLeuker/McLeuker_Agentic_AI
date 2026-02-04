"use client";

import { createContext, useContext, useState, ReactNode, useCallback } from "react";

export type Sector = 
  | "all"
  | "fashion"
  | "beauty"
  | "skincare"
  | "sustainability"
  | "fashion-tech"
  | "catwalks"
  | "culture"
  | "textile"
  | "lifestyle";

export interface SectorConfig {
  id: Sector;
  label: string;
  placeholder: string;
  tagline: string;
  imageDirection: string;
}

export const SECTORS: SectorConfig[] = [
  {
    id: "all",
    label: "Global",
    placeholder: "Describe your research task in natural language...",
    tagline: "Cross-domain intelligence for fashion professionals",
    imageDirection: "Editorial fashion overview",
  },
  {
    id: "fashion",
    label: "Fashion",
    placeholder: "Analyze SS26 womenswear trends from recent catwalks and export a PDF report.",
    tagline: "Runway signals, silhouettes & street style intelligence",
    imageDirection: "Runway, silhouettes, street style",
  },
  {
    id: "beauty",
    label: "Beauty",
    placeholder: "Research emerging clean beauty brands gaining market share in North America.",
    tagline: "Backstage beauty, formulations & brand intelligence",
    imageDirection: "Skin texture, backstage beauty",
  },
  {
    id: "skincare",
    label: "Skincare",
    placeholder: "Map skincare ingredient trends and regulatory changes in EU markets.",
    tagline: "Clinical aesthetics, ingredients & regulatory insights",
    imageDirection: "Minimal, clean, clinical aesthetics",
  },
  {
    id: "sustainability",
    label: "Sustainability",
    placeholder: "Map sustainability claims and certifications for European fashion brands.",
    tagline: "Circularity, materials & supply chain transparency",
    imageDirection: "Nature + material honesty",
  },
  {
    id: "fashion-tech",
    label: "Fashion Tech",
    placeholder: "Research AI adoption in fashion supply chains and generate an executive summary.",
    tagline: "Digital innovation, AI & future technologies",
    imageDirection: "Digital, AI, futuristic textures",
  },
  {
    id: "catwalks",
    label: "Catwalks",
    placeholder: "Analyze color and silhouette trends from Paris Fashion Week FW25.",
    tagline: "Live runway coverage, backstage energy & designer analysis",
    imageDirection: "Live runway, backstage energy",
  },
  {
    id: "culture",
    label: "Culture",
    placeholder: "Research cultural influences on luxury brand positioning in Asian markets.",
    tagline: "Art, exhibitions & social signals shaping fashion",
    imageDirection: "Art, exhibitions, social moments",
  },
  {
    id: "textile",
    label: "Textile",
    placeholder: "Find European mills producing sustainable organic cotton with MOQ under 500 units.",
    tagline: "Fibers, mills, material innovation & sourcing",
    imageDirection: "Fabrics, weaving, material close-ups",
  },
  {
    id: "lifestyle",
    label: "Lifestyle",
    placeholder: "Research wellness and fashion convergence trends in luxury consumer behavior.",
    tagline: "Consumer culture, wellness & lifestyle signals",
    imageDirection: "Interiors, people, culture, movement",
  },
];

// Starter questions for each domain
export const DOMAIN_STARTERS: Record<Sector, string[]> = {
  all: [
    "Top sustainability shifts in luxury fashion",
    "AI-driven beauty personalization trends",
    "Emerging materials disrupting textiles",
    "Consumer wellness influencing style",
  ],
  fashion: [
    "Key silhouette shifts from recent Fashion Weeks",
    "Emerging designers to watch this season",
    "Color trends dominating SS26 collections",
    "Streetwear influence on luxury ready-to-wear",
  ],
  beauty: [
    "Clean beauty brands gaining market share",
    "Backstage beauty trends from recent shows",
    "K-beauty innovations entering Western markets",
    "Sustainable packaging trends in prestige beauty",
  ],
  skincare: [
    "Trending ingredients in clinical skincare",
    "EU regulatory changes affecting formulations",
    "Asian skincare innovations gaining traction",
    "Science-backed actives in demand",
  ],
  sustainability: [
    "Brands leading in circularity initiatives",
    "Supply chain transparency best practices",
    "Certifications gaining consumer trust",
    "Regenerative materials entering production",
  ],
  "fashion-tech": [
    "AI adoption in fashion supply chains",
    "Virtual try-on technologies gaining traction",
    "Digital fashion and NFT market signals",
    "Tech startups disrupting fashion retail",
  ],
  catwalks: [
    "Key moments from Paris Fashion Week",
    "Designer collections making headlines",
    "Runway styling trends this season",
    "Emerging talent on the international circuit",
  ],
  culture: [
    "Cultural shifts influencing luxury positioning",
    "Art collaborations in fashion this year",
    "Social movements shaping brand narratives",
    "Regional cultural signals in fashion",
  ],
  textile: [
    "Sustainable fibers gaining adoption",
    "European mills with low MOQ options",
    "Innovative materials in development",
    "Textile sourcing trends in Asia",
  ],
  lifestyle: [
    "Wellness and fashion convergence",
    "Luxury consumer behavior shifts",
    "Travel and leisure influencing style",
    "Home and fashion crossover trends",
  ],
};

interface SectorContextValue {
  currentSector: Sector;
  setSector: (sector: Sector) => void;
  getSectorConfig: () => SectorConfig;
  getDomainSystemPrompt: () => string;
  getStarters: () => string[];
}

const SectorContext = createContext<SectorContextValue | null>(null);

export function SectorProvider({ children }: { children: ReactNode }) {
  const [currentSector, setCurrentSector] = useState<Sector>("all");

  const getSectorConfig = useCallback(() => {
    return SECTORS.find((s) => s.id === currentSector) || SECTORS[0];
  }, [currentSector]);

  const getDomainSystemPrompt = useCallback(() => {
    const config = getSectorConfig();
    if (currentSector === "all") {
      return "";
    }
    
    const domainInstructions: Record<Sector, string> = {
      all: "",
      fashion: "Focus on runway trends, silhouettes, designer collections, fashion week insights, and ready-to-wear developments.",
      beauty: "Focus on beauty formulations, cosmetic trends, brand strategies, backstage beauty, and consumer preferences.",
      skincare: "Focus on skincare ingredients, clinical aesthetics, regulatory compliance, and science-backed formulations.",
      sustainability: "Focus on circularity, sustainable materials, supply chain transparency, certifications, and environmental impact.",
      "fashion-tech": "Focus on AI in fashion, digital innovation, virtual try-on, tech startups, and future technologies.",
      catwalks: "Focus on runway coverage, designer shows, styling trends, fashion week analysis, and emerging talent.",
      culture: "Focus on cultural influences, art collaborations, social movements, and regional cultural signals in fashion.",
      textile: "Focus on fibers, mills, material innovation, textile sourcing, MOQ requirements, and manufacturing capabilities.",
      lifestyle: "Focus on consumer behavior, wellness trends, luxury lifestyle, travel influence, and cross-category signals.",
    };

    return `\n\nDOMAIN MODE: ${config.label.toUpperCase()}\n${domainInstructions[currentSector]}\nPrioritize insights, language, examples, and sources relevant to ${config.label.toLowerCase()}.`;
  }, [currentSector, getSectorConfig]);

  const getStarters = useCallback(() => {
    return DOMAIN_STARTERS[currentSector] || DOMAIN_STARTERS.all;
  }, [currentSector]);

  return (
    <SectorContext.Provider
      value={{
        currentSector,
        setSector: setCurrentSector,
        getSectorConfig,
        getDomainSystemPrompt,
        getStarters,
      }}
    >
      {children}
    </SectorContext.Provider>
  );
}

export function useSector() {
  const context = useContext(SectorContext);
  if (!context) {
    throw new Error("useSector must be used within a SectorProvider");
  }
  return context;
}
