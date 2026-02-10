'use client';

import { useState } from "react";
import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { ChevronDown, ChevronUp } from "lucide-react";

const FAQS = [
  {
    question: "What are domains and how do I choose one?",
    answer: "Domains are specialized areas of intelligence (Fashion, Beauty, Sustainability, etc.). Each domain focuses the AI on relevant data sources and terminology. Choose 'Global' for cross-industry queries, or select a specific domain for deeper, more focused analysis."
  },
  {
    question: "How does the credit system work?",
    answer: "Credits are consumed with each query based on complexity. Simple questions use fewer credits; deep research and report generation use more. Your plan includes a monthly credit allocation, and you can purchase additional credits as needed."
  },
  {
    question: "What output formats can I export?",
    answer: "McLeuker AI can generate outputs in multiple formats including formatted text (with markdown), PDF reports, Excel spreadsheets for data, and PowerPoint-ready summaries. Specify your preferred format in your query."
  },
  {
    question: "How can I get the best results from my queries?",
    answer: "Be specific about what you need: include timeframes, regions, price segments, and the depth of analysis required. For example, instead of 'tell me about trends,' try 'analyze SS26 womenswear color trends from Milan and Paris fashion weeks for the contemporary market segment.'"
  },
  {
    question: "How reliable is the data?",
    answer: "McLeuker AI draws from curated industry sources, verified databases, and real-time signals. We clearly indicate when information is estimated or when data availability is limited. For critical decisions, we recommend cross-referencing with primary sources."
  },
  {
    question: "Can I save and organize my research?",
    answer: "Yes. All your conversations are saved in Chat History. You can search past conversations and continue where you left off. Important insights can be exported for use in your own systems and reports."
  },
  {
    question: "What are the different modes and how do they work?",
    answer: "McLeuker offers three modes: Instant mode provides fast, concise answers using existing knowledge. Auto mode conducts comprehensive analysis, cross-references multiple sources, and generates structured reports. Agent mode handles complex multi-step tasks with deep reasoning. Credits are deducted dynamically based on actual usage during each task."
  },
  {
    question: "Is my data private and secure?",
    answer: "Yes. Your queries and outputs are private to your account. We don't share your research with other users or use it to train models without consent. See our Privacy Policy for complete details on data handling."
  },
  {
    question: "Can I use McLeuker AI for competitor analysis?",
    answer: "Absolutely. McLeuker AI can analyze competitor positioning, pricing strategies, sustainability claims, product assortments, and market presence. Just specify the brands and aspects you want to compare."
  },
  {
    question: "How do I upgrade my plan or add credits?",
    answer: "Visit the Billing section in your profile to upgrade your subscription or purchase additional credits. Changes take effect immediately, and unused credits roll over based on your plan terms."
  },
  {
    question: "What if the AI doesn't understand my query?",
    answer: "Try rephrasing with more context or breaking complex questions into smaller parts. If you consistently have trouble, our support team can help you formulate effective queries for your specific use case."
  },
  {
    question: "Can multiple team members share an account?",
    answer: "Enterprise plans support multiple seats with shared credit pools and conversation visibility options. Contact us for team pricing and collaboration features."
  },
  {
    question: "How do I contact support?",
    answer: "Email us at info@mcleuker.com or use the Contact page. We typically respond within 24 hours on business days."
  }
];

export default function HelpPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          {/* Hero */}
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Help & FAQ
            </h1>
            <p className="text-white/70 text-lg leading-relaxed">
              Answers to common questions about McLeuker AI, the dashboard, and getting the most from your research.
            </p>
          </div>

          {/* FAQ List */}
          <div className="max-w-3xl mx-auto space-y-3">
            {FAQS.map((faq, index) => (
              <div
                key={index}
                className="bg-gradient-to-b from-[#1A1A1A] to-[#141414] rounded-xl border border-white/[0.08] overflow-hidden"
              >
                <button
                  onClick={() => toggleFaq(index)}
                  className="w-full flex items-center justify-between p-5 text-left focus:outline-none focus:ring-2 focus:ring-white/20 focus:ring-inset"
                >
                  <span className="text-white font-medium pr-4">{faq.question}</span>
                  {openIndex === index ? (
                    <ChevronUp className="h-5 w-5 text-white/50 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-white/50 flex-shrink-0" />
                  )}
                </button>
                {openIndex === index && (
                  <div className="px-5 pb-5">
                    <p className="text-white/60 leading-relaxed">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Still need help */}
          <div className="max-w-3xl mx-auto text-center mt-16">
            <p className="text-white/50 text-sm mb-4">
              Still have questions?
            </p>
            <Link 
              href="/contact"
              className="text-white hover:text-white/80 underline underline-offset-2 text-sm"
            >
              Contact our support team
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
