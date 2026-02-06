'use client';

import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { Mail, Download } from "lucide-react";

export default function PressPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          {/* Hero */}
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Press
            </h1>
            <p className="text-white/70 text-lg leading-relaxed">
              Media resources and contact information for press inquiries about McLeuker AI.
            </p>
          </div>

          {/* Boilerplate */}
          <div className="max-w-3xl mx-auto mb-16">
            <h3 className="text-xl font-medium text-white mb-6">About McLeuker AI</h3>
            <div className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-8 border border-white/[0.08]">
              <p className="text-white/70 leading-relaxed mb-4">
                McLeuker AI is an artificial intelligence platform delivering specialized intelligence 
                for the fashion, beauty, and sustainability sectors. The platform enables brands, 
                retailers, and industry professionals to accelerate research, identify trends, 
                evaluate suppliers, and navigate the complex landscape of sustainable business practices.
              </p>
              <p className="text-white/70 leading-relaxed mb-4">
                Built on advanced language models trained on industry-specific data, McLeuker AI 
                transforms complex research tasks that traditionally took days or weeks into minutes, 
                while maintaining the depth and nuance required for strategic decision-making.
              </p>
              <p className="text-white/70 leading-relaxed">
                McLeuker combines deep fashion and sustainability expertise with cutting-edge AI 
                technology, serving clients across strategy, sourcing, compliance, and creative 
                functions.
              </p>
            </div>
          </div>

          {/* Brand Assets */}
          <div className="max-w-3xl mx-auto mb-16">
            <h3 className="text-xl font-medium text-white mb-6">Brand Assets</h3>
            <div className="bg-[#0D0D0D] rounded-xl p-6 border border-white/[0.05]">
              <div className="flex items-center gap-4">
                <Download className="h-5 w-5 text-white/50" />
                <div>
                  <p className="text-white font-medium">Logo and brand guidelines</p>
                  <p className="text-white/50 text-sm">
                    Contact us for access to logo files, brand guidelines, and approved imagery.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Media Contact */}
          <div className="max-w-3xl mx-auto text-center">
            <div className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-8 border border-white/[0.08]">
              <Mail className="h-8 w-8 text-white/60 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-3">Media Contact</h3>
              <p className="text-white/60 text-sm mb-4">
                For press inquiries, interview requests, or additional information, please contact:
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
