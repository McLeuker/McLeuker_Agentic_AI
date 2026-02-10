'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Coins,
  ArrowRight,
  Loader2,
  Check,
  Zap,
  Search,
  Brain,
  Palette,
  FileText,
  Star,
  Tag,
  Info,
  Calendar,
  Repeat,
  CreditCard,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';
const ANNUAL_DISCOUNT = 0.18;

const creditTiers = [
  { slug: 'credits-50', credits: 50, price: 5 },
  { slug: 'credits-100', credits: 100, price: 10 },
  { slug: 'credits-150', credits: 150, price: 15 },
  { slug: 'credits-200', credits: 200, price: 20 },
  { slug: 'credits-300', credits: 300, price: 30 },
  { slug: 'credits-400', credits: 400, price: 40 },
  { slug: 'credits-500', credits: 500, price: 50, popular: true },
  { slug: 'credits-750', credits: 750, price: 75 },
  { slug: 'credits-1000', credits: 1000, price: 100, bestValue: true },
  { slug: 'credits-1500', credits: 1500, price: 150 },
  { slug: 'credits-2000', credits: 2000, price: 200 },
  { slug: 'credits-2500', credits: 2500, price: 250 },
  { slug: 'credits-3000', credits: 3000, price: 300 },
  { slug: 'credits-5000', credits: 5000, price: 500 },
  { slug: 'credits-7500', credits: 7500, price: 750 },
  { slug: 'credits-10000', credits: 10000, price: 1000 },
  { slug: 'credits-15000', credits: 15000, price: 1500 },
  { slug: 'credits-25000', credits: 25000, price: 2500 },
];

interface BuyCreditsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BuyCreditsModal({ open, onOpenChange }: BuyCreditsModalProps) {
  const { user, session } = useAuth();
  const [currentPlan, setCurrentPlan] = useState<string>('free');
  const [purchaseType, setPurchaseType] = useState<'one-time' | 'annual'>('one-time');
  const [creditBalance, setCreditBalance] = useState<number>(0);
  const [purchasingPack, setPurchasingPack] = useState<string | null>(null);
  const [selectedTier, setSelectedTier] = useState<string | null>(null);

