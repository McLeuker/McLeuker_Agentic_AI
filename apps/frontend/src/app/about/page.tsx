'use client';

import Link from "next/link";
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

const team = [
  {
    name: "Fashion Intelligence",
    role: "Our team combines decades of fashion industry experience with advanced AI expertise."
  },
  {
    name: "Sustainability Focus",
    role: "Dedicated specialists in sustainable fashion, certifications, and ESG compliance."
  },
  {
    name: "Technology Excellence",
    role: "Engineers and data scientists building the future of fashion research."
  }
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
              Redefining Fashion Intelligence
            </h1>
            <p className="text-white/65 text-lg lg:text-xl max-w-2xl mx-auto leading-relaxed">
              We believe fashion intelligence should be as refined as the industry it serves. 
              McLeuker AI combines deep fashion expertise with cutting-edge artificial intelligence 
              to deliver insights that transform how brands operate.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center max-w-6xl mx-auto">
            {/* Image placeholder */}
            <div className="aspect-[4/3] rounded-[20px] bg-gradient-to-br from-[#1A1A1A] to-[#0F0F0F] border border-white/[0.08]" />
            
            {/* Content */}
            <div>
              <p className="text-xs sm:text-sm text-white/40 uppercase tracking-[0.2em] mb-3">
                Our Mission
              </p>
              <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.92] mb-6">
                Intelligence that empowers
              </h2>
              <p className="text-white/65 leading-relaxed mb-6">
                The fashion industry faces unprecedented challenges—from rapidly shifting trends to 
                complex sustainability requirements. Traditional research methods can't keep pace.
              </p>
              <p className="text-white/65 leading-relaxed mb-8">
                McLeuker AI was founded to bridge this gap. We provide fashion professionals with 
                the intelligence they need to make informed decisions, faster than ever before.
              </p>
              <Link
                href="/contact"
                className={cn(
                  "inline-flex items-center gap-2 px-6 py-3 rounded-full",
                  "border border-white/[0.18] text-white/90",
                  "hover:bg-white/[0.08] transition-colors"
                )}
              >
                Get in Touch
                <ArrowRight className="w-4 h-4" />
              </Link>
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

      {/* Team Section */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="text-center mb-12 lg:mb-16">
            <p className="text-xs sm:text-sm text-white/40 uppercase tracking-[0.2em] mb-3">
              Our Expertise
            </p>
            <h2 className="font-editorial text-3xl md:text-4xl lg:text-5xl text-white/[0.92]">
              Built by Experts
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {team.map((member, i) => (
              <div
                key={i}
                className={cn(
                  "p-8 rounded-[20px] text-center",
                  "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
                  "border border-white/[0.08]"
                )}
              >
                <div className="w-16 h-16 rounded-full bg-white/[0.08] mx-auto mb-5" />
                <h3 className="text-lg font-medium text-white/[0.92] mb-2">
                  {member.name}
                </h3>
                <p className="text-sm text-white/55">
                  {member.role}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-28 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12 text-center">
          <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.92] mb-6">
            Ready to transform your research?
          </h2>
          <p className="text-white/65 text-lg mb-10 max-w-2xl mx-auto">
            Join leading fashion brands using McLeuker AI to stay ahead of trends and make smarter decisions.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/signup"
              className={cn(
                "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                "bg-white text-black font-medium",
                "hover:bg-white/90 transition-colors"
              )}
            >
              Start Free Trial
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/contact"
              className={cn(
                "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
                "border border-white/[0.18] text-white/90",
                "hover:bg-white/[0.08] transition-colors"
              )}
            >
              Contact Us
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
