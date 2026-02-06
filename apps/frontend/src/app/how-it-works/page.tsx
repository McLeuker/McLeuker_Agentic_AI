'use client';

import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { MessageSquare, Brain, FileText, ArrowRight, Check } from "lucide-react";

const STEPS = [
  {
    number: "01",
    title: "Ask",
    icon: MessageSquare,
    description: "Pose your research question in natural language. Be specific about the domain, timeframe, and depth of analysis you need.",
    examples: [
      "Analyze SS26 womenswear trends from Milan Fashion Week",
      "Find certified sustainable denim suppliers in Portugal with MOQ under 500 units",
      "Compare luxury handbag pricing strategies across Asian markets"
    ]
  },
  {
    number: "02",
    title: "Analyze",
    icon: Brain,
    description: "McLeuker AI processes your query through specialized domain models, cross-referencing industry data sources, trend signals, and market intelligence.",
    features: [
      "Domain-specific data sources",
      "Real-time market signals",
      "Cross-reference validation",
      "Contextual understanding"
    ]
  },
  {
    number: "03",
    title: "Deliver",
    icon: FileText,
    description: "Receive structured, actionable intelligence formatted for immediate use in presentations, reports, and strategic decisions.",
    outputs: [
      "Trend analysis reports",
      "Supplier comparison sheets",
      "Market sizing data",
      "Competitive intelligence briefs"
    ]
  }
];

export default function HowItWorksPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          {/* Hero */}
          <div className="max-w-3xl mx-auto text-center mb-20">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              How McLeuker AI Works
            </h1>
            <p className="text-white/70 text-lg leading-relaxed">
              Transform complex research into actionable intelligence through our streamlined 
              three-step process. No data science expertise required.
            </p>
          </div>

          {/* Steps */}
          <div className="max-w-4xl mx-auto space-y-16 mb-20">
            {STEPS.map((step) => {
              const IconComponent = step.icon;
              return (
                <div key={step.number} className="flex flex-col md:flex-row gap-8 items-start">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-b from-[#1A1A1A] to-[#141414] border border-white/[0.08] flex items-center justify-center">
                      <IconComponent className="h-7 w-7 text-white/80" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-baseline gap-3 mb-3">
                      <span className="text-white/30 text-sm font-mono">{step.number}</span>
                      <h3 className="text-2xl font-medium text-white">{step.title}</h3>
                    </div>
                    <p className="text-white/60 text-base leading-relaxed mb-4">
                      {step.description}
                    </p>
                    
                    {step.examples && (
                      <div className="bg-[#0D0D0D] rounded-xl p-4 border border-white/[0.05]">
                        <p className="text-white/40 text-xs uppercase tracking-wider mb-3">Example prompts</p>
                        <div className="space-y-2">
                          {step.examples.map((example, i) => (
                            <p key={i} className="text-white/50 text-sm">&ldquo;{example}&rdquo;</p>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {step.features && (
                      <div className="grid grid-cols-2 gap-2">
                        {step.features.map((feature, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <Check className="h-4 w-4 text-white/40" />
                            <span className="text-white/60 text-sm">{feature}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {step.outputs && (
                      <div className="grid grid-cols-2 gap-2">
                        {step.outputs.map((output, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-white/40" />
                            <span className="text-white/60 text-sm">{output}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Methodology */}
          <div className="max-w-3xl mx-auto mb-16">
            <div className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-8 border border-white/[0.08]">
              <h3 className="text-xl font-medium text-white mb-4">Our Methodology</h3>
              <p className="text-white/60 leading-relaxed mb-4">
                McLeuker AI combines large language models with curated industry data sources to deliver 
                accurate, contextual intelligence. Our systems are trained on fashion, beauty, and 
                sustainability-specific terminology and frameworks.
              </p>
              <p className="text-white/60 leading-relaxed">
                We continuously validate outputs against primary sources and industry benchmarks to ensure 
                reliability. When data is uncertain or unavailable, we clearly indicate limitations.
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="text-center">
            <Link 
              href="/signup"
              className="inline-flex items-center bg-white text-black hover:bg-white/90 px-8 py-4 rounded-lg text-base font-medium transition-colors"
            >
              Start Free Trial
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
