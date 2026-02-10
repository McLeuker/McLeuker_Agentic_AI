'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { cn } from '@/lib/utils';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Check,
  X as XIcon,
  Crown,
  Sparkles,
  Zap,
  Building2,
  ArrowRight,
  Loader2,
  Shield,
  Globe,
  FileText,
  Brain,
  Palette,
  Search,
  Users,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';
const ANNUAL_DISCOUNT = 0.18;

interface Plan {
  id: string;
  name: string;
  desc: string;
  monthlyPrice: number | null;
  yearlyPrice: number | null;
  icon: typeof Zap;
  dailyCredits: number;
  maxDomains: number;
  features: string[];
  limitations: string[];
  badge?: string;
}

const plans: Plan[] = [
  {
    id: 'free',
    name: 'Free',
    desc: 'Explore the platform',
    monthlyPrice: 0,
    yearlyPrice: 0,
    icon: Zap,
    dailyCredits: 15,
    maxDomains: 2,
    features: [
      '15 daily fresh credits',
      '2 domains (Global + 1)',
      'Instant search only',
      'Community support',
    ],
    limitations: [
      'No deep search',
      'No agent mode',
      'No file exports',
    ],
  },
  {
    id: 'standard',
    name: 'Standard',
    desc: 'For individual researchers',
    monthlyPrice: 19,
    yearlyPrice: Math.round(19 * 12 * (1 - ANNUAL_DISCOUNT)),
    icon: Sparkles,
    dailyCredits: 50,
    maxDomains: 5,
    features: [
      '50 daily fresh credits',
      '5 domains access',
      'Deep search & analysis',
      'Export to PDF, Excel, PPTX',
      '3 concurrent tasks',
      'Priority support',
    ],
    limitations: [],
    badge: 'Most Popular',
  },
  {
    id: 'pro',
    name: 'Pro',
    desc: 'For fashion professionals',
    monthlyPrice: 99,
    yearlyPrice: Math.round(99 * 12 * (1 - ANNUAL_DISCOUNT)),
    icon: Crown,
    dailyCredits: 300,
    maxDomains: 10,
    features: [
      '300 daily fresh credits',
      'All 10 domains',
      'Agent mode & auto analysis',
      'Advanced trend forecasting',
      'Supplier intelligence',
      'Unlimited concurrent tasks',
    ],
    limitations: [],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    desc: 'For teams & organizations',
    monthlyPrice: null,
    yearlyPrice: null,
    icon: Building2,
    dailyCredits: 500,
    maxDomains: 10,
    features: [
      'Custom credit allocation',
      'All 10 domains + custom',
      'Dedicated account manager',
      'Custom AI model training',
      'API access & integrations',
      'SSO & advanced security',
    ],
    limitations: [],
  },
];

const PLAN_RANK: Record<string, number> = { free: 0, standard: 1, pro: 2, enterprise: 3 };

interface UpgradePlanModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function UpgradePlanModal({ open, onOpenChange }: UpgradePlanModalProps) {
  const { user, session } = useAuth();
  const [annual, setAnnual] = useState(true);
  const [currentPlan, setCurrentPlan] = useState<string>('free');
  const [subscribing, setSubscribing] = useState<string | null>(null);

  useEffect(() => {
    if (!user || !open) return;
    supabase
      .from('users')
      .select('subscription_plan')
      .eq('id', user.id)
      .single()
      .then(({ data }) => {
        setCurrentPlan(data?.subscription_plan || 'free');
      });
  }, [user, open]);

