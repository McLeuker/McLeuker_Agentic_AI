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
  File,
  FileSpreadsheet,
  Presentation,
  GraduationCap,
  Microscope,
  Palette,
  Leaf,
  ShoppingBag,
  Newspaper,
  Code,
  Paintbrush,
  MoreHorizontal,
  Table,
  PieChart,
  BarChart,
  LineChart,
  CheckCircle,
  Database,
  Filter,
  SortAsc,
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
    description: "Routes each query to the best AI model for real-time signals, structured analysis, or creative synthesis.",
  },
  {
    icon: Globe,
    title: "10 Specialized Domains",
    description: "Fashion, Beauty, Skincare, Sustainability, Fashion Tech, Catwalks, Culture, Textile, and Lifestyle.",
  },
  {
    icon: Zap,
    title: "Real-Time Signals",
    description: "Live data from web, social, and search sources. Breaking news, trending topics, and market movements.",
  },
  {
    icon: Layers,
    title: "Structured Outputs",
    description: "Not chat — structured intelligence. Comparisons, tables, key takeaways, and actionable next steps.",
  },
  {
    icon: FileText,
    title: "Professional Reports",
    description: "Generate Excel sheets, PDF reports, Word documents, and presentations — formatted for stakeholders.",
  },
  {
    icon: Target,
    title: "Source-Backed Research",
    description: "Every insight is traceable. Sources, citations, and confidence levels so you know what's verified.",
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
    description: "Type a natural language prompt — from trend analysis to supplier research.",
  },
  {
    number: "02",
    icon: Brain,
    title: "AI Researches",
    description: "Multiple AI models work in parallel, crawling live sources and synthesizing findings.",
  },
  {
    number: "03",
    icon: LayoutDashboard,
    title: "Structured Output",
    description: "Results organized into key takeaways, comparisons, data tables, and source citations.",
  },
  {
    number: "04",
    icon: Download,
    title: "Export & Act",
    description: "Download as Excel, PDF, or presentation. Share with your team and act on it.",
  },
];

