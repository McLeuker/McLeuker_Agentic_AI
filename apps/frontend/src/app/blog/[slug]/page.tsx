'use client';

import { useParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { blogPosts } from "@/data/blog-posts";
import { ArrowLeft, ArrowRight, Clock, User } from "lucide-react";

export default function BlogPostPage() {
  const params = useParams();
  const slug = params?.slug as string;
  const post = blogPosts.find(p => p.slug === slug);
  
  if (!post) {
    return (
      <div className="min-h-screen bg-[#070707] flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl text-white/80 mb-4">Article not found</h1>
          <Link href="/blog" className="text-[#5c6652] hover:underline">
            Back to Journal
          </Link>
        </div>
      </div>
    );
  }

  // Find related posts (same category, excluding current)
  const related = blogPosts
    .filter(p => p.slug !== post.slug)
    .slice(0, 2);

  // Simple markdown-to-HTML conversion for blog content
  const renderContent = (content: string) => {
    const lines = content.split("\n");
    const elements: JSX.Element[] = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      if (line.startsWith("## ")) {
        elements.push(
          <h2 key={i} className="text-2xl font-medium text-white/[0.92] mt-10 mb-4">
            {line.slice(3)}
          </h2>
        );
      } else if (line.startsWith("### ")) {
        elements.push(
          <h3 key={i} className="text-xl font-medium text-white/[0.88] mt-8 mb-3">
            {line.slice(4)}
          </h3>
        );
      } else if (line.startsWith("**") && line.endsWith("**")) {
        elements.push(
          <p key={i} className="text-lg font-medium text-white/[0.85] mt-6 mb-2">
            {line.slice(2, -2)}
          </p>
        );
      } else if (line.startsWith("**")) {
        // Bold paragraph start
        const boldMatch = line.match(/^\*\*(.+?)\*\*\s*(.*)/);
        if (boldMatch) {
          elements.push(
            <p key={i} className="text-white/[0.72] text-base leading-[1.8] mb-4">
              <strong className="text-white/[0.88]">{boldMatch[1]}</strong>{" "}
              {boldMatch[2]}
            </p>
          );
        } else {
          elements.push(
            <p key={i} className="text-white/[0.72] text-base leading-[1.8] mb-4">
              {line}
            </p>
          );
        }
      } else if (line.trim() === "") {
        // Skip empty lines
      } else {
        elements.push(
          <p key={i} className="text-white/[0.72] text-base leading-[1.8] mb-4">
            {line}
          </p>
        );
      }
      i++;
    }

    return elements;
  };

  return (
    <div className="min-h-screen bg-[#070707] overflow-x-hidden">
      <TopNavigation variant="marketing" />
      <div className="h-16 lg:h-[72px]" />

      {/* Hero Image */}
      <div className="relative h-[40vh] lg:h-[50vh] overflow-hidden">
        <Image
          src={post.image}
          alt={post.title}
          fill
          className="object-cover grayscale brightness-[0.5]"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#070707] via-[#070707]/60 to-transparent" />
        
        {/* Back button */}
        <div className="absolute top-8 left-0 right-0 z-10">
          <div className="container mx-auto px-6 lg:px-12">
            <Link
              href="/blog"
              className="inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/80 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Journal
            </Link>
          </div>
        </div>
      </div>

      {/* Article */}
      <article className="relative -mt-32 z-10">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="max-w-[720px] mx-auto">
            {/* Meta */}
            <div className="flex items-center gap-3 text-xs text-white/40 mb-5">
              <span className="px-2.5 py-1 rounded-full bg-[#141414] border border-white/[0.06] text-[#5c6652]">
                {post.category}
              </span>
              <Clock className="w-3.5 h-3.5" />
              <span>{post.readTime}</span>
              <span className="w-1 h-1 rounded-full bg-white/20" />
              <span>{new Date(post.date).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</span>
            </div>

            {/* Title */}
            <h1 className="font-editorial text-3xl md:text-4xl lg:text-5xl text-white/[0.95] mb-6 leading-[1.1]">
              {post.title}
            </h1>

            {/* Author */}
            <div className="flex items-center gap-3 mb-12 pb-8 border-b border-white/[0.06]">
              <div className="w-10 h-10 rounded-full bg-[#141414] border border-white/[0.06] flex items-center justify-center">
                <User className="w-4 h-4 text-white/40" />
              </div>
              <div>
                <p className="text-sm font-medium text-white/[0.85]">{post.author}</p>
                <p className="text-xs text-white/35">McLeuker AI</p>
              </div>
            </div>

            {/* Content */}
            <div className="prose-custom">
              {renderContent(post.content)}
            </div>

            {/* Divider */}
            <div className="my-16 h-px bg-white/[0.06]" />

            {/* Related Posts */}
            {related.length > 0 && (
              <div>
                <h3 className="text-sm text-white/40 uppercase tracking-[0.15em] mb-6">
                  Continue Reading
                </h3>
                <div className="grid sm:grid-cols-2 gap-5">
                  {related.map((r, i) => (
                    <Link
                      key={i}
                      href={`/blog/${r.slug}`}
                      className="group p-5 rounded-xl bg-[#0C0C0C] border border-white/[0.04] hover:border-[#2E3524]/20 transition-all"
                    >
                      <span className="text-xs text-[#5c6652] mb-2 block">{r.category}</span>
                      <h4 className="text-sm font-medium text-white/[0.88] group-hover:text-[#5c6652] transition-colors line-clamp-2 mb-2">
                        {r.title}
                      </h4>
                      <div className="flex items-center gap-1 text-xs text-white/30">
                        <span>{r.readTime}</span>
                        <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </article>

      {/* Spacer */}
      <div className="h-20" />

      <Footer />
    </div>
  );
}
