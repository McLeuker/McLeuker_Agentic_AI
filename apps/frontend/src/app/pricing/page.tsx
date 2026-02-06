'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";
import { ArrowRight, Check } from "lucide-react";

const plans = [
  {
    name: "Starter",
    price: "Free",
    description: "Explore fashion, beauty & lifestyle intelligence",
    features: [
      "5 research queries per month",
      "Basic trend reports",
      "Email support",
      "Standard response time"
    ],
    cta: "Get Started",
    href: "/signup",
    highlighted: false
  },
  {
    name: "Professional",
    price: "$99",
    period: "/month",
    description: "For professionals who need structured, source-backed research",
    features: [
      "100 research queries per month",
      "Advanced trend forecasting",
      "Supplier intelligence reports",
      "Market analysis",
      "Priority support",
      "Structured output formatting"
    ],
    cta: "Start Free Trial",
    href: "/signup",
    highlighted: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "Tailored intelligence workflows for large teams",
    features: [
      "Unlimited research queries",
      "Custom AI model training",
      "Dedicated account manager",
      "API access",
      "SSO & advanced security",
      "Custom integrations",
      "SLA guarantee"
    ],
    cta: "Contact Sales",
    href: "/contact",
    highlighted: false
  }
];

const faqs = [
  {
    question: "How does the free trial work?",
    answer: "Start with our Professional plan free for 14 days. No credit card required. Cancel anytime."
  },
  {
    question: "Can I change plans later?",
    answer: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately."
  },
  {
    question: "What payment methods do you accept?",
    answer: "We accept all major credit cards, PayPal, and wire transfers for Enterprise plans."
  },
  {
    question: "Is there a discount for annual billing?",
    answer: "Yes, annual plans receive a 20% discount compared to monthly billing."
  }
];

export default function PricingPage() {
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
              Pricing
            </p>
            <h1 className="font-editorial text-4xl md:text-5xl lg:text-6xl text-white/[0.92] mb-6 leading-[1.1]">
              Pricing
            </h1>
            <p className="text-white/65 text-lg lg:text-xl max-w-2xl mx-auto">
              Built for fashion, beauty &amp; lifestyle research workflows. Start free and upgrade anytime.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-16 lg:py-20 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {plans.map((plan, i) => (
              <div
                key={i}
                className={cn(
                  "p-8 rounded-[20px]",
                  "border",
                  plan.highlighted 
                    ? "bg-gradient-to-b from-[#1A1A1A] to-[#0F0F0F] border-white/[0.18]" 
                    : "bg-gradient-to-b from-[#141414] to-[#0A0A0A] border-white/[0.08]"
                )}
              >
                {plan.highlighted && (
                  <div className="text-xs text-white/70 uppercase tracking-wider mb-4 px-3 py-1 bg-white/[0.08] rounded-full inline-block">
                    Most Popular
                  </div>
                )}
                <h3 className="text-xl font-medium text-white/[0.92] mb-2">
                  {plan.name}
                </h3>
                <div className="flex items-baseline gap-1 mb-4">
                  <span className="text-4xl font-editorial text-white/[0.92]">
                    {plan.price}
                  </span>
                  {plan.period && (
                    <span className="text-white/50">{plan.period}</span>
                  )}
                </div>
                <p className="text-sm text-white/55 mb-6">
                  {plan.description}
                </p>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-3 text-sm text-white/70">
                      <Check className="w-4 h-4 text-white/50 mt-0.5 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.href}
                  className={cn(
                    "w-full flex items-center justify-center gap-2 px-6 py-3 rounded-full transition-colors",
                    plan.highlighted
                      ? "bg-white text-black hover:bg-white/90"
                      : "border border-white/[0.18] text-white/90 hover:bg-white/[0.08]"
                  )}
                >
                  {plan.cta}
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 lg:py-28 bg-[#0A0A0A]">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="text-center mb-12 lg:mb-16">
            <p className="text-xs sm:text-sm text-white/40 uppercase tracking-[0.2em] mb-3">
              FAQ
            </p>
            <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.92]">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="max-w-3xl mx-auto space-y-6">
            {faqs.map((faq, i) => (
              <div
                key={i}
                className={cn(
                  "p-6 rounded-[16px]",
                  "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
                  "border border-white/[0.08]"
                )}
              >
                <h3 className="text-lg font-medium text-white/[0.92] mb-2">
                  {faq.question}
                </h3>
                <p className="text-white/55">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-28 bg-[#070707]">
        <div className="container mx-auto px-6 lg:px-12 text-center">
          <h2 className="font-editorial text-3xl md:text-4xl text-white/[0.92] mb-6">
            Still have questions?
          </h2>
          <p className="text-white/65 text-lg mb-10 max-w-2xl mx-auto">
            Our team is here to help you find the right plan for your needs.
          </p>
          <Link
            href="/contact"
            className={cn(
              "inline-flex items-center gap-2 px-8 py-3.5 rounded-full",
              "border border-white/[0.18] text-white/90",
              "hover:bg-white/[0.08] transition-colors"
            )}
          >
            Contact Us
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
