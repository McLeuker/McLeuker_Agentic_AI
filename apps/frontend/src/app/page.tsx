'use client';

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { 
  ArrowRight, 
  Sparkles, 
  TrendingUp, 
  Search, 
  BarChart3, 
  ShieldCheck,
  Leaf
} from "lucide-react";

const suggestionPrompts = [
  {
    icon: TrendingUp,
    title: "Trend Forecasting",
    prompt: "SS26 signals → 5 themes, key brands, and implications (sources where available).",
  },
  {
    icon: Search,
    title: "Beauty & Claims Intelligence",
    prompt: "Trending ingredients + claim-safe framing for skincare/makeup (sources where available).",
  },
  {
    icon: BarChart3,
    title: "Market Intelligence",
    prompt: "Build a luxury pricing ladder across EU/US/Asia in a clean table.",
  },
  {
    icon: ShieldCheck,
    title: "Supplier Research",
    prompt: "Find denim suppliers in Europe with MOQ targets + certifications (where available).",
  }
];

const services = [
  {
    title: "Trend & Signal Forecasting",
    description: "Synthesize runway, brand, and consumer signals into clear themes and what they mean."
  },
  {
    title: "Beauty & Claims Intelligence",
    description: "Ingredient trends, category shifts, and careful claims-aware summaries."
  },
  {
    title: "Competitive & Pricing Analysis",
    description: "Positioning, hero products, pricing ladders, and market moves — formatted for decisions."
  },
  {
    title: "Sourcing & Materials Intelligence",
    description: "Supplier discovery and materials scanning with practical constraints (where available)."
  }
];

const testimonials = [
  {
    quote: "SS26 signals summarized into themes + key brands + next steps.",
    author: "Example workflow",
    company: ""
  },
  {
    quote: "Competitive scan with pricing ladder formatted for quick sharing.",
    author: "Example workflow",
    company: ""
  },
  {
    quote: "Beauty ingredient trend summary with claims-aware framing.",
    author: "Example workflow",
    company: ""
  }
];