  const handleSubscribe = async (planSlug: string) => {
    if (planSlug === currentPlan) return;
    if (planSlug === 'enterprise') {
      window.location.href = '/contact';
      return;
    }
    if (!session?.access_token) {
      window.location.href = `/login?redirect=/pricing&plan=${planSlug}`;
      return;
    }

    setSubscribing(planSlug);
    try {
      const res = await fetch(`${API_URL}/api/v1/billing/checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan_slug: planSlug,
          billing_interval: annual ? 'year' : 'month',
          mode: 'subscription',
        }),
      });
      const data = await res.json();
      if (data.success && data.url) {
        window.location.href = data.url;
      } else if (data.detail) {
        alert(data.detail);
      }
    } catch (error) {
      console.error('Checkout error:', error);
    } finally {
      setSubscribing(null);
    }
  };

  const getButtonText = (planSlug: string) => {
    if (planSlug === 'enterprise') return 'Contact Sales';
    if (currentPlan === planSlug) return 'Current Plan';
    if (PLAN_RANK[planSlug] > PLAN_RANK[currentPlan]) return 'Upgrade';
    if (PLAN_RANK[planSlug] < PLAN_RANK[currentPlan]) return 'Downgrade';
    return 'Subscribe';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[900px] w-[95vw] max-h-[90vh] overflow-y-auto bg-[#111111] border-white/[0.08] p-0">
        <div className="p-6 pb-0">
          <DialogHeader>
            <DialogTitle className="text-2xl font-serif font-light text-white">
              Choose your plan
            </DialogTitle>
            <DialogDescription className="text-white/50">
              Upgrade to unlock more domains, auto analysis, file exports, and agent mode.
            </DialogDescription>
          </DialogHeader>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-3 mt-6">
            <button
              onClick={() => setAnnual(false)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm transition-all',
                !annual ? 'bg-white/[0.10] text-white' : 'text-white/40 hover:text-white/60'
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => setAnnual(true)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2',
                annual ? 'bg-white/[0.10] text-white' : 'text-white/40 hover:text-white/60'
              )}
            >
              Annual
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-green-500/20 text-green-400 border border-green-500/20">
                Save 18%
              </span>
            </button>
          </div>
        </div>

        {/* Plan Cards */}
        <div className="p-6 pt-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {plans.map((plan) => {
              const isCurrent = currentPlan === plan.id;
              const isUpgrade = PLAN_RANK[plan.id] > PLAN_RANK[currentPlan];
              const Icon = plan.icon;
              const price = annual ? plan.yearlyPrice : plan.monthlyPrice;
              const monthlyEquiv = annual && plan.yearlyPrice ? Math.round(plan.yearlyPrice / 12) : plan.monthlyPrice;

              return (
                <div
                  key={plan.id}
                  className={cn(
                    'relative rounded-xl border p-4 transition-all',
                    isCurrent
                      ? 'border-white/20 bg-white/[0.05]'
                      : isUpgrade
                        ? 'border-white/[0.10] bg-white/[0.03] hover:border-white/20'
                        : 'border-white/[0.06] bg-white/[0.02]'
                  )}
                >
                  {plan.badge && (
                    <div className="absolute -top-2.5 left-1/2 -translate-x-1/2">
                      <span className="text-[9px] px-2.5 py-0.5 rounded-full bg-white/[0.10] text-white/70 border border-white/[0.10] uppercase tracking-wider whitespace-nowrap">
                        {plan.badge}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-white/[0.05] flex items-center justify-center">
                      <Icon className="h-4 w-4 text-white/50" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-white">{plan.name}</h3>
                      <p className="text-[10px] text-white/40">{plan.desc}</p>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="mb-3">
                    {price !== null ? (
                      <>
                        <span className="text-2xl font-light text-white">
                          ${monthlyEquiv}
                        </span>
                        <span className="text-sm text-white/40">/mo</span>
                        {annual && plan.monthlyPrice !== null && plan.monthlyPrice > 0 && (
                          <p className="text-[10px] text-white/30 mt-0.5">
                            Billed ${price}/year
                          </p>
                        )}
                      </>
                    ) : (
                      <span className="text-2xl font-light text-white">Custom</span>
                    )}
                  </div>

                  {/* Key stats */}
                  <div className="flex items-center gap-3 mb-3 text-[10px] text-white/40">
                    <span>{plan.dailyCredits} credits/day</span>
                    <span>{plan.maxDomains === 10 ? 'All domains' : `${plan.maxDomains} domains`}</span>
                  </div>

                  {/* Features */}
                  <div className="space-y-1.5 mb-4">
                    {plan.features.map((feature, i) => (
                      <div key={i} className="flex items-start gap-1.5">
                        <Check className="h-3 w-3 text-white/30 mt-0.5 flex-shrink-0" />
                        <span className="text-[11px] text-white/50">{feature}</span>
                      </div>
                    ))}
                    {plan.limitations.map((limitation, i) => (
                      <div key={i} className="flex items-start gap-1.5">
                        <XIcon className="h-3 w-3 text-white/20 mt-0.5 flex-shrink-0" />
                        <span className="text-[11px] text-white/30 line-through">{limitation}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleSubscribe(plan.id)}
                    disabled={isCurrent || subscribing === plan.id}
                    className={cn(
                      'w-full py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-1.5',
                      isCurrent
                        ? 'bg-white/[0.05] text-white/30 cursor-default'
                        : isUpgrade
                          ? 'bg-white text-black hover:bg-white/90'
                          : 'bg-white/[0.08] text-white/60 hover:bg-white/[0.12]'
                    )}
                  >
                    {subscribing === plan.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        {getButtonText(plan.id)}
                        {isUpgrade && <ArrowRight className="h-3.5 w-3.5" />}
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Comparison highlights */}
          <div className="mt-6 p-4 rounded-xl bg-white/[0.02] border border-white/[0.04]">
            <h4 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-3">Quick Comparison</h4>
            <div className="grid grid-cols-5 gap-2 text-[11px]">
              <div className="text-white/40 font-medium">Feature</div>
              <div className="text-center text-white/40">Free</div>
              <div className="text-center text-white/40">Standard</div>
              <div className="text-center text-white/40">Pro</div>
              <div className="text-center text-white/40">Enterprise</div>

              <div className="text-white/50 flex items-center gap-1"><Search className="h-3 w-3" /> Deep Search</div>
              <div className="text-center text-white/20"><XIcon className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>

              <div className="text-white/50 flex items-center gap-1"><Brain className="h-3 w-3" /> Agent Mode</div>
              <div className="text-center text-white/20"><XIcon className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/20"><XIcon className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>

              <div className="text-white/50 flex items-center gap-1"><FileText className="h-3 w-3" /> File Exports</div>
              <div className="text-center text-white/20"><XIcon className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>

              <div className="text-white/50 flex items-center gap-1"><Globe className="h-3 w-3" /> Domains</div>
              <div className="text-center text-white/40">2</div>
              <div className="text-center text-white/40">5</div>
              <div className="text-center text-white/40">All 10</div>
              <div className="text-center text-white/40">All 10+</div>

              <div className="text-white/50 flex items-center gap-1"><Palette className="h-3 w-3" /> Creative Mode</div>
              <div className="text-center text-white/20"><XIcon className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/20"><XIcon className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>
              <div className="text-center text-white/50"><Check className="h-3 w-3 mx-auto" /></div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
