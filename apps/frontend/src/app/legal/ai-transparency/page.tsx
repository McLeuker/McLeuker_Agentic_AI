'use client';

import Link from "next/link";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function AITransparencyPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              AI Transparency &amp; Safety
            </h1>
            <p className="text-white/50 mb-12">
              Last updated: February 6, 2026
            </p>

            <div className="space-y-10">
              <section>
                <p className="text-white/60 leading-relaxed">
                  McLeuker AI is committed to the responsible and transparent use of artificial intelligence. This page describes how our AI systems work, what data they process, and the safeguards we have in place, in alignment with the EU AI Act and GDPR requirements.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">AI System Classification</h2>
                <p className="text-white/60 leading-relaxed">
                  Under the EU AI Act, our system is classified as a <strong className="text-white/80">general-purpose AI system</strong> used for information retrieval, analysis, and content generation in the fashion intelligence domain. We do not operate in any high-risk category as defined by Annex III of the EU AI Act. Our AI does not make autonomous decisions that significantly affect individuals&apos; legal rights or vital interests.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">How Our AI Works</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  McLeuker AI uses third-party large language models (currently Grok by xAI) combined with retrieval-augmented generation (RAG) and web search (Perplexity AI) to provide intelligent responses. The system operates through a multi-layer reasoning process:
                </p>
                <div className="space-y-3">
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium mb-1">1. Intent Understanding</p>
                    <p className="text-white/60 text-sm">The system analyzes your query to understand the intent, domain, and required depth of analysis.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium mb-1">2. Information Retrieval</p>
                    <p className="text-white/60 text-sm">Relevant information is gathered from web sources, with citations provided for transparency.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium mb-1">3. Reasoning &amp; Analysis</p>
                    <p className="text-white/60 text-sm">The AI synthesizes information and applies domain-specific reasoning to generate insights.</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <p className="text-white/80 font-medium mb-1">4. Response Generation</p>
                    <p className="text-white/60 text-sm">A structured response is generated with sources, reasoning transparency, and follow-up suggestions.</p>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Data Processing by AI</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  When you interact with our AI, the following data may be processed:
                </p>
                <ul className="space-y-2 text-white/60">
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span>Your query text and conversation history (for context)</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span>Your selected domain and preferences</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span>Files you upload for analysis</span>
                  </li>
                </ul>
                <div className="mt-4 p-4 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                  <p className="text-white/80 font-medium mb-2">Important</p>
                  <p className="text-white/60">Your data is <strong className="text-white/80">never used to train or fine-tune</strong> any AI models. Data is processed in real-time for inference only and is not retained by our AI providers beyond the duration of the API call.</p>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Limitations &amp; Risks</h2>
                <p className="text-white/60 leading-relaxed mb-4">
                  AI systems have inherent limitations that users should be aware of:
                </p>
                <ul className="space-y-2 text-white/60">
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Hallucinations:</strong> The AI may generate information that sounds plausible but is factually incorrect.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Bias:</strong> AI models may reflect biases present in their training data.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Timeliness:</strong> Information may not always reflect the most recent developments.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-white/40 shrink-0">&bull;</span>
                    <span><strong className="text-white/80">Not Professional Advice:</strong> AI output should not be treated as legal, medical, or financial advice.</span>
                  </li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Human Oversight</h2>
                <p className="text-white/60 leading-relaxed">
                  McLeuker AI is designed as a human-in-the-loop system. All AI-generated outputs are presented to the user for review before any action is taken. High-impact agent actions require explicit user approval. Users always have the ability to override, edit, or reject AI suggestions.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Your Rights</h2>
                <p className="text-white/60 leading-relaxed">
                  Under GDPR Article 22, you have the right not to be subject to a decision based solely on automated processing that significantly affects you. Our AI assists decision-making but does not make autonomous decisions with legal or similarly significant effects. You can exercise your data rights through our{' '}
                  <Link href="/legal/dsar" className="text-white/80 underline hover:text-white">Data Subject Access Request</Link> page.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Contact</h2>
                <p className="text-white/60 leading-relaxed">
                  For questions about our AI practices, please contact{' '}
                  <a href="mailto:dpo@mcleuker.com" className="text-white/80 underline hover:text-white">dpo@mcleuker.com</a>.
                </p>
              </section>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
