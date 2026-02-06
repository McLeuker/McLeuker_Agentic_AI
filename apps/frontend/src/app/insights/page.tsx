'use client';

import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { ExternalLink } from "lucide-react";

const BLOG_POSTS = [
  {
    title: "The Future of Sustainable Fashion: 2026 and Beyond",
    excerpt: "Exploring emerging trends in circular fashion, regenerative materials, and the evolving regulatory landscape shaping the industry.",
    date: "January 2026",
    url: "https://www.mcleuker.com/blog"
  },
  {
    title: "AI in Fashion Supply Chains: A Practical Guide",
    excerpt: "How leading brands are leveraging artificial intelligence to optimize sourcing, reduce waste, and improve traceability.",
    date: "December 2025",
    url: "https://www.mcleuker.com/blog"
  },
  {
    title: "Navigating EU Textile Regulations: What Brands Need to Know",
    excerpt: "A comprehensive overview of upcoming European regulations and their implications for fashion and apparel companies.",
    date: "November 2025",
    url: "https://www.mcleuker.com/blog"
  },
  {
    title: "The Rise of Pre-Loved Luxury: Market Analysis",
    excerpt: "Analyzing the secondhand luxury market's explosive growth and what it means for traditional retail models.",
    date: "October 2025",
    url: "https://www.mcleuker.com/blog"
  },
  {
    title: "Supplier Transparency: Building Trust Through Traceability",
    excerpt: "Best practices for implementing supply chain transparency initiatives that satisfy both regulators and consumers.",
    date: "September 2025",
    url: "https://www.mcleuker.com/blog"
  },
  {
    title: "Color Trends SS26: What the Runways Are Telling Us",
    excerpt: "Our analysis of color directions from the Spring/Summer 2026 fashion weeks and their commercial applications.",
    date: "August 2025",
    url: "https://www.mcleuker.com/blog"
  }
];

export default function InsightsPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          {/* Hero */}
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Insights
            </h1>
            <p className="text-white/70 text-lg leading-relaxed">
              Industry analysis, trend reports, and strategic perspectives from the McLeuker team.
            </p>
          </div>

          {/* Blog Grid */}
          <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-6">
            {BLOG_POSTS.map((post, i) => (
              <a
                key={i}
                href={post.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-2xl p-6 border border-white/[0.08] hover:border-white/[0.15] transition-colors"
              >
                <div className="flex items-start justify-between gap-4 mb-3">
                  <h3 className="text-lg font-medium text-white group-hover:text-white/90 transition-colors">
                    {post.title}
                  </h3>
                  <ExternalLink className="h-4 w-4 text-white/30 flex-shrink-0 mt-1 group-hover:text-white/50 transition-colors" />
                </div>
                <p className="text-white/60 text-sm leading-relaxed mb-4">
                  {post.excerpt}
                </p>
                <p className="text-white/40 text-xs">{post.date}</p>
              </a>
            ))}
          </div>

          {/* More on McLeuker */}
          <div className="max-w-3xl mx-auto text-center mt-16">
            <p className="text-white/50 text-sm">
              Visit{" "}
              <a 
                href="https://www.mcleuker.com/blog" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-white/70 hover:text-white underline underline-offset-2"
              >
                mcleuker.com/blog
              </a>
              {" "}for more articles and industry perspectives.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
