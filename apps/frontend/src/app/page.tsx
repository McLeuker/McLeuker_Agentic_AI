'use client';

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { blogPosts } from "@/data/blog-posts";
import { 
  ArrowRight, 
  Sparkles, 
  TrendingUp, 
  Search, 
  BarChart3, 
  ShieldCheck,
  Layers,
  Globe,
  Zap,
  FileText,
  ChevronLeft,
  ChevronRight,
  Brain,
  Target,
  LayoutDashboard,
  Download,
  Clock,
  Quote,
} from "lucide-react";

/* ─── Static Data ─── */

const suggestionPrompts = [
  {
    icon: TrendingUp,
    title: "Trend Forecasting",
    prompt: "Analyze SS26 womenswear trends from Milan and Paris Fashion Week",
  },
  {
    icon: Search,
    title: "Supplier Research",
    prompt: "Find sustainable denim suppliers in Europe with MOQ under 500 units",
  },
  {
    icon: BarChart3,
    title: "Market Intelligence",
    prompt: "Compare luxury handbag pricing across US, EU, and Asian markets",
  },
  {
    icon: ShieldCheck,
    title: "Sustainability Audit",
    prompt: "Map sustainability certifications for European fashion brands",
  }
];

const capabilities = [
  {
    icon: Brain,
    title: "Multi-Model Intelligence",
    description: "Routes each query to the best AI model — Grok for real-time signals, Gemini for structured analysis, GPT for creative synthesis.",
    accent: "from-[#2E3524]/20 to-transparent",
  },
  {
    icon: Globe,
    title: "10 Specialized Domains",
    description: "Fashion, Beauty, Skincare, Sustainability, Fashion Tech, Catwalks, Culture, Textile, and Lifestyle — each with tailored intelligence.",
    accent: "from-[#1a2a1a]/20 to-transparent",
  },
  {
    icon: Zap,
    title: "Real-Time Signals",
    description: "Live data from web, social, and search sources. Breaking news, trending topics, and market movements — updated continuously.",
    accent: "from-[#2a2e1a]/20 to-transparent",
  },
  {
    icon: Layers,
    title: "Structured Outputs",
    description: "Not chat — structured intelligence. Comparisons, tables, key takeaways, and actionable next steps in every response.",
    accent: "from-[#1a2a20]/20 to-transparent",
  },
  {
    icon: FileText,
    title: "Professional Reports",
    description: "Generate Excel sheets, PDF reports, Word documents, and presentations — formatted and ready for stakeholders.",
    accent: "from-[#252e1a]/20 to-transparent",
  },
  {
    icon: Target,
    title: "Source-Backed Research",
    description: "Every insight is traceable. We surface sources, citations, and confidence levels so you know what's verified and what's estimated.",
    accent: "from-[#1a2e24]/20 to-transparent",
  },
];

const domains = [
  { slug: "fashion", name: "Fashion", description: "Runway signals, silhouettes & street style", image: "/images/domains/fashion.jpg" },
  { slug: "beauty", name: "Beauty", description: "Formulations, ingredients & brand strategy", image: "/images/domains/beauty.jpg" },
  { slug: "skincare", name: "Skincare", description: "Clinical trends, actives & consumer science", image: "/images/domains/skincare.jpg" },
  { slug: "sustainability", name: "Sustainability", description: "Certifications, impact & circular models", image: "/images/domains/sustainability.jpg" },
  { slug: "fashion-tech", name: "Fashion Tech", description: "Wearables, AI tools & digital innovation", image: "/images/domains/fashion-tech.jpg" },
  { slug: "catwalks", name: "Catwalks", description: "Show reviews, designer analysis & collections", image: "/images/domains/catwalks.jpg" },
  { slug: "culture", name: "Culture", description: "Art, music & cultural influence on fashion", image: "/images/domains/culture.jpg" },
  { slug: "textile", name: "Textile", description: "Fabrics, materials & manufacturing intelligence", image: "/images/domains/textile.jpg" },
  { slug: "lifestyle", name: "Lifestyle", description: "Wellness, travel & luxury consumer trends", image: "/images/domains/lifestyle.jpg" },
];

