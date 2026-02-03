'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { ArrowRight, TrendingUp, Search, BarChart3, Leaf } from "lucide-react";

const solutions = [
  {
    icon: TrendingUp,
    title: "Trend Forecasting",
    description: "AI-powered analysis of global fashion trends, from runway shows to street style. Stay ahead of the curve with predictive insights.",
    features: [
      "Runway trend analysis",
      "Color and material forecasting",
      "Consumer sentiment tracking",
      "Seasonal predictions"
    ],
    href: "/solutions/trend-forecasting"
  },
  {
    icon: Search,
    title: "Supplier Research",
    description: "Comprehensive research and vetting of suppliers worldwide. Find the right partners for your production needs.",
    features: [
      "Global supplier database",
      "Certification verification",
      "MOQ and pricing analysis",
      "Quality assessment"
    ],
    href: "/solutions/supplier-research"
  },
  {
    icon: BarChart3,
    title: "Market Analysis",
    description: "Deep insights into competitive landscapes, pricing strategies, and growth opportunities across markets.",
    features: [
      "Competitive intelligence",
      "Pricing benchmarks",
      "Market sizing",
      "Growth opportunity mapping"
    ],
    href: "/solutions/market-analysis"
  },
  {
    icon: Leaf,
    title: "Sustainability Insights",
    description: "Expert guidance on certifications, impact measurement, and ESG compliance for responsible fashion.",
    features: [
      "Certification tracking",
      "Impact assessment",
      "ESG compliance",
      "Sustainable sourcing"
    ],
    href: "/solutions/sustainability-insights"
  }
];

export default function SolutionsPage() {
  return (
    <div className="min-h-screen bg-[#070707]">
      <TopNavigation variant="marketing" />
      
      {/* Spacer for fixed nav */}
      <div className="h-16 lg:h-[72px]" />

      {/* Hero Section */}
      <section className="pt-24 lg:pt-32 pb-16 lg:pb-24 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-xs sm:text-sm text-white/50 uppercase tracking-[0.2em] mb-4">
              Our Solutions
            </p>
            <h1 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-6 leading-[1.1]">
              Comprehensive Fashion Intelligence
            </h1>
            <p className="text-white/65 text-lg lg:text-xl max-w-2xl mx-auto">
              From trend forecasting to sustainability consulting, we provide the insights you need to make informed decisions.
            </p>
          </div>
        </div>
      </section>

      {/* Solutions Grid */}
      <section className="py-16 lg:py-24 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {solutions.map((solution, i) => {
              const IconComponent = solution.icon;
              return (
                <Link
                  key={i}
                  href={solution.href}
                  className={cn(
                    "group p-8 rounded-[20px]",
                    "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
                    "border border-white/[0.08]",
                    "hover:border-white/[0.14] transition-all"
                  )}
                >
                  <div className="flex items-start justify-between mb-6">
                    <div className="w-14 h-14 rounded-xl bg-white/[0.08] flex items-center justify-center group-hover:bg-white/[0.12] transition-colors">
                      <IconComponent className="w-7 h-7 text-white/70" />
                    </div>
                    <ArrowRight className="w-5 h-5 text-white/30 group-hover:text-white/60 group-hover:translate-x-1 transition-all" />
                  </div>
                  
                  <h3 className="text-2xl font-editorial text-white/[0.92] mb-3">
                    {solution.title}
                  </h3>
                  <p className="text-white/55 leading-relaxed mb-6">
                    {solution.description}
                  </p>
                  
                  <ul className="space-y-2">
                    {solution.features.map((feature, j) => (
                      <li key={j} className="flex items-center gap-2 text-sm text-white/50">
                        <div className="w-1 h-1 rounded-full bg-white/40" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-28 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12 text-center">
          <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.92] mb-6">
            Ready to get started?
          </h2>
          <p className="text-white/65 text-lg mb-10 max-w-2xl mx-auto">
            Experience the power of AI-driven fashion intelligence.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className={cn(
                "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                "bg-white text-black font-medium",
                "hover:bg-white/90 transition-colors"
              )}
            >
              Try It Now
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/pricing"
              className={cn(
                "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                "border border-white/[0.18] text-white/90",
                "hover:bg-white/[0.08] transition-colors"
              )}
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
