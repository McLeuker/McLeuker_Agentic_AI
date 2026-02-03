'use client';

import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { ArrowRight, Leaf, Target, Users, Sparkles } from "lucide-react";

const values = [
  {
    icon: Target,
    title: "Precision",
    description: "Every insight is meticulously researched and verified. We deliver accuracy that fashion professionals can rely on."
  },
  {
    icon: Leaf,
    title: "Sustainability",
    description: "Environmental responsibility is at our core. We help brands make decisions that benefit both business and planet."
  },
  {
    icon: Users,
    title: "Partnership",
    description: "We work alongside our clients, understanding their unique challenges and delivering tailored solutions."
  },
  {
    icon: Sparkles,
    title: "Innovation",
    description: "Combining cutting-edge AI with deep fashion expertise to transform how the industry approaches research."
  }
];

const capabilities = [
  { title: "Strategy & Planning", desc: "Strategic intelligence for collection planning, market entry, and brand positioning." },
  { title: "Sustainability", desc: "Environmental impact analysis, certification mapping, and ESG reporting support." },
  { title: "Circularity", desc: "Circular business model research, resale market analysis, and waste reduction strategies." },
  { title: "Traceability", desc: "Supply chain transparency, due diligence research, and compliance verification." },
  { title: "Sourcing", desc: "Supplier discovery, capability assessment, and partnership evaluation." },
  { title: "Market Intelligence", desc: "Competitive analysis, pricing benchmarks, and consumer trend insights." }
];

export default function AboutPage() {
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
              About McLeuker AI
            </p>
            <h1 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-6 leading-[1.1]">
              AI & Sustainability<br />for Fashion
            </h1>
            <p className="text-white/65 text-lg lg:text-xl max-w-2xl mx-auto leading-relaxed">
              We&apos;re building the future of fashion intelligence — where AI-powered insights 
              meet sustainable practices to help brands make smarter decisions.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-24 lg:py-32 bg-[#0B0B0B]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
              <div>
                <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-4">
                  Our Mission
                </p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92] mb-8 leading-[1.1]">
                  Empowering fashion with intelligence
                </h2>
                <p className="text-white/65 text-lg leading-relaxed mb-6">
                  At McLeuker AI, we believe that the fashion industry stands at a crossroads. 
                  The demand for faster trend cycles, sustainable practices, and data-driven 
                  decisions has never been greater.
                </p>
                <p className="text-white/65 text-lg leading-relaxed mb-6">
                  Our mission is to empower fashion professionals with AI-powered tools that 
                  transform complex research into actionable intelligence — all while keeping 
                  sustainability at the forefront.
                </p>
                <p className="text-white/65 text-lg leading-relaxed">
                  From trend forecasting to supplier research, we&apos;re building the comprehensive 
                  platform that modern fashion businesses need to thrive.
                </p>
              </div>
              
              {/* Stats */}
              <div className="p-10 lg:p-12 rounded-[20px] bg-gradient-to-b from-[#1A1A1A] to-[#141414] border border-white/[0.10] shadow-[0_14px_40px_rgba(0,0,0,0.55)]">
                <div className="space-y-10">
                  <div>
                    <p className="text-5xl lg:text-6xl font-editorial text-white/[0.92] mb-3">100+</p>
                    <p className="text-white/50">Fashion brands served</p>
                  </div>
                  <div className="border-t border-white/10 pt-10">
                    <p className="text-5xl lg:text-6xl font-editorial text-white/[0.92] mb-3">50K+</p>
                    <p className="text-white/50">Research tasks completed</p>
                  </div>
                  <div className="border-t border-white/10 pt-10">
                    <p className="text-5xl lg:text-6xl font-editorial text-white/[0.92] mb-3">85%</p>
                    <p className="text-white/50">Time saved on research</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="py-24 lg:py-32 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-20">
              <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-4">
                Our Capabilities
              </p>
              <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92]">
                Areas of Expertise
              </h2>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {capabilities.map((capability, i) => (
                <div 
                  key={i} 
                  className="p-6 lg:p-8 rounded-[20px] bg-gradient-to-b from-[#1A1A1A] to-[#141414] border border-white/[0.10] hover:border-white/[0.18] transition-all"
                >
                  <h3 className="text-lg font-medium text-white/[0.92] mb-3">
                    {capability.title}
                  </h3>
                  <p className="text-white/60 text-sm leading-relaxed">
                    {capability.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 lg:py-28 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="text-center mb-12 lg:mb-16">
            <p className="text-xs sm:text-sm text-white/40 uppercase tracking-[0.2em] mb-3">
              Our Values
            </p>
            <h2 className="font-editorial text-3xl md:text-4xl lg:text-5xl text-white/[0.92]">
              What Drives Us
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
            {values.map((value, i) => {
              const IconComponent = value.icon;
              return (
                <div
                  key={i}
                  className={cn(
                    "p-8 rounded-[20px]",
                    "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
                    "border border-white/[0.08]"
                  )}
                >
                  <div className="w-12 h-12 rounded-lg bg-white/[0.08] flex items-center justify-center mb-5">
                    <IconComponent className="w-6 h-6 text-white/70" />
                  </div>
                  <h3 className="text-xl font-medium text-white/[0.92] mb-3">
                    {value.title}
                  </h3>
                  <p className="text-white/55 leading-relaxed">
                    {value.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Vision Section with Image */}
      <section className="py-24 lg:py-32 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
              {/* Image */}
              <div className="relative rounded-[20px] overflow-hidden shadow-[0_14px_40px_rgba(0,0,0,0.55)] aspect-[4/5]">
                <Image 
                  src="/images/sustainable-materials.jpg" 
                  alt="Sustainable fashion materials" 
                  fill
                  className="object-cover grayscale contrast-105 brightness-90"
                />
              </div>

              {/* Content */}
              <div className="lg:py-12">
                <p className="text-sm text-white/50 uppercase tracking-[0.2em] mb-4">
                  Our Vision
                </p>
                <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92] mb-8 leading-[1.1]">
                  A sustainable future for fashion
                </h2>
                <p className="text-white/65 text-lg leading-relaxed mb-8">
                  We envision a fashion industry where every decision is informed by intelligent 
                  data, where sustainability isn&apos;t an afterthought but a foundation, and where 
                  professionals can focus on creativity while AI handles the research heavy lifting.
                </p>
                <div className="inline-flex items-center gap-3 px-5 py-3 rounded-full bg-[#141414] border border-white/[0.10]">
                  <Leaf className="w-5 h-5 text-white/60" />
                  <span className="text-white/80 font-medium">
                    Committed to net-zero by 2030
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 lg:py-40 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="font-editorial text-4xl md:text-5xl text-white/[0.92] mb-8 leading-[1.1]">
              Ready to transform your workflow?
            </h2>
            <p className="text-white/60 text-lg mb-12">
              Join leading fashion brands using McLeuker AI for smarter research.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link 
                href="/signup"
                className="inline-flex items-center px-10 py-4 text-base bg-white text-black hover:bg-white/90 rounded-lg font-medium transition-colors"
              >
                Get Started Free
                <ArrowRight className="h-4 w-4 ml-2" />
              </Link>
              <Link 
                href="/contact"
                className="inline-flex items-center px-10 py-4 text-base bg-[#141414] border border-white/[0.10] text-white hover:bg-[#1A1A1A] rounded-lg font-medium transition-colors"
              >
                Contact Us
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