  useEffect(() => {
    if (!user || !session || !open) return;
    fetch(`${API_URL}/api/v1/billing/credits`, {
      headers: { 'Authorization': `Bearer ${session.access_token}` },
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setCurrentPlan(data.data?.plan || 'free');
          setCreditBalance(data.data?.balance || 0);
        }
      })
      .catch(console.error);
  }, [user, session, open]);

  const handlePurchaseCredits = async (packSlug: string) => {
    if (!session?.access_token) {
      window.location.href = `/login?redirect=/billing`;
      return;
    }

    setPurchasingPack(packSlug);
    try {
      const isAnnualPurchase = purchaseType === 'annual';
      const res = await fetch(`${API_URL}/api/v1/billing/checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          package_slug: isAnnualPurchase ? `${packSlug}-annual` : packSlug,
          mode: isAnnualPurchase ? 'subscription' : 'payment',
          billing_interval: isAnnualPurchase ? 'year' : undefined,
        }),
      });
      const data = await res.json();
      if (data.success && data.url) {
        window.location.href = data.url;
      } else if (data.detail) {
        alert(data.detail);
      }
    } catch (error) {
      console.error('Error purchasing credits:', error);
    } finally {
      setPurchasingPack(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[680px] w-[95vw] max-h-[90vh] overflow-hidden bg-[#111111] border-white/[0.08] p-0">
        {/* Header */}
        <div className="p-6 pb-0">
          <DialogHeader>
            <DialogTitle className="text-2xl font-serif font-light text-white flex items-center gap-2">
              <Coins className="h-6 w-6 text-white/50" />
              Buy Credits
            </DialogTitle>
            <DialogDescription className="text-white/50">
              Purchase credits to use for deep search, agent mode, creative tasks, and file exports.
            </DialogDescription>
          </DialogHeader>

          {/* Current Balance */}
          <div className="mt-4 p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
            <div>
              <p className="text-xs text-white/40">Current Balance</p>
              <p className="text-xl font-light text-white">{creditBalance.toLocaleString()} <span className="text-sm text-white/40">credits</span></p>
            </div>
            <div className="text-right">
              <p className="text-xs text-white/40">Plan</p>
              <p className="text-sm text-white/60 capitalize">{currentPlan}</p>
            </div>
          </div>

          {/* Purchase Type Toggle: One-Time vs Annual */}
          <div className="mt-4 p-1 rounded-xl bg-white/[0.03] border border-white/[0.06] flex">
            <button
              onClick={() => setPurchaseType('one-time')}
              className={cn(
                'flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm transition-all',
                purchaseType === 'one-time'
                  ? 'bg-white/[0.08] text-white border border-white/[0.10]'
                  : 'text-white/40 hover:text-white/60'
              )}
            >
              <CreditCard className="h-3.5 w-3.5" />
              One-Time Purchase
            </button>
            <button
              onClick={() => setPurchaseType('annual')}
              className={cn(
                'flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm transition-all relative',
                purchaseType === 'annual'
                  ? 'bg-white/[0.08] text-white border border-white/[0.10]'
                  : 'text-white/40 hover:text-white/60'
              )}
            >
              <Repeat className="h-3.5 w-3.5" />
              Annual Credit Plan
              <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-green-500/15 text-green-400 border border-green-500/20 font-medium">
                -18%
              </span>
            </button>
          </div>

          {/* Purchase type description */}
          {purchaseType === 'one-time' ? (
            <div className="mt-3 p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06] flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-white/30 flex-shrink-0" />
              <p className="text-xs text-white/40">
                Buy credits once. Credits never expire and are added to your balance immediately.
              </p>
            </div>
          ) : (
            <div className="mt-3 p-2.5 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center gap-2">
              <Calendar className="h-4 w-4 text-green-400 flex-shrink-0" />
              <p className="text-xs text-green-400">
                Subscribe to receive credits <strong>every month</strong> at <strong>18% off</strong>. Billed annually. Cancel anytime.
              </p>
            </div>
          )}

          {/* Credit usage info */}
          <div className="mt-3 grid grid-cols-4 gap-2">
            <div className="p-2 rounded-lg bg-white/[0.02] border border-white/[0.04] text-center">
              <Search className="h-3.5 w-3.5 mx-auto text-white/30 mb-1" />
              <p className="text-[9px] text-white/40">Deep Search</p>
              <p className="text-[10px] text-white/60 font-medium">5-15 cr</p>
            </div>
            <div className="p-2 rounded-lg bg-white/[0.02] border border-white/[0.04] text-center">
              <Brain className="h-3.5 w-3.5 mx-auto text-white/30 mb-1" />
              <p className="text-[9px] text-white/40">Agent Mode</p>
              <p className="text-[10px] text-white/60 font-medium">20-50 cr</p>
            </div>
            <div className="p-2 rounded-lg bg-white/[0.02] border border-white/[0.04] text-center">
              <Palette className="h-3.5 w-3.5 mx-auto text-white/30 mb-1" />
              <p className="text-[9px] text-white/40">Creative</p>
              <p className="text-[10px] text-white/60 font-medium">10-30 cr</p>
            </div>
            <div className="p-2 rounded-lg bg-white/[0.02] border border-white/[0.04] text-center">
              <FileText className="h-3.5 w-3.5 mx-auto text-white/30 mb-1" />
              <p className="text-[9px] text-white/40">File Export</p>
              <p className="text-[10px] text-white/60 font-medium">5-10 cr</p>
            </div>
          </div>
        </div>

        {/* Scrollable Credit Tiers */}
        <div className="px-6 pb-6 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-medium text-white/50 uppercase tracking-wider">
              {purchaseType === 'annual' ? 'Select Monthly Credit Amount' : 'Select Credit Amount'}
            </h3>
            <p className="text-[10px] text-white/30">
              {purchaseType === 'annual' ? '$0.082 per credit/mo' : '$0.10 per credit'}
            </p>
          </div>

          <div className="max-h-[280px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {creditTiers.map((tier) => {
                const isAnnual = purchaseType === 'annual';
                const oneTimePrice = tier.price;
                const annualMonthlyPrice = Math.round(tier.price * (1 - ANNUAL_DISCOUNT));
                const annualTotalPrice = annualMonthlyPrice * 12;
                const displayPrice = isAnnual ? annualMonthlyPrice : oneTimePrice;
                const savings = isAnnual ? (oneTimePrice * 12) - annualTotalPrice : 0;
                const isSelected = selectedTier === tier.slug;

                return (
                  <button
                    key={tier.slug}
                    onClick={() => {
                      setSelectedTier(tier.slug);
                      handlePurchaseCredits(tier.slug);
                    }}
                    disabled={purchasingPack === tier.slug}
                    className={cn(
                      'relative p-3 rounded-xl border transition-all text-left group',
                      tier.popular
                        ? 'border-white/15 bg-white/[0.05] ring-1 ring-white/[0.08]'
                        : tier.bestValue
                          ? 'border-white/12 bg-white/[0.04]'
                          : 'border-white/[0.06] bg-white/[0.02]',
                      isSelected && 'border-white/30 bg-white/[0.08]',
                      'hover:border-white/20 hover:bg-white/[0.06]',
                      purchasingPack === tier.slug && 'opacity-50 cursor-wait'
                    )}
                  >
                    {tier.popular && (
                      <div className="absolute -top-2 left-1/2 -translate-x-1/2">
                        <span className="text-[8px] px-2 py-0.5 rounded-full bg-white/[0.10] text-white/70 border border-white/[0.10] uppercase tracking-wider whitespace-nowrap">
                          Popular
                        </span>
                      </div>
                    )}
                    {tier.bestValue && (
                      <div className="absolute -top-2 left-1/2 -translate-x-1/2">
                        <span className="text-[8px] px-2 py-0.5 rounded-full bg-white/[0.10] text-white/70 border border-white/[0.10] uppercase tracking-wider whitespace-nowrap flex items-center gap-0.5">
                          <Star className="h-2 w-2" /> Best Value
                        </span>
                      </div>
                    )}

                    <p className="text-lg font-editorial text-white/90 leading-tight">
                      {tier.credits.toLocaleString()}
                    </p>
                    <p className="text-[10px] text-white/30 mb-1.5">
                      {isAnnual ? 'credits / month' : 'credits'}
                    </p>

                    <div className="flex items-baseline gap-1.5">
                      <p className="text-base font-medium text-white/80">
                        ${displayPrice.toLocaleString()}
                        {isAnnual && <span className="text-[10px] text-white/40">/mo</span>}
                      </p>
                      {isAnnual && (
                        <p className="text-[10px] text-white/30 line-through">${oneTimePrice}</p>
                      )}
                    </div>

                    {isAnnual && (
                      <div className="mt-0.5">
                        <p className="text-[9px] text-white/30">
                          ${annualTotalPrice.toLocaleString()}/yr
                        </p>
                        <p className="text-[9px] text-green-400/70">
                          Save ${savings.toLocaleString()}/yr
                        </p>
                      </div>
                    )}

                    {!isAnnual && (
                      <div className="mt-2 pt-2 border-t border-white/[0.04]">
                        <span className="text-[10px] text-white/30 group-hover:text-white/50 transition-colors flex items-center gap-1">
                          {purchasingPack === tier.slug ? (
                            <><Loader2 className="h-2.5 w-2.5 animate-spin" /> Processing...</>
                          ) : (
                            <>Buy now <ArrowRight className="w-2.5 h-2.5" /></>
                          )}
                        </span>
                      </div>
                    )}

                    {isAnnual && (
                      <div className="mt-2 pt-2 border-t border-white/[0.04]">
                        <span className="text-[10px] text-white/30 group-hover:text-white/50 transition-colors flex items-center gap-1">
                          {purchasingPack === tier.slug ? (
                            <><Loader2 className="h-2.5 w-2.5 animate-spin" /> Processing...</>
                          ) : (
                            <>Subscribe <ArrowRight className="w-2.5 h-2.5" /></>
                          )}
                        </span>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Annual comparison summary */}
          {purchaseType === 'annual' && (
            <div className="mt-3 p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-3.5 w-3.5 text-white/40" />
                <p className="text-xs font-medium text-white/60">Annual Credit Plan Benefits</p>
              </div>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <p className="text-[10px] text-white/30">Discount</p>
                  <p className="text-sm font-medium text-green-400">18% off</p>
                </div>
                <div>
                  <p className="text-[10px] text-white/30">Delivery</p>
                  <p className="text-sm font-medium text-white/70">Monthly</p>
                </div>
                <div>
                  <p className="text-[10px] text-white/30">Billing</p>
                  <p className="text-sm font-medium text-white/70">Annually</p>
                </div>
              </div>
              <p className="text-[10px] text-white/30 mt-2 text-center">
                Credits are delivered monthly. Billed once per year. Cancel anytime with remaining months refunded.
              </p>
            </div>
          )}

          {/* Footer info */}
          <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between">
            <p className="text-[10px] text-white/30">
              {purchaseType === 'annual'
                ? 'Annual subscription. Credits delivered monthly. Cancel anytime.'
                : 'Credits never expire. Secure payment via Stripe.'}
            </p>
            <div className="flex items-center gap-1 text-[10px] text-white/30">
              <Check className="h-3 w-3" />
              All task types included
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
