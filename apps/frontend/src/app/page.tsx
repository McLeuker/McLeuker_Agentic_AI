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

const services = [
  {
    title: "Trend Forecasting",
    description: "AI-powered analysis of global fashion trends, from runway to street style."
  },
  {
    title: "Supplier Intelligence",
    description: "Comprehensive research and vetting of sustainable suppliers worldwide."
  },
  {
    title: "Market Analysis",
    description: "Deep insights into competitive landscapes and growth opportunities."
  },
  {
    title: "Sustainability Consulting",
    description: "Expert guidance on certifications, impact measurement, and ESG compliance."
  }
];

const testimonials = [
  {
    quote: "McLeuker AI transformed how we approach trend research. What took weeks now takes hours.",
    author: "Creative Director",
    company: "European Fashion House"
  },
  {
    quote: "The supplier intelligence reports are incredibly thorough. A game-changer for our sourcing team.",
    author: "Head of Procurement",
    company: "Luxury Accessories Brand"
  },
  {
    quote: "Finally, an AI tool built by people who understand fashion. The outputs are genuinely useful.",
    author: "Brand Strategy Lead",
    company: "Sustainable Fashion Label"
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

      {/* Hero Section - Try McLeuker AI */}
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

            {/* Interactive Input - McLeuker Green Ombre */}
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
                    "bg-gradient-to-r from-[#3d655c] to-[#3d665c] text-white",
                    "hover:from-[#1a8a62] hover:to-[#2d7a35]",
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
                        <div className="flex-shrink-0 w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-white/[0.08] flex items-center justify-center group-hover:bg-[#3d655c]/20 transition-colors">
                          <IconComponent className="w-5 h-5 sm:w-6 sm:h-6 text-white/70 group-hover:text-[#6b9b8a]" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm sm:text-base font-medium text-white/[0.92] mb-1 sm:mb-1.5">
                            {suggestion.title}
                          </p>
                          <p className="text-xs sm:text-sm text-white/55 leading-relaxed line-clamp-2">
                            {suggestion.prompt}
                          </p>
                        </div>
                        <ArrowRight className="w-4 h-4 text-white/30 group-hover:text-[#3d655c] group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Hero Section - Fashion Intelligence with Runway Image */}
      <section className="relative min-h-[70vh] lg:min-h-[80vh] flex items-center justify-center overflow-hidden">
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
        <div className="relative z-10 container mx-auto px-6 lg:px-12 py-20 lg:py-32">
          <div className="max-w-4xl mx-auto text-center">
            {/* Tagline Badge - Updated with green accent */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#141414]/80 backdrop-blur-sm border border-[#3d655c]/30 mb-8 lg:mb-10">
              <Sparkles className="w-4 h-4 text-[#6b9b8a]" />
              <span className="text-sm text-white/70 tracking-wide">
                AI & Sustainability for Fashion
              </span>
            </div>

            {/* Main Headline */}
            <h2 className="font-editorial text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-white/[0.92] mb-6 lg:mb-8 leading-[1.05]">
              The Future of<br />Fashion Intelligence
            </h2>

            {/* Subheadline */}
            <p className="text-base md:text-lg lg:text-xl text-white/65 mb-10 lg:mb-12 max-w-2xl mx-auto leading-relaxed">
              From a single prompt to finished reports, sourcing sheets, and presentation decks. 
              AI-powered research for fashion professionals who demand excellence.
            </p>

            {/* CTAs - Updated with green primary button */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/dashboard"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "bg-gradient-to-r from-[#3d655c] to-[#3d665c] text-white font-medium",
                  "hover:from-[#1a8a62] hover:to-[#2d7a35] transition-all",
                  "shadow-lg shadow-[#3d655c]/20"
                )}
              >
                Open Dashboard
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/domains"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                  "border border-white/[0.18] text-white/90",
                  "hover:bg-[#3d655c]/10 hover:border-[#3d655c]/30 transition-colors"
                )}
              >
                Explore Domains
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Quote Section */}
      <section className="py-32 lg:py-40 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <blockquote className="max-w-4xl mx-auto text-center">
            <p className="font-editorial text-3xl md:text-4xl lg:text-5xl text-white/[0.92] leading-[1.2]">
              &ldquo;We believe fashion intelligence should be as refined as the industry it serves.&rdquo;
            </p>
            <footer className="mt-8 text-white/50 text-lg">
              — McLeuker AI
            </footer>
          </blockquote>
        </div>
      </section>

      {/* Solutions Section - Updated with bubble gradient variations */}
      <section className="py-24 lg:py-32 bg-[#0B0B0B]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1120px] mx-auto">
            {/* Section Header */}
            <div className="text-center mb-20">
              <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-4">
                Our Expertise
              </p>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                Comprehensive Solutions
              </h2>
            </div>

            {/* Services Grid - Updated with bubble gradient variations */}
            <div className="grid md:grid-cols-2 gap-8 lg:gap-10">
              {services.map((service, i) => (
                <div 
                  key={i} 
                  className={cn(
                    "group p-8 lg:p-10 rounded-[20px] cursor-pointer",
                    "mcleuker-bubble",
                    i % 4 === 0 && "mcleuker-bubble-v1",
                    i % 4 === 1 && "mcleuker-bubble-v2",
                    i % 4 === 2 && "mcleuker-bubble-v3",
                    i % 4 === 3 && "mcleuker-bubble-v4",
                    "transition-all duration-200"
                  )}
                >
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-6">
                      <span className="text-5xl font-editorial text-white/15 group-hover:text-[#3d655c]/30 transition-colors">
                        0{i + 1}
                      </span>
                      <ArrowRight className="w-5 h-5 text-white/40 group-hover:text-[#3d655c] group-hover:translate-x-1 transition-all" />
                    </div>
                    <h3 className="text-xl lg:text-2xl font-medium text-white/[0.92] mb-3">
                      {service.title}
                    </h3>
                    <p className="text-white/60 leading-relaxed">
                      {service.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* CTA - Updated with green accent */}
            <div className="text-center mt-16">
              <Link
                href="/solutions"
                className={cn(
                  "inline-flex items-center gap-2 px-8 py-3",
                  "bg-[#141414] border border-white/[0.10] rounded-full",
                  "text-white/80 hover:bg-[#3d655c]/10 hover:border-[#3d655c]/30",
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

      {/* Visual Showcase - Atelier (with Grayscale Image) */}
      <section className="py-24 lg:py-32 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
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
              <div className="lg:py-12">
                <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-4">
                  Crafted for Excellence
                </p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92] mb-8 leading-[1.1]">
                  Intelligence meets craftsmanship
                </h2>
                <p className="text-white/65 text-lg leading-relaxed mb-8">
                  Just as the finest ateliers combine tradition with innovation, 
                  McLeuker AI blends deep fashion expertise with cutting-edge artificial intelligence. 
                  Every insight is curated, every report is refined.
                </p>
                <ul className="space-y-4 mb-10">
                  {[
                    "Professional-grade reports and presentations",
                    "Structured data exports ready for your workflow",
                    "Real deliverables, not just conversations"
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-3 text-white/[0.85]">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#6b9b8a]"></div>
                      {item}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/signup"
                  className={cn(
                    "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                    "bg-gradient-to-r from-[#3d655c] to-[#3d665c] text-white font-medium",
                    "hover:from-[#1a8a62] hover:to-[#2d7a35] transition-all",
                    "shadow-lg shadow-[#3d655c]/20"
                  )}
                >
                  Start Your Journey
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Sustainability Focus - Dark with Grayscale Image */}
      <section className="py-24 lg:py-32 bg-[#0B0B0B]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
              {/* Content - Left on desktop */}
              <div className="lg:py-12 order-2 lg:order-1">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#141414] border border-[#3d655c]/30 mb-6">
                  <Leaf className="w-4 h-4 text-[#6b9b8a]" />
                  <span className="text-sm text-white/60">
                    Sustainability First
                  </span>
                </div>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92] mb-8 leading-[1.1]">
                  Fashion with purpose
                </h2>
                <p className="text-white/65 text-lg leading-relaxed mb-8">
                  Sustainability isn&apos;t an afterthought—it&apos;s woven into everything we do. 
                  From supplier certifications to impact assessments, we help brands 
                  make informed decisions that benefit both business and planet.
                </p>
                <div className="grid grid-cols-2 gap-8 mb-10">
                  <div>
                    <p className="text-4xl font-editorial text-[#6b9b8a] mb-2">85%</p>
                    <p className="text-sm text-white/50">Time saved on sustainability research</p>
                  </div>
                  <div>
                    <p className="text-4xl font-editorial text-[#6b9b8a] mb-2">100+</p>
                    <p className="text-sm text-white/50">Certification databases tracked</p>
                  </div>
                </div>
                <Link
                  href="/about"
                  className={cn(
                    "inline-flex items-center gap-2 px-8 py-3",
                    "bg-[#141414] border border-[#3d655c]/30 rounded-full",
                    "text-white hover:bg-[#3d655c]/10 hover:border-[#3d655c]/50",
                    "transition-colors"
                  )}
                >
                  Learn About Our Mission
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

      {/* Testimonials Section - Updated with bubble styling */}
      <section className="py-24 lg:py-32 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1120px] mx-auto">
            {/* Section Header */}
            <div className="text-center mb-20">
              <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-4">
                Trusted by Industry Leaders
              </p>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                What Our Clients Say
              </h2>
            </div>

            {/* Testimonials Grid - Updated with bubble gradient variations */}
            <div className="grid md:grid-cols-3 gap-6">
              {testimonials.map((testimonial, i) => (
                <div 
                  key={i} 
                  className={cn(
                    "p-8 rounded-[20px]",
                    "mcleuker-bubble",
                    i % 3 === 0 && "mcleuker-bubble-v1",
                    i % 3 === 1 && "mcleuker-bubble-v2",
                    i % 3 === 2 && "mcleuker-bubble-v3",
                    "shadow-[0_14px_40px_rgba(0,0,0,0.55)]"
                  )}
                >
                  <div className="relative z-10">
                    <blockquote className="text-white/[0.85] text-lg leading-relaxed mb-8">
                      &ldquo;{testimonial.quote}&rdquo;
                    </blockquote>
                    <div>
                      <p className="text-sm font-medium text-white/[0.92]">
                        {testimonial.author}
                      </p>
                      <p className="text-sm text-white/50">
                        {testimonial.company}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section - Updated with green accents */}
      <section className="py-32 lg:py-40 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-8 leading-[1.1]">
              Elevate your fashion intelligence
            </h2>
            <p className="text-white/60 text-lg mb-12 max-w-xl mx-auto">
              Join leading fashion brands transforming their research with AI-powered insights.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/signup"
                className={cn(
                  "inline-flex items-center gap-2 px-10 py-4 rounded-full",
                  "bg-gradient-to-r from-[#3d655c] to-[#3d665c] text-white font-medium",
                  "hover:from-[#1a8a62] hover:to-[#2d7a35] transition-all",
                  "shadow-lg shadow-[#3d655c]/20"
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
                  "hover:bg-[#3d655c]/10 hover:border-[#3d655c]/30 transition-colors"
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
