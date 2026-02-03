'use client';

import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { Mail } from "lucide-react";

const AREAS_OF_INTEREST = [
  {
    title: "Engineering",
    description: "Full-stack development, AI/ML infrastructure, data pipelines, and platform scalability."
  },
  {
    title: "AI & Machine Learning",
    description: "Large language models, NLP, information retrieval, and domain-specific model training."
  },
  {
    title: "Fashion & Industry",
    description: "Deep expertise in fashion, beauty, sustainability, supply chains, or retail strategy."
  },
  {
    title: "Design",
    description: "Product design, UX/UI, brand identity, and user research."
  },
  {
    title: "Operations",
    description: "Business operations, partnerships, customer success, and growth."
  }
];

export default function CareersPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          {/* Hero */}
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Careers
            </h1>
            <p className="text-white/70 text-lg leading-relaxed">
              We&apos;re building the intelligence layer for sustainable fashion. Join us in transforming 
              how the industry makes decisions.
            </p>
          </div>

          {/* Intro */}
          <div className="max-w-3xl mx-auto mb-16">
            <div className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-8 border border-white/[0.08]">
              <p className="text-white/70 leading-relaxed mb-4">
                McLeuker operates at the intersection of AI, fashion, and sustainability. We&apos;re always 
                interested in hearing from talented people who share our mission to make the fashion 
                industry more transparent, efficient, and responsible.
              </p>
              <p className="text-white/70 leading-relaxed">
                We value intellectual curiosity, craftsmanship, and a genuine interest in the problems 
                we&apos;re solving. If that sounds like you, we&apos;d love to hear from you.
              </p>
            </div>
          </div>

          {/* Areas of Interest */}
          <div className="max-w-3xl mx-auto mb-16">
            <h3 className="text-xl font-medium text-white mb-6">Areas of interest</h3>
            <div className="space-y-4">
              {AREAS_OF_INTEREST.map((area, i) => (
                <div 
                  key={i}
                  className="bg-[#0D0D0D] rounded-xl p-5 border border-white/[0.05]"
                >
                  <h4 className="text-white font-medium mb-2">{area.title}</h4>
                  <p className="text-white/60 text-sm">{area.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Contact CTA */}
          <div className="max-w-3xl mx-auto text-center">
            <div className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-8 border border-white/[0.08]">
              <Mail className="h-8 w-8 text-white/60 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-3">Get in touch</h3>
              <p className="text-white/60 text-sm mb-4">
                Send us your background, what you&apos;re interested in, and why McLeuker appeals to you.
              </p>
              <a 
                href="mailto:info@mcleuker.com"
                className="text-white hover:text-white/80 underline underline-offset-2"
              >
                info@mcleuker.com
              </a>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