export default function LandingPage() {
  const [prompt, setPrompt] = useState("");
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      sessionStorage.setItem("domainPrompt", prompt);
      router.push("/dashboard");
    }
  };

  const handlePromptClick = (promptText: string) => {
    sessionStorage.setItem("domainPrompt", promptText);
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen bg-[#070707] overflow-x-hidden">
      <TopNavigation variant="marketing" />
      
      {/* Spacer for fixed nav */}
      <div className="h-16 lg:h-[72px]" />

      {/* SECTION 1: AI INPUT BUBBLE (must stay first) */}
      <section className="pt-20 lg:pt-24 pb-12 lg:pb-16 bg-[#0A0A0A]">
        <div className="container mx-auto px-4 sm:px-6 lg:px-12">
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-xs sm:text-sm text-white/50 uppercase tracking-[0.2em] mb-3 sm:mb-4">
              Fashion &bull; Beauty &bull; Lifestyle Intelligence
            </p>
            <h1 className="font-editorial text-3xl sm:text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-4 sm:mb-5 leading-[1.1]">
              Try McLeuker AI
            </h1>
            <p className="text-white/65 text-base sm:text-lg mb-7 sm:mb-8 max-w-2xl mx-auto px-2">
              One prompt &rarr; source-backed intelligence for fashion, beauty &amp; lifestyle.
            </p>

            {/* Interactive Input - McLeuker Green Ombre */}
            <form onSubmit={handleSubmit} className="max-w-2xl mx-auto mb-8 sm:mb-10 px-2">
              <div className="relative">
                <textarea 
                  value={prompt} 
                  onChange={e => setPrompt(e.target.value)} 
                  placeholder="e.g., SS26: synthesize runway + consumer signals into 5 themes…" 
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

            {/* Suggestion Prompts - Bubble gradient variations */}
            <div className="max-w-4xl mx-auto px-2">
              <p className="text-xs sm:text-sm text-white/40 uppercase tracking-[0.15em] mb-4 sm:mb-5">
                Try one of these examples
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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

      {/* SECTION 2: HERO / POSITIONING BLOCK */}
      <section className="relative min-h-[60vh] lg:min-h-[70vh] flex items-center justify-center overflow-hidden">
        {/* Background Image with Grayscale + Dark Overlay */}
        <div className="absolute inset-0">
          <Image 
            src="/images/hero-runway.jpg" 
            alt="Fashion runway" 
            fill
            className="object-cover grayscale contrast-[1.08] brightness-[0.85]"
            priority
          />
          {/* Dark gradient overlay for readability */}
          <div 
            className="absolute inset-0" 
            style={{
              background: 'linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.82) 60%, rgba(0,0,0,0.90) 100%)'
            }}
          />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 container mx-auto px-6 lg:px-12 py-16 lg:py-24">
          <div className="max-w-4xl mx-auto text-center">
            {/* Tagline Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#141414]/80 backdrop-blur-sm border border-[#2E3524]/30 mb-6 lg:mb-8">
              <Sparkles className="w-4 h-4 text-[#5c6652]" />
              <span className="text-sm text-white/70 tracking-wide">
                Fashion, Beauty &amp; Lifestyle Intelligence
              </span>
            </div>

            {/* Main Headline */}
            <h2 className="font-editorial text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-white/[0.92] mb-5 lg:mb-6 leading-[1.05]">
              The Future of<br />Industry Intelligence
            </h2>

            {/* Subheadline */}
            <p className="text-base md:text-lg lg:text-xl text-white/65 mb-8 lg:mb-10 max-w-2xl mx-auto leading-relaxed">
              Turn questions into structured decisions: trend briefs, competitor scans, retail signals, and product/ingredient insights — built for teams that move fast.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/signup"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white font-medium",
                  "hover:from-[#3a4530] hover:to-[#353d2a] transition-all",
                  "shadow-lg shadow-[#2E3524]/15"
                )}
              >
                Start Free Trial
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/solutions"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "border border-white/[0.18] text-white/90",
                  "hover:bg-[#2E3524]/10 hover:border-[#2E3524]/30 transition-colors"
                )}
              >
                Explore Solutions
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Quote Section */}
      <section className="py-20 lg:py-24 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <blockquote className="max-w-4xl mx-auto text-center">
            <p className="font-editorial text-3xl md:text-4xl lg:text-5xl text-white/[0.92] leading-[1.2]">
              &ldquo;We believe fashion intelligence should be as refined as the industry it serves.&rdquo;
            </p>
            <footer className="mt-6 text-white/50 text-lg">
              — McLeuker AI
            </footer>
          </blockquote>
        </div>
      </section>

      {/* SECTION 3: SOLUTIONS (4 cards) */}
      <section className="py-16 lg:py-24 bg-[#0B0B0B]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1120px] mx-auto">
            {/* Section Header */}
            <div className="text-center mb-14 lg:mb-16">
              <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-3">
                Our Expertise
              </p>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                Comprehensive Solutions
              </h2>
            </div>

            {/* Services Grid */}
            <div className="grid md:grid-cols-2 gap-6 lg:gap-8">
              {services.map((service, i) => (
                <div 
                  key={i} 
                  className={cn(
                    "group p-7 lg:p-8 rounded-[20px] cursor-pointer",
                    "mcleuker-bubble",
                    i % 4 === 0 && "mcleuker-bubble-v1",
                    i % 4 === 1 && "mcleuker-bubble-v2",
                    i % 4 === 2 && "mcleuker-bubble-v3",
                    i % 4 === 3 && "mcleuker-bubble-v4",
                    "transition-all duration-200"
                  )}
                >
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-5">
                      <span className="text-5xl font-editorial text-white/15 group-hover:text-[#2E3524]/30 transition-colors">
                        0{i + 1}
                      </span>
                      <ArrowRight className="w-5 h-5 text-white/40 group-hover:text-[#2E3524] group-hover:translate-x-1 transition-all" />
                    </div>
                    <h3 className="text-xl lg:text-2xl font-medium text-white/[0.92] mb-2.5">
                      {service.title}
                    </h3>
                    <p className="text-white/60 leading-relaxed">
                      {service.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* CTA */}
            <div className="text-center mt-12">
              <Link
                href="/solutions"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3",
                  "bg-[#141414] border border-white/[0.10] rounded-full",
                  "text-white/80 hover:bg-[#2E3524]/10 hover:border-[#2E3524]/30",
                  "transition-colors"
                )}
              >
                Explore All Solutions
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 4: CRAFTED FOR EXCELLENCE → Output-first */}
      <section className="py-16 lg:py-24 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
              {/* Image with Grayscale Filter */}
              <div className="relative rounded-[20px] overflow-hidden shadow-[0_14px_40px_rgba(0,0,0,0.55)] aspect-[4/5]">
                <Image 
                  src="/images/fashion-atelier.jpg" 
                  alt="Fashion atelier workspace" 
                  fill
                  className="object-cover grayscale contrast-105 brightness-90"
                />
              </div>

              {/* Content */}
              <div className="lg:py-8">
                <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-3">
                  Output-first
                </p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92] mb-6 leading-[1.1]">
                  Deliverables — not just answers
                </h2>
                <p className="text-white/65 text-lg leading-relaxed mb-6">
                  McLeuker AI uses a multi-model engine to research, compare, and format results into clear, shareable outputs for fashion and beauty teams.
                </p>
                <ul className="space-y-3.5 mb-8">
                  {[
                    "Clear takeaways and next steps",
                    "Structured tables for benchmarks and comparisons",
                    "Source-backed summaries (where available)"
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-3 text-white/[0.85]">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#5c6652]"></div>
                      {item}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/signup"
                  className={cn(
                    "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                    "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white font-medium",
                    "hover:from-[#3a4530] hover:to-[#353d2a] transition-all",
                    "shadow-lg shadow-[#2E3524]/15"
                  )}
                >
                  Start Free Trial
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 5: SUSTAINABILITY → Responsible Intelligence */}
      <section className="py-16 lg:py-24 bg-[#0B0B0B]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
              {/* Content - Left on desktop */}
              <div className="lg:py-8 order-2 lg:order-1">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#141414] border border-[#2E3524]/30 mb-5">
                  <Leaf className="w-4 h-4 text-[#5c6652]" />
                  <span className="text-sm text-white/60">
                    Responsible intelligence
                  </span>
                </div>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92] mb-6 leading-[1.1]">
                  Evidence-forward by default
                </h2>
                <p className="text-white/65 text-lg leading-relaxed mb-6">
                  Sustainability is one important lens — alongside trend, product, retail, and competitive intelligence. Outputs emphasize sources and clear assumptions.
                </p>
                <div className="grid grid-cols-2 gap-6 mb-8">
                  <div>
                    <p className="text-4xl font-editorial text-[#5c6652] mb-1.5">Faster</p>
                    <p className="text-sm text-white/50">Less time spent on manual research</p>
                  </div>
                  <div>
                    <p className="text-4xl font-editorial text-[#5c6652] mb-1.5">Multi-source</p>
                    <p className="text-sm text-white/50">Source-backed summaries across multiple inputs</p>
                  </div>
                </div>
                <Link
                  href="/about"
                  className={cn(
                    "inline-flex items-center gap-2 px-8 py-3",
                    "bg-[#141414] border border-[#2E3524]/30 rounded-full",
                    "text-white hover:bg-[#2E3524]/10 hover:border-[#2E3524]/50",
                    "transition-colors"
                  )}
                >
                  Learn More
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>

              {/* Image - Right on desktop (with Grayscale) */}
              <div className="relative rounded-[20px] overflow-hidden shadow-[0_14px_40px_rgba(0,0,0,0.55)] order-1 lg:order-2 aspect-[4/5]">
                <Image 
                  src="/images/sustainable-materials.jpg" 
                  alt="Sustainable fashion materials" 
                  fill
                  className="object-cover grayscale contrast-105 brightness-90"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 6: EXAMPLE OUTCOMES (was Testimonials) */}
      <section className="py-16 lg:py-24 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1120px] mx-auto">
            {/* Section Header */}
            <div className="text-center mb-14 lg:mb-16">
              <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-3">
                What it looks like
              </p>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                Example outcomes
              </h2>
            </div>

            {/* Testimonials Grid */}
            <div className="grid md:grid-cols-3 gap-5">
              {testimonials.map((testimonial, i) => (
                <div 
                  key={i} 
                  className={cn(
                    "p-7 rounded-[20px]",
                    "mcleuker-bubble",
                    i % 3 === 0 && "mcleuker-bubble-v1",
                    i % 3 === 1 && "mcleuker-bubble-v2",
                    i % 3 === 2 && "mcleuker-bubble-v3",
                    "shadow-[0_14px_40px_rgba(0,0,0,0.55)]"
                  )}
                >
                  <div className="relative z-10">
                    <blockquote className="text-white/[0.85] text-lg leading-relaxed mb-6">
                      &ldquo;{testimonial.quote}&rdquo;
                    </blockquote>
                    <div>
                      <p className="text-sm font-medium text-white/[0.70] italic">
                        {testimonial.author}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 7: FINAL CTA */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-6 leading-[1.1]">
              Elevate your fashion intelligence
            </h2>
            <p className="text-white/60 text-lg mb-10 max-w-xl mx-auto">
              Source-backed research for fashion, beauty &amp; lifestyle teams — powered by a multi-model engine with web + social + search signals (where available).
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/signup"
                className={cn(
                  "inline-flex items-center gap-2 px-10 py-4 rounded-full",
                  "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white font-medium",
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
                  "bg-[#141414] border border-white/[0.10] text-white",
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
