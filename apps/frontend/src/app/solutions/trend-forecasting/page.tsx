'use client';

import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { TrendingUp, ArrowRight, Check, Users } from "lucide-react";

const USE_CASES = [
  "Analyze runway collections across major fashion weeks for emerging themes",
  "Identify color palettes and material trends for upcoming seasons",
  "Track silhouette evolution across luxury, contemporary, and fast fashion",
  "Monitor social media and street style for early trend signals",
  "Compare trend adoption timelines across different markets",
  "Generate seasonal trend reports for internal presentations"
];

export default function TrendForecastingPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          {/* Hero */}
          <div className="max-w-3xl mx-auto text-center mb-16">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-b from-[#1A1A1A] to-[#141414] border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
              <TrendingUp className="h-8 w-8 text-white/80" />
            </div>
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Trend Forecasting
            </h1>
            <p className="text-white/70 text-lg leading-relaxed">
              Data-driven trend intelligence to inform design decisions, buying strategies, 
              and product development timelines.
            </p>
          </div>

          {/* Who it's for */}
          <div className="max-w-4xl mx-auto mb-16">
            <div className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-8 border border-white/[0.08]">
              <div className="flex items-center gap-3 mb-4">
                <Users className="h-5 w-5 text-white/60" />
                <h3 className="text-lg font-medium text-white">Who it&apos;s for</h3>
              </div>
              <p className="text-white/60 leading-relaxed">
                Creative directors, design teams, buyers, merchandisers, and product developers 
                who need to make informed decisions about upcoming collections and assortments.
              </p>
            </div>
          </div>

          {/* What you get */}
          <div className="max-w-4xl mx-auto mb-16">
            <h3 className="text-xl font-medium text-white mb-6">What you get</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {[
                "Runway analysis across 40+ fashion weeks",
                "Color trend reports with Pantone references",
                "Silhouette and proportion forecasts",
                "Material and texture trend maps",
                "Cross-market trend comparison",
                "Exportable reports for presentations"
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-3 bg-[#0D0D0D] rounded-xl p-4 border border-white/[0.05]">
                  <Check className="h-5 w-5 text-white/50 flex-shrink-0 mt-0.5" />
                  <span className="text-white/70 text-sm">{item}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Use Cases */}
          <div className="max-w-4xl mx-auto mb-16">
            <h3 className="text-xl font-medium text-white mb-6">Use cases</h3>
            <div className="space-y-3">
              {USE_CASES.map((useCase, i) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="text-white/30 text-sm font-mono w-6">{String(i + 1).padStart(2, '0')}</span>
                  <span className="text-white/60">{useCase}</span>
                </div>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="text-center">
            <Link 
              href="/dashboard"
              className="inline-flex items-center bg-white text-black hover:bg-white/90 px-8 py-4 rounded-lg text-base font-medium transition-colors"
            >
              Try Trend Forecasting
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
