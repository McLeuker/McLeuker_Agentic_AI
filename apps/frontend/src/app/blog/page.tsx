'use client';

import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { blogPosts } from "@/data/blog-posts";
import { ArrowRight, Clock } from "lucide-react";

export default function BlogPage() {
  const featured = blogPosts.find(p => p.featured) || blogPosts[0];
  const rest = blogPosts.filter(p => p.slug !== featured.slug);

  return (
    <div className="min-h-screen bg-[#070707] overflow-x-hidden">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* Header */}
      <section className="pt-20 lg:pt-28 pb-12 lg:pb-16 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <p className="text-xs text-white/40 uppercase tracking-[0.2em] mb-3">
              Insights & Analysis
            </p>
            <h1 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-4 leading-[1.05]">
              The McLeuker Journal
            </h1>
            <p className="text-white/50 text-lg max-w-2xl leading-relaxed">
              Industry analysis, technology perspectives, and trend intelligence from the McLeuker Research team.
            </p>
          </div>
        </div>
      </section>

      {/* Featured Post */}
      <section className="pb-16 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <Link href={`/blog/${featured.slug}`} className="group block">
              <div className="grid lg:grid-cols-2 gap-8 rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] group-hover:border-[#2E3524]/20 transition-all duration-300">
                {/* Image */}
                <div className="relative h-[280px] lg:h-full min-h-[360px] overflow-hidden">
                  <Image
                    src={featured.image}
                    alt={featured.title}
                    fill
                    className="object-cover grayscale brightness-[0.65] group-hover:brightness-[0.75] group-hover:scale-105 transition-all duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent to-[#0C0C0C]/50 hidden lg:block" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#0C0C0C] to-transparent lg:hidden" />
                  <div className="absolute top-5 left-5">
                    <span className="px-3 py-1.5 rounded-full bg-[#2E3524]/80 backdrop-blur-sm text-xs text-white/90 font-medium">
                      Featured
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-8 lg:p-10 flex flex-col justify-center">
                  <div className="flex items-center gap-3 text-xs text-white/35 mb-4">
                    <span className="px-2.5 py-1 rounded-full bg-[#141414] border border-white/[0.06] text-[#5c6652]">
                      {featured.category}
                    </span>
                    <Clock className="w-3.5 h-3.5" />
                    <span>{featured.readTime}</span>
                    <span className="w-1 h-1 rounded-full bg-white/20" />
                    <span>{new Date(featured.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</span>
                  </div>
                  <h2 className="text-2xl lg:text-3xl font-medium text-white/[0.92] mb-4 group-hover:text-[#5c6652] transition-colors leading-tight">
                    {featured.title}
                  </h2>
                  <p className="text-white/45 leading-relaxed mb-6 line-clamp-3">
                    {featured.excerpt}
                  </p>
                  <div className="flex items-center gap-2 text-sm text-[#5c6652]">
                    <span>Read Article</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* All Posts Grid */}
      <section className="py-16 lg:py-20 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[1200px] mx-auto">
            <h3 className="text-sm text-white/40 uppercase tracking-[0.15em] mb-8">
              All Articles
            </h3>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {rest.map((post, i) => (
                <Link
                  key={i}
                  href={`/blog/${post.slug}`}
                  className="group"
                >
                  <div className="rounded-2xl overflow-hidden bg-[#0C0C0C] border border-white/[0.04] group-hover:border-[#2E3524]/20 transition-all duration-300 h-full">
                    <div className="relative h-[200px] overflow-hidden">
                      <Image
                        src={post.image}
                        alt={post.title}
                        fill
                        className="object-cover grayscale brightness-[0.65] group-hover:brightness-[0.75] group-hover:scale-105 transition-all duration-700"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-[#0C0C0C] to-transparent" />
                      <div className="absolute top-4 left-4">
                        <span className="px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-sm text-xs text-white/70 border border-white/[0.06]">
                          {post.category}
                        </span>
                      </div>
                    </div>
                    
                    <div className="p-6">
                      <div className="flex items-center gap-3 text-xs text-white/35 mb-3">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{post.readTime}</span>
                        <span className="w-1 h-1 rounded-full bg-white/20" />
                        <span>{new Date(post.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</span>
                      </div>
                      <h3 className="text-base font-medium text-white/[0.92] mb-2 group-hover:text-[#5c6652] transition-colors line-clamp-2">
                        {post.title}
                      </h3>
                      <p className="text-sm text-white/40 leading-relaxed line-clamp-2">
                        {post.excerpt}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