const useCases = [
  {
    role: "Creative Directors",
    task: "Trend forecasting across 4 fashion weeks in one prompt",
    result: "12-page structured report with visual references",
    icon: Sparkles,
    image: "/images/domains/fashion.jpg",
    accent: "#C9A96E",
  },
  {
    role: "Sourcing Teams",
    task: "Find and compare 30+ suppliers by MOQ, price, and certifications",
    result: "Exportable Excel with tier rankings and contact details",
    icon: Search,
    image: "/images/domains/textile.jpg",
    accent: "#A3B18A",
  },
  {
    role: "Brand Strategists",
    task: "Competitive positioning across luxury, mid-range, and DTC",
    result: "Presentation-ready brand maps with market data",
    icon: Target,
    image: "/images/domains/culture.jpg",
    accent: "#E07A5F",
  },
  {
    role: "Sustainability Leads",
    task: "Map GOTS, OEKO-TEX, and BCI compliance across supply chain",
    result: "Gap analysis document with remediation steps",
    icon: ShieldCheck,
    image: "/images/domains/sustainability.jpg",
    accent: "#6B9E78",
  },
  {
    role: "Fashion Students",
    task: "Research dissertation topics across fashion history, trends, and cultural impact",
    result: "5,000-word research document with 40+ cited sources",
    icon: GraduationCap,
    image: "/images/domains/catwalks.jpg",
    accent: "#8ECAE6",
  },
  {
    role: "Academic Researchers",
    task: "Cross-reference consumer behavior data with market trends across regions",
    result: "Multi-sheet Excel with statistical breakdowns and methodology notes",
    icon: Microscope,
    image: "/images/domains/lifestyle.jpg",
    accent: "#DDA15E",
  },
  {
    role: "Beauty Professionals",
    task: "Analyze ingredient trends and clean beauty formulations across 50 brands",
    result: "Competitive landscape PDF with ingredient matrices and brand positioning",
    icon: Palette,
    image: "/images/domains/beauty.jpg",
    accent: "#D4A0B0",
  },
  {
    role: "Skincare Specialists",
    task: "Compare active ingredient efficacy data and regulatory compliance by market",
    result: "Clinical summary report with regulatory comparison tables",
    icon: Leaf,
    image: "/images/domains/skincare.jpg",
    accent: "#8ECAE6",
  },
  {
    role: "Retail Buyers",
    task: "Benchmark pricing, sell-through rates, and assortment gaps across competitors",
    result: "Buyer's deck with pricing grids and assortment recommendations",
    icon: ShoppingBag,
    image: "/images/domains/fashion-tech.jpg",
    accent: "#7B68EE",
  },
  {
    role: "Fashion Journalists",
    task: "Compile show notes, designer interviews, and trend narratives from fashion week",
    result: "Editorial-ready article draft with quotes and trend analysis",
    icon: Newspaper,
    image: "/images/domains/catwalks.jpg",
    accent: "#E8D5B7",
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
  const [activeOutput, setActiveOutput] = useState(0);
  const router = useRouter();
  const domainScroll = useHorizontalScroll();
  const useCaseScroll = useHorizontalScroll();

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

  // Auto-rotate output showcase
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveOutput((prev) => (prev + 1) % 4);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  const recentPosts = blogPosts.slice(0, 3);

  return (
    <div className="min-h-screen bg-[#070707] overflow-x-hidden">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 1 — Hero (OpenAI-style clean, centered) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative bg-[#070707] min-h-[calc(100vh-72px)] flex items-center justify-center">
        {/* Subtle radial glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-[#1a1f14]/30 blur-[150px]" />
        </div>

        <div className="relative z-10 w-full max-w-3xl mx-auto px-6 text-center py-20">
          {/* Main heading */}
          <h1 className="font-editorial text-5xl md:text-6xl lg:text-[72px] text-white/[0.95] tracking-tight leading-[1.08] mb-6">
            What do you want<br />to research?
          </h1>

          {/* Subtitle */}
          <p className="text-white/40 text-lg md:text-xl max-w-xl mx-auto mb-10 leading-relaxed">
            AI-powered fashion intelligence. From one prompt to structured reports, benchmarks, and clear next steps.
          </p>

          {/* Search input */}
          <form onSubmit={handleSubmit} className="relative max-w-2xl mx-auto mb-6">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Analyze SS26 trends, find suppliers, compare markets..."
              className={cn(
                "w-full h-14 pl-5 pr-14 rounded-2xl",
                "bg-white/[0.05] border border-white/[0.10]",
                "text-white/90 placeholder:text-white/25",
                "focus:outline-none focus:border-white/[0.20] focus:bg-white/[0.07]",
                "text-[15px] transition-all duration-300"
              )}
            />
            <button
              type="submit"
              disabled={!prompt.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-xl bg-white/90 text-black flex items-center justify-center hover:bg-white disabled:opacity-20 disabled:cursor-not-allowed transition-all"
            >
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Suggestion pills */}
          <div className="flex flex-wrap justify-center gap-2">
            {suggestionPrompts.map((s, i) => {
              const Icon = s.icon;
              return (
                <button
                  key={i}
                  onClick={() => handlePromptClick(s.prompt)}
                  className="group flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.06] transition-all duration-200"
                >
                  <Icon className="w-3.5 h-3.5 text-white/25 group-hover:text-white/40 transition-colors" />
                  <span className="text-xs text-white/40 group-hover:text-white/60 transition-colors">{s.title}</span>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 2 — The Future of Fashion Intelligence */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative py-24 lg:py-32 bg-[#070707] overflow-hidden">
        {/* Separator line */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[80%] max-w-[600px] h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />

        {/* Background visual elements */}
        <div className="absolute inset-0 pointer-events-none">
          {/* Floating grid dots */}
          <div className="absolute top-12 left-[10%] w-[200px] h-[200px] opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
          <div className="absolute bottom-12 right-[10%] w-[200px] h-[200px] opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
          {/* Accent glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] rounded-full bg-[#2E3524]/[0.06] blur-[120px]" />
        </div>

        <div className="relative z-10 container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            {/* Top: Heading + Description */}
            <div className="text-center mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06] mb-6">
                <Sparkles className="w-3.5 h-3.5 text-[#6b9b8a]/60" />
                <span className="text-[11px] text-white/40 uppercase tracking-[0.15em]">Fashion Intelligence Platform</span>
              </div>
              <h2 className="font-editorial text-4xl md:text-5xl lg:text-[56px] text-white/[0.95] tracking-tight mb-5 leading-[1.08]">
                The Future of<br />Fashion Intelligence
              </h2>
              <p className="text-white/40 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
                One platform for every fashion research task. From trend analysis to supplier sourcing — structured, professional, and ready to act on.
              </p>
            </div>

            {/* Bento Grid — Visual showcase */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-14">
              {/* Card 1 — Large: Live Research Preview */}
              <div className="lg:col-span-2 group relative rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.08] transition-all duration-500 p-6 lg:p-8">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#6b9b8a]/20 to-transparent" />
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full bg-[#6b9b8a]/60 animate-pulse" />
                      <span className="text-[10px] text-white/30 uppercase tracking-wider">Live Research</span>
                    </div>
                    <h3 className="text-lg font-medium text-white/85">From prompt to structured intelligence</h3>
                  </div>
                  <Brain className="w-5 h-5 text-white/15" />
                </div>
                {/* Mock research output */}
                <div className="bg-[#080808] rounded-xl border border-white/[0.04] p-4 mb-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Search className="w-3.5 h-3.5 text-white/20" />
                    <span className="text-[13px] text-white/50">"Analyze SS26 denim trends across European markets"</span>
                  </div>
                  <div className="h-px bg-white/[0.04] mb-3" />
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { label: "Sources analyzed", value: "47" },
                      { label: "Key trends found", value: "12" },
                      { label: "Markets covered", value: "8" },
                    ].map((stat, i) => (
                      <div key={i} className="text-center">
                        <div className="text-xl font-light text-white/80">{stat.value}</div>
                        <div className="text-[9px] text-white/25 uppercase tracking-wider mt-0.5">{stat.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
                {/* Output files row */}
                <div className="flex gap-2">
                  {[
                    { ext: ".xlsx", color: "#217346", name: "supplier_data" },
                    { ext: ".pdf", color: "#D32F2F", name: "trend_report" },
                    { ext: ".pptx", color: "#D04423", name: "market_deck" },
                  ].map((file, i) => (
                    <div key={i} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04] flex-1">
                      <div className="w-1.5 h-6 rounded-full" style={{ backgroundColor: `${file.color}40` }} />
                      <div>
                        <div className="text-[11px] text-white/50">{file.name}</div>
                        <div className="text-[9px] font-mono" style={{ color: `${file.color}90` }}>{file.ext}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Card 2 — Domain coverage */}
              <div className="group relative rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.08] transition-all duration-500 p-6">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#C9A96E]/15 to-transparent" />
                <div className="flex items-center gap-2 mb-4">
                  <Globe className="w-4 h-4 text-white/25" />
                  <span className="text-[10px] text-white/30 uppercase tracking-wider">Domain Coverage</span>
                </div>
                <div className="text-4xl font-light text-white/90 mb-1">10</div>
                <div className="text-sm text-white/40 mb-5">Specialized domains</div>
                <div className="flex flex-wrap gap-1.5">
                  {["Fashion", "Beauty", "Skincare", "Sustainability", "Tech", "Catwalks", "Culture", "Textile", "Lifestyle"].map((d, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-full bg-white/[0.03] border border-white/[0.05] text-[10px] text-white/35">{d}</span>
                  ))}
                </div>
              </div>

              {/* Card 3 — Speed metric */}
              <div className="group relative rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.08] transition-all duration-500 p-6">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#8ECAE6]/15 to-transparent" />
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-4 h-4 text-white/25" />
                  <span className="text-[10px] text-white/30 uppercase tracking-wider">Research Speed</span>
                </div>
                <div className="text-4xl font-light text-white/90 mb-1">&lt;5<span className="text-lg text-white/40">min</span></div>
                <div className="text-sm text-white/40 mb-5">Average time to full report</div>
                {/* Mini timeline */}
                <div className="space-y-2">
                  {[
                    { step: "Prompt received", time: "0s", w: "5%" },
                    { step: "Sources crawled", time: "45s", w: "35%" },
                    { step: "Analysis complete", time: "2m", w: "65%" },
                    { step: "Report exported", time: "4m", w: "100%" },
                  ].map((s, i) => (
                    <div key={i}>
                      <div className="flex justify-between mb-0.5">
                        <span className="text-[9px] text-white/30">{s.step}</span>
                        <span className="text-[9px] text-white/20 font-mono">{s.time}</span>
                      </div>
                      <div className="h-1 rounded-full bg-white/[0.04] overflow-hidden">
                        <div className="h-full rounded-full bg-gradient-to-r from-[#8ECAE6]/30 to-[#8ECAE6]/10 transition-all duration-1000" style={{ width: s.w }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Card 4 — AI Models */}
              <div className="group relative rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.08] transition-all duration-500 p-6">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#E07A5F]/15 to-transparent" />
                <div className="flex items-center gap-2 mb-4">
                  <Layers className="w-4 h-4 text-white/25" />
                  <span className="text-[10px] text-white/30 uppercase tracking-wider">Multi-Model AI</span>
                </div>
                <div className="text-4xl font-light text-white/90 mb-1">4<span className="text-lg text-white/40">+</span></div>
                <div className="text-sm text-white/40 mb-5">AI models in parallel</div>
                <div className="space-y-2">
                  {[
                    { label: "Real-time signals", color: "#E07A5F" },
                    { label: "Deep analysis", color: "#6b9b8a" },
                    { label: "Creative synthesis", color: "#C9A96E" },
                    { label: "Data structuring", color: "#8ECAE6" },
                  ].map((m, i) => (
                    <div key={i} className="flex items-center gap-2.5">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: `${m.color}50` }} />
                      <span className="text-[11px] text-white/35">{m.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Card 5 — Wide: Source-backed */}
              <div className="lg:col-span-2 group relative rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.08] transition-all duration-500 p-6">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#A3B18A]/15 to-transparent" />
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-4 h-4 text-white/25" />
                      <span className="text-[10px] text-white/30 uppercase tracking-wider">Source-Backed Intelligence</span>
                    </div>
                    <h3 className="text-lg font-medium text-white/85 mb-2">Every insight is traceable</h3>
                    <p className="text-sm text-white/35 max-w-md leading-relaxed">Sources, citations, and confidence levels included in every output. Know exactly where each data point comes from.</p>
                  </div>
                  <div className="hidden sm:flex items-center gap-3 ml-6">
                    {[
                      { n: "47", label: "Sources" },
                      { n: "98%", label: "Accuracy" },
                      { n: "24/7", label: "Monitoring" },
                    ].map((s, i) => (
                      <div key={i} className="text-center px-4 py-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                        <div className="text-lg font-light text-white/70">{s.n}</div>
                        <div className="text-[9px] text-white/25 uppercase tracking-wider">{s.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* CTAs */}
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
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/domains"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "bg-[#141414] border border-white/[0.10] text-white/80",
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
      {/* SECTION 3 — Capabilities Grid */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-14 lg:py-20 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="text-center mb-10 lg:mb-14">
              <p className="text-xs text-white/30 uppercase tracking-[0.2em] mb-3">What We Deliver</p>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                Intelligence, not just answers
              </h2>
              <p className="text-white/40 text-base max-w-xl mx-auto mt-4 leading-relaxed">
                McLeuker AI combines multiple AI models, real-time data sources, and fashion domain expertise to deliver research you can act on.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {capabilities.map((cap, i) => {
                const Icon = cap.icon;
                return (
                  <div
                    key={i}
                    className="group p-6 rounded-2xl bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.08] transition-all duration-300"
                  >
                    <div className="w-10 h-10 rounded-xl bg-white/[0.04] border border-white/[0.06] flex items-center justify-center mb-4 group-hover:border-white/[0.12] transition-colors">
                      <Icon className="w-5 h-5 text-white/40" />
                    </div>
                    <h3 className="text-base font-medium text-white/[0.88] mb-2">{cap.title}</h3>
                    <p className="text-sm text-white/40 leading-relaxed">{cap.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 4 — Domain Carousel */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-12 lg:py-16 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="flex items-end justify-between mb-8">
              <div>
                <p className="text-xs text-white/30 uppercase tracking-[0.2em] mb-3">Specialized Intelligence</p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                  10 Domains. One Platform.
                </h2>
              </div>
              <div className="hidden sm:flex items-center gap-2">
                <button
                  onClick={() => domainScroll.scroll("left")}
                  disabled={!domainScroll.canScrollLeft}
                  className="w-10 h-10 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/40 hover:text-white/70 hover:border-white/15 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => domainScroll.scroll("right")}
                  disabled={!domainScroll.canScrollRight}
                  className="w-10 h-10 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/40 hover:text-white/70 hover:border-white/15 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div
          ref={domainScroll.ref}
          className="flex gap-4 overflow-x-auto scrollbar-hide px-6 lg:px-12 pb-4 snap-x snap-mandatory"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          <div className="flex-shrink-0 w-[calc((100vw-1200px)/2-24px)] hidden xl:block" />
          {domains.map((domain, i) => (
            <Link key={i} href={`/domain/${domain.slug}`} className="group flex-shrink-0 w-[260px] sm:w-[300px] snap-start">
              <div className="relative h-[360px] sm:h-[400px] rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] group-hover:border-white/[0.08] transition-all duration-300">
                <div className="absolute inset-0">
                  <Image src={domain.image} alt={domain.name} fill className="object-cover grayscale brightness-[0.5] group-hover:brightness-[0.6] group-hover:scale-105 transition-all duration-700" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
                </div>
                <div className="absolute inset-0 flex flex-col justify-end p-6">
                  <p className="text-[10px] text-white/25 uppercase tracking-[0.15em] mb-2">Domain</p>
                  <h3 className="text-xl font-medium text-white/[0.92] mb-2">{domain.name}</h3>
                  <p className="text-sm text-white/40 leading-relaxed mb-4">{domain.description}</p>
                  <div className="flex items-center gap-2 text-white/30 text-sm opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 transition-all duration-300">
                    <span>Explore</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </Link>
          ))}
          <div className="flex-shrink-0 w-6 lg:w-12 xl:w-[calc((100vw-1200px)/2-24px)]" />
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 5 — How It Works */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-12 lg:py-16 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="text-center mb-10 lg:mb-14">
              <p className="text-xs text-white/30 uppercase tracking-[0.2em] mb-3">The Process</p>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                From prompt to intelligence in minutes
              </h2>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {steps.map((step, i) => {
                const Icon = step.icon;
                return (
                  <div key={i} className="relative group">
                    {i < steps.length - 1 && (
                      <div className="hidden lg:block absolute top-10 left-[calc(50%+40px)] w-[calc(100%-40px)] h-px bg-gradient-to-r from-white/[0.06] to-transparent" />
                    )}
                    <div className="text-center lg:text-left">
                      <div className="flex items-center justify-center lg:justify-start gap-4 mb-5">
                        <div className="w-16 h-16 rounded-2xl bg-[#0C0C0C] border border-white/[0.06] flex items-center justify-center group-hover:border-white/[0.12] transition-colors relative">
                          <Icon className="w-6 h-6 text-white/35" />
                          <span className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-[10px] text-white/50 font-medium">
                            {step.number}
                          </span>
                        </div>
                      </div>
                      <h3 className="text-base font-medium text-white/[0.88] mb-2">{step.title}</h3>
                      <p className="text-sm text-white/35 leading-relaxed max-w-[240px] mx-auto lg:mx-0">{step.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="text-center mt-10">
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
      {/* SECTION 6 — Exportable Deliverables (Enhanced) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-16 lg:py-24 bg-[#0A0A0A] overflow-hidden">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            {/* Header */}
            <div className="grid lg:grid-cols-2 gap-8 lg:gap-16 items-start mb-12">
              <div>
                <p className="text-xs text-white/30 uppercase tracking-[0.2em] mb-3">Exportable Deliverables</p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92] leading-[1.1]">
                  Not chat responses.<br />Real documents.
                </h2>
              </div>
              <div className="lg:pt-8">
                <p className="text-white/40 text-base leading-relaxed mb-6">
                  Every research task produces structured, professional files — ready to share with your team, present to stakeholders, or archive for reference.
                </p>
                <div className="flex flex-wrap gap-3">
                  {[
                    { label: ".xlsx", color: "#217346" },
                    { label: ".pdf", color: "#D32F2F" },
                    { label: ".pptx", color: "#D04423" },
                    { label: ".docx", color: "#2B579A" },
                  ].map((f, i) => (
                    <span key={i} className="px-3 py-1.5 rounded-full border text-xs font-mono" style={{ borderColor: `${f.color}30`, color: `${f.color}cc`, backgroundColor: `${f.color}08` }}>
                      {f.label}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Backend Capabilities Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10">
              {[
                { icon: Code, label: "Code Generation", desc: "Python, SQL, formulas" },
                { icon: Paintbrush, label: "Visual Design", desc: "Charts, heatmaps, matrices" },
                { icon: Table, label: "Data Structuring", desc: "Tables, comparisons, rankings" },
                { icon: Database, label: "Source Integration", desc: "Live web, APIs, databases" },
              ].map((cap, i) => {
                const CapIcon = cap.icon;
                return (
                  <div key={i} className="group p-4 rounded-xl bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.08] transition-all">
                    <CapIcon className="w-5 h-5 text-white/30 mb-3 group-hover:text-white/50 transition-colors" />
                    <div className="text-sm font-medium text-white/70 mb-1">{cap.label}</div>
                    <div className="text-[11px] text-white/30">{cap.desc}</div>
                  </div>
                );
              })}
            </div>

            {/* Stacked overlapping cards — all 4 visible, click to expand */}
            <div className="relative" style={{ perspective: "1200px" }}>
              {/* Card stack */}
              <div className="relative h-[560px] md:h-[520px]">
                {[
                  { idx: 0, label: "Excel", icon: FileSpreadsheet, color: "#217346", file: "supplier_analysis.xlsx", meta: "3 sheets · 32 rows · Auto-filtered" },
                  { idx: 1, label: "PDF", icon: FileText, color: "#D32F2F", file: "trend_report.pdf", meta: "12 pages · 8 charts · 47 sources" },
                  { idx: 2, label: "Slides", icon: Presentation, color: "#D04423", file: "market_overview.pptx", meta: "15 slides · Stakeholder-ready" },
                  { idx: 3, label: "Word", icon: File, color: "#2B579A", file: "competitive_analysis.docx", meta: "5,200 words · 42 citations" },
                ].map((card) => {
                  const CardIcon = card.icon;
                  const isActive = activeOutput === card.idx;
                  const offset = card.idx - activeOutput;
                  return (
                    <div
                      key={card.idx}
                      onClick={() => setActiveOutput(card.idx)}
                      className="absolute inset-0 cursor-pointer transition-all duration-700 ease-out"
                      style={{
                        transform: isActive
                          ? "translateY(0) scale(1) rotateX(0)"
                          : `translateY(${offset * 12 + (offset > 0 ? 30 : -30)}px) scale(${1 - Math.abs(offset) * 0.03}) rotateX(${offset * 2}deg)`,
                        zIndex: isActive ? 40 : 30 - Math.abs(offset) * 10,
                        opacity: Math.abs(offset) > 2 ? 0 : 1 - Math.abs(offset) * 0.15,
                        filter: isActive ? "none" : `brightness(${0.7 - Math.abs(offset) * 0.1})`,
                      }}
                    >
                      <div className={cn(
                        "h-full rounded-2xl overflow-hidden border transition-all duration-500",
                        isActive ? "bg-[#0C0C0C] border-white/[0.10] shadow-2xl shadow-black/50" : "bg-[#0A0A0A] border-white/[0.04]"
                      )}>
                        {/* Color bar */}
                        <div className="h-1" style={{ backgroundColor: `${card.color}${isActive ? '60' : '20'}` }} />
                        
                        {/* Header */}
                        <div className="flex items-center gap-3 px-6 py-3.5 border-b border-white/[0.04]">
                          <CardIcon className="w-5 h-5" style={{ color: card.color }} />
                          <span className="text-sm font-medium text-white/80">{card.file}</span>
                          <span className="ml-auto text-[10px] text-white/25 font-mono hidden sm:inline">{card.meta}</span>
                          <span className="ml-auto sm:ml-2 text-[10px] font-mono px-2 py-0.5 rounded" style={{ color: card.color, backgroundColor: `${card.color}12` }}>{card.label}</span>
                        </div>

                        {/* Content — only render active for performance */}
                        <div className={cn("transition-opacity duration-300", isActive ? "opacity-100" : "opacity-40")}>
                          {/* EXCEL content — Enhanced */}
                          {card.idx === 0 && (
                            <div>
                              {/* Toolbar */}
                              <div className="flex items-center gap-2 px-4 py-2 border-b border-white/[0.03]">
                                <div className="flex items-center gap-1.5">
                                  <Filter className="w-3 h-3 text-[#217346]/60" />
                                  <span className="text-[9px] text-white/25">Auto-filter</span>
                                </div>
                                <div className="w-px h-3 bg-white/[0.06]" />
                                <div className="flex items-center gap-1.5">
                                  <SortAsc className="w-3 h-3 text-[#217346]/60" />
                                  <span className="text-[9px] text-white/25">Sort A-Z</span>
                                </div>
                                <div className="w-px h-3 bg-white/[0.06]" />
                                <div className="flex items-center gap-1.5">
                                  <BarChart className="w-3 h-3 text-[#217346]/60" />
                                  <span className="text-[9px] text-white/25">Pivot</span>
                                </div>
                                <div className="ml-auto flex items-center gap-1.5">
                                  <CheckCircle className="w-3 h-3 text-[#217346]/40" />
                                  <span className="text-[9px] text-white/20">Formulas included</span>
                                </div>
                              </div>
                              <div className="flex gap-0 px-4 pt-2">
                                {["Suppliers", "Pricing Matrix", "Certifications"].map((tab, i) => (
                                  <div key={i} className={cn(
                                    "px-4 py-1.5 text-[11px] rounded-t-lg border border-b-0",
                                    i === 0 ? "bg-[#0F0F0F] border-white/[0.06] text-white/60" : "bg-transparent border-transparent text-white/25"
                                  )}>{tab}</div>
                                ))}
                              </div>
                              <div className="mx-4 mb-4 rounded-b-lg border border-white/[0.04] overflow-hidden">
                                <div className="grid grid-cols-6 bg-[#217346]/[0.08]">
                                  {["#", "Supplier", "Country", "MOQ", "Certification", "Lead Time"].map((h, j) => (
                                    <div key={j} className="px-3 py-2 text-[10px] font-semibold text-white/50 uppercase tracking-wider border-r border-white/[0.03] last:border-r-0">{h}</div>
                                  ))}
                                </div>
                                {[
                                  ["1", "Candiani Denim", "Italy", "300 units", "GOTS, OEKO-TEX", "6 weeks"],
                                  ["2", "Tejidos Royo", "Spain", "500 units", "OEKO-TEX 100", "4 weeks"],
                                  ["3", "Advance Denim", "Portugal", "200 units", "BCI, EU Ecolabel", "5 weeks"],
                                  ["4", "Orta Anadolu", "Turkey", "1,000 units", "GOTS, GRS", "3 weeks"],
                                  ["5", "Artistic Milliners", "Pakistan", "500 units", "WRAP, BSCI", "8 weeks"],
                                ].map((row, j) => (
                                  <div key={j} className={cn("grid grid-cols-6 border-t border-white/[0.03]", j % 2 === 1 && "bg-white/[0.01]")}>
                                    {row.map((cell, k) => (
                                      <div key={k} className="px-3 py-2 text-[11px] text-white/45 border-r border-white/[0.02] last:border-r-0 truncate">{cell}</div>
                                    ))}
                                  </div>
                                ))}
                                <div className="px-3 py-2 text-[10px] text-white/20 bg-[#217346]/[0.04] border-t border-white/[0.04]">
                                  + 27 more rows across 3 sheets · Formulas included · Ready to filter
                                </div>
                              </div>
                            </div>
                          )}

                          {/* PDF content — Enhanced */}
                          {card.idx === 1 && (
                            <div className="p-5">
                              <div className="grid md:grid-cols-2 gap-4">
                                <div className="bg-[#111] rounded-xl border border-white/[0.04] p-5">
                                  <div className="w-12 h-0.5 rounded-full bg-[#D32F2F]/40 mb-3" />
                                  <div className="text-[10px] text-white/20 uppercase tracking-wider mb-1">McLeuker AI Report</div>
                                  <div className="text-sm text-white/70 font-medium mb-4">SS26 Womenswear Trend Analysis</div>
                                  <div className="space-y-2.5">
                                    {["Executive Summary", "Key Findings", "Trend Analysis", "Competitive Landscape", "Recommendations"].map((s, j) => (
                                      <div key={j} className="flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full bg-[#D32F2F]/30" />
                                        <span className="text-[11px] text-white/40 flex-1">{s}</span>
                                        <div className="flex-1 border-b border-dotted border-white/[0.04]" />
                                        <span className="text-[10px] text-white/20">{j * 2 + 1}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                                <div className="bg-[#111] rounded-xl border border-white/[0.04] p-5">
                                  <div className="flex items-center justify-between mb-3">
                                    <div>
                                      <div className="text-[10px] text-white/20 uppercase tracking-wider mb-1">Page 3</div>
                                      <div className="text-xs text-white/50 font-medium">Trend Heatmap by Region</div>
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <PieChart className="w-3 h-3 text-[#D32F2F]/40" />
                                      <LineChart className="w-3 h-3 text-[#D32F2F]/30" />
                                    </div>
                                  </div>
                                  <div className="space-y-2">
                                    {[
                                      { label: "Oversized Tailoring", w: "85%" },
                                      { label: "Sheer Fabrics", w: "72%" },
                                      { label: "Burgundy Tones", w: "68%" },
                                      { label: "Utility Details", w: "55%" },
                                      { label: "Metallic Accents", w: "45%" },
                                    ].map((bar, j) => (
                                      <div key={j}>
                                        <div className="flex justify-between mb-0.5">
                                          <span className="text-[9px] text-white/35">{bar.label}</span>
                                          <span className="text-[9px] text-white/20">{bar.w}</span>
                                        </div>
                                        <div className="h-2 rounded-full bg-white/[0.04] overflow-hidden">
                                          <div className="h-full rounded-full bg-gradient-to-r from-[#D32F2F]/40 to-[#D32F2F]/20" style={{ width: bar.w }} />
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                  <div className="text-[9px] text-white/15 mt-3">Source: McLeuker AI analysis of 47 runway shows</div>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Slides content — Enhanced */}
                          {card.idx === 2 && (
                            <div className="p-5">
                              <div className="grid grid-cols-3 md:grid-cols-5 gap-2.5">
                                {["Title & Overview", "Market Size $42B", "Competitive Map", "Trend Matrix", "Consumer Segments", "Regional Analysis", "Brand Positioning", "Growth Drivers", "Risk Factors", "Next Steps"].map((slide, j) => (
                                  <div key={j} className={cn(
                                    "aspect-[16/10] rounded-lg border flex flex-col items-center justify-center p-2 transition-all duration-300",
                                    j === 0 ? "bg-[#D04423]/[0.08] border-[#D04423]/20" : "bg-[#111] border-white/[0.04] hover:border-white/[0.08]"
                                  )}>
                                    <div className="w-full h-0.5 rounded-full mb-1.5" style={{ backgroundColor: j === 0 ? "#D04423" : "#ffffff08" }} />
                                    <span className="text-[8px] text-white/35 text-center leading-tight">{slide}</span>
                                    {j === 0 && <div className="w-4 h-0.5 rounded-full bg-[#D04423]/30 mt-1" />}
                                  </div>
                                ))}
                              </div>
                              <div className="mt-3 text-center text-[10px] text-white/20">+ 5 more slides with appendix data and source citations</div>
                            </div>
                          )}

                          {/* Word content — Enhanced */}
                          {card.idx === 3 && (
                            <div className="p-5 max-w-2xl mx-auto">
                              <div className="bg-[#111] rounded-xl border border-white/[0.04] p-5">
                                <div className="flex items-center gap-2 mb-4">
                                  <div className="w-8 h-0.5 rounded-full bg-[#2B579A]/40" />
                                  <div className="w-16 h-0.5 rounded-full bg-[#2B579A]/20" />
                                </div>
                                {["1. Introduction", "2. Methodology", "3. Key Findings", "4. Competitive Analysis", "5. Appendix & Sources"].map((section, j) => (
                                  <div key={j} className="mb-3">
                                    <div className="text-sm text-white/60 font-medium mb-1">{section}</div>
                                    <div className="space-y-1">
                                      {Array.from({ length: j === 2 ? 4 : j === 4 ? 1 : 2 }).map((_, l) => (
                                        <div key={l} className="h-2 rounded-full bg-white/[0.03]" style={{ width: `${95 - l * 5 - j * 2}%` }} />
                                      ))}
                                    </div>
                                  </div>
                                ))}
                                <div className="mt-3 pt-3 border-t border-white/[0.04] text-[9px] text-white/15">
                                  [1] McKinsey State of Fashion 2026 · [2] BoF Insights · [3] Euromonitor ... +39 more
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Navigation dots */}
              <div className="flex items-center justify-center gap-2 mt-6">
                {[0, 1, 2, 3].map((i) => (
                  <button
                    key={i}
                    onClick={() => setActiveOutput(i)}
                    className={cn(
                      "transition-all duration-300 rounded-full",
                      activeOutput === i ? "w-8 h-2 bg-white/40" : "w-2 h-2 bg-white/10 hover:bg-white/20"
                    )}
                  />
                ))}
              </div>
            </div>

            {/* Generate CTA */}
            <div className="text-center mt-8">
              <Link
                href="/dashboard"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white font-medium",
                  "hover:from-[#3a4530] hover:to-[#353d2a] transition-all",
                  "shadow-lg shadow-[#2E3524]/15"
                )}
              >
                Generate Your First Report
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 7 — Platform Numbers (visual, no model names) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-10 lg:py-14 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                { value: "10", label: "Specialized Domains", icon: Globe, detail: "Fashion to Lifestyle" },
                { value: "4+", label: "AI Models in Parallel", icon: Brain, detail: "Parallel processing" },
                { value: "<5min", label: "Avg. Research Time", icon: Clock, detail: "From prompt to report" },
                { value: "24/7", label: "Live Signal Monitoring", icon: Zap, detail: "Across all sources" },
              ].map((metric, i) => {
                const MetricIcon = metric.icon;
                return (
                  <div key={i} className="relative group p-5 rounded-xl bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.08] transition-all text-center overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-white/[0.01] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="relative">
                      <MetricIcon className="w-5 h-5 text-white/20 mx-auto mb-3" />
                      <div className="text-2xl lg:text-3xl font-light text-white/[0.88] mb-1 tracking-tight">{metric.value}</div>
                      <div className="text-xs text-white/50 font-medium mb-0.5">{metric.label}</div>
                      <div className="text-[10px] text-white/25">{metric.detail}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 8 — Who It's For (expanded + horizontal scroll) */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-12 lg:py-16 bg-[#0A0A0A] overflow-hidden">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="flex items-end justify-between mb-8">
              <div>
                <p className="text-xs text-white/30 uppercase tracking-[0.2em] mb-3">Who It&apos;s For</p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                  Built for every role in the industry
                </h2>
                <p className="text-white/35 text-base max-w-lg mt-3 leading-relaxed">
                  From creative directors to fashion students — one platform for everyone who needs fashion intelligence.
                </p>
              </div>
              <div className="hidden sm:flex items-center gap-2">
                <button
                  onClick={() => useCaseScroll.scroll("left")}
                  disabled={!useCaseScroll.canScrollLeft}
                  className="w-9 h-9 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/40 hover:text-white/70 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => useCaseScroll.scroll("right")}
                  disabled={!useCaseScroll.canScrollRight}
                  className="w-9 h-9 rounded-full bg-[#0C0C0C] border border-white/[0.08] flex items-center justify-center text-white/40 hover:text-white/70 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Full-bleed scrollable use case cards — 10 roles */}
        <div
          ref={useCaseScroll.ref}
          className="flex gap-4 overflow-x-auto scrollbar-hide px-6 lg:px-12 pb-4 snap-x snap-mandatory"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          <div className="flex-shrink-0 w-[calc((100vw-1200px)/2-24px)] hidden xl:block" />
          
          {useCases.map((uc, i) => {
            const Icon = uc.icon;
            return (
              <div key={i} className="group flex-shrink-0 w-[280px] sm:w-[320px] snap-start">
                <div className="relative h-[420px] rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] hover:border-white/[0.10] transition-all duration-300">
                  <div className="absolute inset-0">
                    <Image
                      src={uc.image}
                      alt={uc.role}
                      fill
                      className="object-cover grayscale brightness-[0.35] group-hover:brightness-[0.45] group-hover:scale-105 transition-all duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0C0C0C] via-[#0C0C0C]/85 to-transparent" />
                  </div>
                  
                  <div className="absolute top-0 left-0 right-0 h-0.5" style={{ backgroundColor: `${uc.accent}40` }} />
                  
                  <div className="absolute inset-0 flex flex-col justify-end p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${uc.accent}15`, border: `1px solid ${uc.accent}25` }}>
                        <Icon className="w-4 h-4" style={{ color: `${uc.accent}90` }} />
                      </div>
                      <span className="text-sm font-medium text-white/85">{uc.role}</span>
                    </div>
                    
                    <div className="mb-3">
                      <span className="text-[10px] text-white/25 uppercase tracking-wider">Task</span>
                      <p className="text-[13px] text-white/50 leading-relaxed mt-0.5">{uc.task}</p>
                    </div>
                    
                    <div className="p-3 rounded-xl bg-white/[0.04] border border-white/[0.06]">
                      <span className="text-[10px] text-white/30 uppercase tracking-wider">You Get</span>
                      <p className="text-[13px] text-white/70 leading-relaxed mt-0.5">{uc.result}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
          
          <div className="flex-shrink-0 w-6 lg:w-12 xl:w-[calc((100vw-1200px)/2-24px)]" />
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 9 — Blog Preview */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="py-12 lg:py-16 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <div className="flex items-end justify-between mb-8">
              <div>
                <p className="text-xs text-white/30 uppercase tracking-[0.2em] mb-3">Insights & Analysis</p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                  From the McLeuker Journal
                </h2>
              </div>
              <Link
                href="/blog"
                className="hidden sm:inline-flex items-center gap-2 text-sm text-white/40 hover:text-white/60 transition-colors"
              >
                View All
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="grid md:grid-cols-3 gap-5">
              {recentPosts.map((post, i) => (
                <Link key={i} href={`/blog/${post.slug}`} className="group">
                  <div className="rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] group-hover:border-white/[0.08] transition-all duration-300">
                    <div className="relative h-[180px] overflow-hidden">
                      <Image
                        src={post.image}
                        alt={post.title}
                        fill
                        className="object-cover grayscale brightness-[0.6] group-hover:brightness-[0.7] group-hover:scale-105 transition-all duration-700"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-[#0C0C0C] to-transparent" />
                      <div className="absolute top-4 left-4">
                        <span className="px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-sm text-[10px] text-white/60 border border-white/[0.06]">
                          {post.category}
                        </span>
                      </div>
                    </div>
                    <div className="p-5">
                      <div className="flex items-center gap-3 text-[10px] text-white/25 mb-3">
                        <Clock className="w-3 h-3" />
                        <span>{post.readTime}</span>
                        <span className="w-0.5 h-0.5 rounded-full bg-white/15" />
                        <span>{new Date(post.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</span>
                      </div>
                      <h3 className="text-sm font-medium text-white/[0.85] mb-2 group-hover:text-white/95 transition-colors line-clamp-2">
                        {post.title}
                      </h3>
                      <p className="text-xs text-white/35 leading-relaxed line-clamp-2">{post.excerpt}</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            <div className="text-center mt-6 sm:hidden">
              <Link href="/blog" className="inline-flex items-center gap-2 text-sm text-white/40 hover:text-white/60 transition-colors">
                View All Posts
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 10 — Final CTA */}
      {/* ═══════════════════════════════════════════════════════ */}
      <section className="relative py-20 lg:py-28 bg-[#070707] overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[600px] h-[600px] rounded-full bg-white/[0.01] blur-[120px]" />
        </div>
        
        <div className="relative z-10 container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-5 leading-[1.05]">
              Your next research task,<br />solved in minutes
            </h2>
            <p className="text-white/40 text-lg mb-10 max-w-xl mx-auto leading-relaxed">
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
                  "bg-[#141414] border border-white/[0.08] text-white/70",
                  "hover:bg-white/[0.04] hover:border-white/[0.15] transition-colors"
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