const steps = [
  {
    number: "01",
    icon: Search,
    title: "Describe Your Task",
    description: "Type a natural language prompt — from trend analysis to supplier research. Our AI understands fashion context.",
  },
  {
    number: "02",
    icon: Brain,
    title: "AI Researches & Analyzes",
    description: "Multiple AI models work in parallel, crawling live sources, analyzing data, and synthesizing findings.",
  },
  {
    number: "03",
    icon: LayoutDashboard,
    title: "Structured Intelligence",
    description: "Results are organized into clear sections: key takeaways, comparisons, data tables, and source citations.",
  },
  {
    number: "04",
    icon: Download,
    title: "Export & Act",
    description: "Download as Excel, PDF, or presentation. Share with your team. Make decisions backed by real intelligence.",
  },
];

const outputExamples = [
  {
    title: "Trend Forecast Report",
    type: "PDF Report",
    description: "SS26 womenswear color and silhouette analysis across 4 fashion weeks",
    tags: ["12 pages", "47 sources", "8 charts"],
  },
  {
    title: "Supplier Comparison",
    type: "Excel Sheet",
    description: "European sustainable denim suppliers with MOQ, pricing, and certifications",
    tags: ["32 suppliers", "6 criteria", "3 tiers"],
  },
  {
    title: "Market Intelligence",
    type: "Structured Analysis",
    description: "Luxury handbag pricing strategy across US, EU, and Asian markets",
    tags: ["15 brands", "3 markets", "Price matrix"],
  },
  {
    title: "Brand Positioning Map",
    type: "Presentation",
    description: "Competitive landscape analysis for emerging sustainable fashion brands",
    tags: ["20 brands", "4 quadrants", "Key insights"],
  },
  {
    title: "Certification Audit",
    type: "Word Document",
    description: "GOTS, OEKO-TEX, and BCI compliance mapping for supply chain partners",
    tags: ["18 suppliers", "5 certs", "Gap analysis"],
  },
];

const testimonials = [
  {
    quote: "McLeuker AI transformed how we approach trend research. What took weeks now takes hours.",
    author: "Creative Director",
    company: "European Fashion House",
  },
  {
    quote: "The supplier intelligence reports are incredibly thorough. A game-changer for our sourcing team.",
    author: "Head of Procurement",
    company: "Luxury Accessories Brand",
  },
  {
    quote: "Finally, an AI tool built by people who understand fashion. The outputs are genuinely useful.",
    author: "Brand Strategy Lead",
    company: "Sustainable Fashion Label",
  },
  {
    quote: "The multi-model approach means we get real-time data alongside deep analysis. Nothing else does this.",
    author: "VP of Merchandising",
    company: "Global Retail Group",
  },
  {
    quote: "We use it daily for competitive intelligence. The structured outputs save us hours of manual work.",
    author: "Market Analyst",
    company: "Fashion Consultancy",
  },
];

/* ─── Horizontal Scroll Hook ─── */

function useHorizontalScroll() {
  const ref = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const checkScroll = () => {
    if (!ref.current) return;
    const { scrollLeft, scrollWidth, clientWidth } = ref.current;
    setCanScrollLeft(scrollLeft > 4);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 4);
  };

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    checkScroll();
    el.addEventListener("scroll", checkScroll, { passive: true });
    window.addEventListener("resize", checkScroll);
    return () => {
      el.removeEventListener("scroll", checkScroll);
      window.removeEventListener("resize", checkScroll);
    };
  }, []);

  const scroll = (direction: "left" | "right") => {
    if (!ref.current) return;
    const amount = ref.current.clientWidth * 0.75;
    ref.current.scrollBy({ left: direction === "left" ? -amount : amount, behavior: "smooth" });
  };

  return { ref, canScrollLeft, canScrollRight, scroll };
}

/* ─── Page Component ─── */

export default function LandingPage() {
  const [prompt, setPrompt] = useState("");
  const router = useRouter();
  const domainScroll = useHorizontalScroll();
  const outputScroll = useHorizontalScroll();
  const testimonialScroll = useHorizontalScroll();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      sessionStorage.setItem("domainPrompt", prompt);
      sessionStorage.setItem("autoExecute", "true");
      router.push("/dashboard");
    }
  };

  const handlePromptClick = (promptText: string) => {
    sessionStorage.setItem("domainPrompt", promptText);
    sessionStorage.setItem("autoExecute", "true");
    router.push("/dashboard");
  };

  const recentPosts = blogPosts.slice(0, 3);

  return (
    <div className="min-h-screen bg-[#070707] overflow-x-hidden">
      <TopNavigation variant="marketing" />
      
      {/* Spacer for fixed nav */}
      <div className="h-16 lg:h-[72px]" />

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 1 — Try McLeuker AI (KEEP) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="pt-24 lg:pt-28 pb-16 lg:pb-24 bg-[#0A0A0A]">
        <div className="container mx-auto px-4 sm:px-6 lg:px-12">
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-xs sm:text-sm text-white/50 uppercase tracking-[0.2em] mb-3 sm:mb-4">
              Experience the Platform
            </p>
            <h1 className="font-editorial text-3xl sm:text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-4 sm:mb-6 leading-[1.1]">
              Try McLeuker AI
            </h1>
            <p className="text-white/65 text-base sm:text-lg mb-8 sm:mb-10 max-w-2xl mx-auto px-2">
              Describe your research task and let our AI deliver professional-grade intelligence.
            </p>

            <form onSubmit={handleSubmit} className="max-w-2xl mx-auto mb-10 sm:mb-12 px-2">
              <div className="relative">
                <textarea 
                  value={prompt} 
                  onChange={e => setPrompt(e.target.value)} 
                  placeholder="e.g., Analyze SS26 womenswear color trends from Milan and Paris..." 
                  className={cn(
                    "w-full h-28 sm:h-32 px-4 sm:px-6 py-4 sm:py-5",
                    "rounded-[20px]",
                    "mcleuker-green-input",
                    "text-white/[0.88] placeholder:text-white/40",
                    "focus:outline-none",
                    "resize-none text-sm sm:text-base"
                  )}
                  onKeyDown={e => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }} 
                />
                <button 
                  type="submit" 
                  disabled={!prompt.trim()} 
                  className={cn(
                    "absolute bottom-3 sm:bottom-4 right-3 sm:right-4",
                    "px-4 sm:px-6 py-2 rounded-md text-sm font-medium",
                    "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white",
                    "hover:from-[#3a4530] hover:to-[#353d2a]",
                    "disabled:bg-white/10 disabled:text-white/40 disabled:from-white/10 disabled:to-white/10",
                    "flex items-center gap-2 transition-all"
                  )}
                >
                  <span className="hidden sm:inline">Run Task</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </form>

            <div className="max-w-4xl mx-auto px-2">
              <p className="text-xs sm:text-sm text-white/40 uppercase tracking-[0.15em] mb-4 sm:mb-6">
                Try one of these examples
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {suggestionPrompts.map((suggestion, i) => {
                  const IconComponent = suggestion.icon;
                  return (
                    <button
                      key={i}
                      onClick={() => handlePromptClick(suggestion.prompt)}
                      className={cn(
                        "group relative p-4 sm:p-5 rounded-[18px]",
                        "mcleuker-bubble",
                        i % 4 === 0 && "mcleuker-bubble-v1",
                        i % 4 === 1 && "mcleuker-bubble-v2",
                        i % 4 === 2 && "mcleuker-bubble-v3",
                        i % 4 === 3 && "mcleuker-bubble-v4",
                        "transition-all duration-200 text-left"
                      )}
                    >
                      <div className="relative flex items-start gap-3 sm:gap-4 z-10">
                        <div className="flex-shrink-0 w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-white/[0.08] flex items-center justify-center group-hover:bg-[#2E3524]/20 transition-colors">
                          <IconComponent className="w-5 h-5 sm:w-6 sm:h-6 text-white/70 group-hover:text-[#5c6652]" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm sm:text-base font-medium text-white/[0.92] mb-1 sm:mb-1.5">
                            {suggestion.title}
                          </p>
                          <p className="text-xs sm:text-sm text-white/55 leading-relaxed line-clamp-2">
                            {suggestion.prompt}
                          </p>
                        </div>
                        <ArrowRight className="w-4 h-4 text-white/30 group-hover:text-[#2E3524] group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 2 — Hero with Runway Image (KEEP) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative min-h-[70vh] lg:min-h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0">
          <Image 
            src="/images/hero-runway.jpg" 
            alt="Fashion runway" 
            fill
            className="object-cover grayscale contrast-[1.08] brightness-[0.85]"
            priority
          />
          <div 
            className="absolute inset-0" 
            style={{
              background: 'linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.82) 60%, rgba(0,0,0,0.90) 100%)'
            }}
          />
        </div>

        <div className="relative z-10 container mx-auto px-6 lg:px-12 py-20 lg:py-32">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#141414]/80 backdrop-blur-sm border border-[#2E3524]/30 mb-5 lg:mb-6">
              <Sparkles className="w-4 h-4 text-[#5c6652]" />
              <span className="text-sm text-white/70 tracking-wide">
                AI & Sustainability for Fashion
              </span>
            </div>

            <h2 className="font-editorial text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-white/[0.92] mb-4 lg:mb-5 leading-[1.05]">
              The Future of<br />Fashion Intelligence
            </h2>

            <p className="text-base md:text-lg lg:text-xl text-white/65 mb-8 lg:mb-10 max-w-2xl mx-auto leading-relaxed">
              From one prompt to structured intelligence: trends, benchmarks, and clear next steps.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/dashboard"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white font-medium",
                  "hover:from-[#3a4530] hover:to-[#353d2a] transition-all",
                  "shadow-lg shadow-[#2E3524]/15"
                )}
              >
                Start Research
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/domains"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "border border-white/[0.18] text-white/90",
                  "hover:bg-[#2E3524]/10 hover:border-[#2E3524]/30 transition-colors"
                )}
              >
                Explore Domains
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 3 — Capabilities Showcase (NEW) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="text-center mb-16 lg:mb-20">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#0C0C0C] border border-white/[0.06] mb-6">
                <div className="w-1.5 h-1.5 rounded-full bg-[#5c6652] animate-pulse" />
                <span className="text-xs text-white/50 uppercase tracking-[0.15em]">What We Deliver</span>
              </div>
              <h2 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-6 leading-[1.05]">
                Intelligence, not just answers
              </h2>
              <p className="text-white/55 text-lg max-w-2xl mx-auto leading-relaxed">
                McLeuker AI combines multiple AI models, real-time data sources, and fashion domain expertise to deliver research you can act on.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
              {capabilities.map((cap, i) => {
                const Icon = cap.icon;
                return (
                  <div
                    key={i}
                    className={cn(
                      "group relative p-7 lg:p-8 rounded-2xl",
                      "bg-[#0C0C0C] border border-white/[0.04]",
                      "hover:border-[#2E3524]/30 transition-all duration-300",
                      "overflow-hidden"
                    )}
                  >
                    {/* Subtle gradient glow on hover */}
                    <div className={cn(
                      "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500",
                      "bg-gradient-to-br", cap.accent
                    )} />
                    <div className="relative z-10">
                      <div className="w-11 h-11 rounded-xl bg-[#141414] border border-white/[0.06] flex items-center justify-center mb-5 group-hover:border-[#2E3524]/30 transition-colors">
                        <Icon className="w-5 h-5 text-[#5c6652]" />
                      </div>
                      <h3 className="text-lg font-medium text-white/[0.92] mb-2.5">
                        {cap.title}
                      </h3>
                      <p className="text-sm text-white/50 leading-relaxed">
                        {cap.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 4 — Domain Carousel (NEW — Horizontal Scroll) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="flex items-end justify-between mb-12">
              <div>
                <p className="text-xs text-white/40 uppercase tracking-[0.2em] mb-3">Specialized Intelligence</p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                  10 Domains. One Platform.
                </h2>
              </div>
              <div className="hidden sm:flex items-center gap-2">
                <button
                  onClick={() => domainScroll.scroll("left")}
                  disabled={!domainScroll.canScrollLeft}
                  className="w-10 h-10 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/50 hover:text-white/80 hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => domainScroll.scroll("right")}
                  disabled={!domainScroll.canScrollRight}
                  className="w-10 h-10 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/50 hover:text-white/80 hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Full-bleed scrollable area */}
        <div
          ref={domainScroll.ref}
          className="flex gap-5 overflow-x-auto scrollbar-hide px-6 lg:px-12 pb-4 snap-x snap-mandatory"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          {/* Left spacer for centering */}
          <div className="flex-shrink-0 w-[calc((100vw-1200px)/2-24px)] hidden xl:block" />
          
          {domains.map((domain, i) => (
            <Link
              key={i}
              href={`/domain/${domain.slug}`}
              className="group flex-shrink-0 w-[280px] sm:w-[320px] snap-start"
            >
              <div className="relative h-[380px] sm:h-[420px] rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] group-hover:border-[#2E3524]/30 transition-all duration-300">
                {/* Domain image */}
                <div className="absolute inset-0">
                  <Image
                    src={domain.image}
                    alt={domain.name}
                    fill
                    className="object-cover grayscale brightness-[0.6] group-hover:brightness-[0.7] group-hover:scale-105 transition-all duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
                </div>
                
                {/* Content overlay */}
                <div className="absolute inset-0 flex flex-col justify-end p-6">
                  <p className="text-xs text-[#5c6652] uppercase tracking-[0.15em] mb-2">Domain</p>
                  <h3 className="text-xl font-medium text-white/[0.95] mb-2">
                    {domain.name}
                  </h3>
                  <p className="text-sm text-white/50 leading-relaxed mb-4">
                    {domain.description}
                  </p>
                  <div className="flex items-center gap-2 text-[#5c6652] text-sm opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 transition-all duration-300">
                    <span>Explore</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </Link>
          ))}
          
          {/* Right spacer */}
          <div className="flex-shrink-0 w-6 lg:w-12 xl:w-[calc((100vw-1200px)/2-24px)]" />
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 5 — How It Works (NEW) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="text-center mb-16 lg:mb-20">
              <p className="text-xs text-white/40 uppercase tracking-[0.2em] mb-3">The Process</p>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                From prompt to intelligence in minutes
              </h2>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-4">
              {steps.map((step, i) => {
                const Icon = step.icon;
                return (
                  <div key={i} className="relative group">
                    {/* Connecting line (desktop only) */}
                    {i < steps.length - 1 && (
                      <div className="hidden lg:block absolute top-10 left-[calc(50%+40px)] w-[calc(100%-40px)] h-px bg-gradient-to-r from-white/[0.08] to-transparent" />
                    )}
                    
                    <div className="text-center lg:text-left">
                      {/* Step number + icon */}
                      <div className="flex items-center justify-center lg:justify-start gap-4 mb-6">
                        <div className="w-20 h-20 rounded-2xl bg-[#0C0C0C] border border-white/[0.06] flex items-center justify-center group-hover:border-[#2E3524]/30 transition-colors relative">
                          <Icon className="w-7 h-7 text-[#5c6652]" />
                          <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-xs text-white/60 font-medium">
                            {step.number}
                          </span>
                        </div>
                      </div>
                      
                      <h3 className="text-lg font-medium text-white/[0.92] mb-2.5">
                        {step.title}
                      </h3>
                      <p className="text-sm text-white/45 leading-relaxed max-w-[260px] mx-auto lg:mx-0">
                        {step.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* CTA */}
            <div className="text-center mt-16">
              <Link
                href="/dashboard"
                onClick={() => {
                  sessionStorage.setItem("domainPrompt", "Analyze SS26 womenswear trends from Milan and Paris Fashion Week");
                  sessionStorage.setItem("autoExecute", "true");
                }}
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white font-medium",
                  "hover:from-[#3a4530] hover:to-[#353d2a] transition-all",
                  "shadow-lg shadow-[#2E3524]/15"
                )}
              >
                Try It Now
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 6 — Output Gallery (NEW — Horizontal Scroll) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="flex items-end justify-between mb-12">
              <div>
                <p className="text-xs text-white/40 uppercase tracking-[0.2em] mb-3">What You Get</p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                  Professional-grade outputs
                </h2>
                <p className="text-white/45 text-base mt-4 max-w-lg">
                  Every research task produces structured, exportable intelligence — not chat responses.
                </p>
              </div>
              <div className="hidden sm:flex items-center gap-2">
                <button
                  onClick={() => outputScroll.scroll("left")}
                  disabled={!outputScroll.canScrollLeft}
                  className="w-10 h-10 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/50 hover:text-white/80 hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => outputScroll.scroll("right")}
                  disabled={!outputScroll.canScrollRight}
                  className="w-10 h-10 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/50 hover:text-white/80 hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div
          ref={outputScroll.ref}
          className="flex gap-5 overflow-x-auto scrollbar-hide px-6 lg:px-12 pb-4 snap-x snap-mandatory"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          <div className="flex-shrink-0 w-[calc((100vw-1200px)/2-24px)] hidden xl:block" />
          
          {outputExamples.map((output, i) => (
            <div
              key={i}
              className="group flex-shrink-0 w-[340px] sm:w-[380px] snap-start"
            >
              <div className="h-full p-7 rounded-2xl bg-[#0C0C0C] border border-white/[0.04] group-hover:border-[#2E3524]/20 transition-all duration-300">
                {/* Type badge */}
                <div className="flex items-center justify-between mb-5">
                  <span className="px-3 py-1 rounded-full bg-[#141414] border border-white/[0.06] text-xs text-[#5c6652] uppercase tracking-wider">
                    {output.type}
                  </span>
                  <FileText className="w-5 h-5 text-white/20 group-hover:text-[#5c6652]/60 transition-colors" />
                </div>
                
                {/* Content */}
                <h3 className="text-lg font-medium text-white/[0.92] mb-2.5">
                  {output.title}
                </h3>
                <p className="text-sm text-white/45 leading-relaxed mb-6">
                  {output.description}
                </p>
                
                {/* Tags */}
                <div className="flex flex-wrap gap-2">
                  {output.tags.map((tag, j) => (
                    <span
                      key={j}
                      className="px-2.5 py-1 rounded-md bg-[#141414] text-xs text-white/40"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
          
          {/* "See it in action" card */}
          <Link
            href="/dashboard"
            className="group flex-shrink-0 w-[340px] sm:w-[380px] snap-start"
          >
            <div className="h-full p-7 rounded-2xl bg-gradient-to-br from-[#2E3524]/10 to-[#0C0C0C] border border-[#2E3524]/20 group-hover:border-[#2E3524]/40 transition-all duration-300 flex flex-col items-center justify-center text-center min-h-[260px]">
              <div className="w-14 h-14 rounded-2xl bg-[#2E3524]/20 flex items-center justify-center mb-5">
                <ArrowRight className="w-6 h-6 text-[#5c6652]" />
              </div>
              <h3 className="text-lg font-medium text-white/[0.92] mb-2">
                See it in action
              </h3>
              <p className="text-sm text-white/45">
                Try a research task and see the output quality yourself.
              </p>
            </div>
          </Link>
          
          <div className="flex-shrink-0 w-6 lg:w-12 xl:w-[calc((100vw-1200px)/2-24px)]" />
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 7 — Testimonials (REDESIGNED — Horizontal Scroll) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="flex items-end justify-between mb-12">
              <div>
                <p className="text-xs text-white/40 uppercase tracking-[0.2em] mb-3">From the Industry</p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                  Trusted by fashion professionals
                </h2>
              </div>
              <div className="hidden sm:flex items-center gap-2">
                <button
                  onClick={() => testimonialScroll.scroll("left")}
                  disabled={!testimonialScroll.canScrollLeft}
                  className="w-10 h-10 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/50 hover:text-white/80 hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => testimonialScroll.scroll("right")}
                  disabled={!testimonialScroll.canScrollRight}
                  className="w-10 h-10 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/50 hover:text-white/80 hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div
          ref={testimonialScroll.ref}
          className="flex gap-5 overflow-x-auto scrollbar-hide px-6 lg:px-12 pb-4 snap-x snap-mandatory"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          <div className="flex-shrink-0 w-[calc((100vw-1200px)/2-24px)] hidden xl:block" />
          
          {testimonials.map((t, i) => (
            <div
              key={i}
              className="flex-shrink-0 w-[360px] sm:w-[420px] snap-start"
            >
              <div className="h-full p-8 rounded-2xl bg-[#0C0C0C] border border-white/[0.04] relative">
                <Quote className="w-8 h-8 text-[#2E3524]/30 mb-5" />
                <blockquote className="text-white/[0.82] text-base leading-relaxed mb-8">
                  &ldquo;{t.quote}&rdquo;
                </blockquote>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#141414] border border-white/[0.06] flex items-center justify-center">
                    <span className="text-sm text-white/50 font-medium">
                      {t.author.split(" ").map(w => w[0]).join("")}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white/[0.88]">{t.author}</p>
                    <p className="text-xs text-white/40">{t.company}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          <div className="flex-shrink-0 w-6 lg:w-12 xl:w-[calc((100vw-1200px)/2-24px)]" />
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 8 — Blog Preview (NEW) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="flex items-end justify-between mb-12">
              <div>
                <p className="text-xs text-white/40 uppercase tracking-[0.2em] mb-3">Insights & Analysis</p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                  From the McLeuker Journal
                </h2>
              </div>
              <Link
                href="/blog"
                className="hidden sm:inline-flex items-center gap-2 text-sm text-white/50 hover:text-[#5c6652] transition-colors"
              >
                View All
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {recentPosts.map((post, i) => (
                <Link
                  key={i}
                  href={`/blog/${post.slug}`}
                  className="group"
                >
                  <div className="rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] group-hover:border-[#2E3524]/20 transition-all duration-300">
                    {/* Image */}
                    <div className="relative h-[200px] overflow-hidden">
                      <Image
                        src={post.image}
                        alt={post.title}
                        fill
                        className="object-cover grayscale brightness-[0.7] group-hover:brightness-[0.8] group-hover:scale-105 transition-all duration-700"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-[#0C0C0C] to-transparent" />
                      <div className="absolute top-4 left-4">
                        <span className="px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-sm text-xs text-white/70 border border-white/[0.06]">
                          {post.category}
                        </span>
                      </div>
                    </div>
                    
                    {/* Content */}
                    <div className="p-6">
                      <div className="flex items-center gap-3 text-xs text-white/35 mb-3">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{post.readTime}</span>
                        <span className="w-1 h-1 rounded-full bg-white/20" />
                        <span>{new Date(post.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</span>
                      </div>
                      <h3 className="text-base font-medium text-white/[0.92] mb-2 group-hover:text-[#5c6652] transition-colors line-clamp-2">
                        {post.title}
                      </h3>
                      <p className="text-sm text-white/40 leading-relaxed line-clamp-2">
                        {post.excerpt}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Mobile "View All" */}
            <div className="text-center mt-8 sm:hidden">
              <Link
                href="/blog"
                className="inline-flex items-center gap-2 text-sm text-white/50 hover:text-[#5c6652] transition-colors"
              >
                View All Posts
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 9 — Final CTA (REDESIGNED) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative py-32 lg:py-40 bg-[#070707] overflow-hidden">
        {/* Subtle radial glow */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[800px] h-[800px] rounded-full bg-[#2E3524]/[0.04] blur-[120px]" />
        </div>
        
        <div className="relative z-10 container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#0C0C0C] border border-[#2E3524]/20 mb-8">
              <Sparkles className="w-4 h-4 text-[#5c6652]" />
              <span className="text-xs text-white/50 uppercase tracking-[0.15em]">Start Free</span>
            </div>
            
            <h2 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-6 leading-[1.05]">
              Your next research task,<br />solved in minutes
            </h2>
            <p className="text-white/50 text-lg mb-12 max-w-xl mx-auto leading-relaxed">
              Join fashion professionals who use McLeuker AI to make faster, smarter decisions backed by real intelligence.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/signup"
                className={cn(
                  "inline-flex items-center gap-2 px-10 py-4 rounded-full",
                  "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white font-medium text-base",
                  "hover:from-[#3a4530] hover:to-[#353d2a] transition-all",
                  "shadow-lg shadow-[#2E3524]/15"
                )}
              >
                Start Free Trial
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/pricing"
                className={cn(
                  "inline-flex items-center gap-2 px-10 py-4 rounded-full",
                  "bg-[#141414] border border-white/[0.10] text-white/80",
                  "hover:bg-[#2E3524]/10 hover:border-[#2E3524]/30 transition-colors"
                )}
              >
                View Pricing
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
