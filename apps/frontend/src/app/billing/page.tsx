'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { UpgradePlanModal } from '@/components/billing/UpgradePlanModal';
import { BuyCreditsModal } from '@/components/billing/BuyCreditsModal';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  CreditCard,
  Coins,
  TrendingUp,
  ArrowRight,
  Zap,
  Receipt,
  ChevronLeft,
  LogOut,
  CheckCircle,
  Clock,
  Gift,
  ShoppingCart,
  ExternalLink,
  Flame,
  Crown,
  Search,
  Brain,
  Palette,
  Plus,
  Settings,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

const PLAN_DETAILS: Record<string, { name: string; dailyCredits: number; monthlyCredits: number; maxDomains: number; price: string }> = {
  free: { name: 'Free', dailyCredits: 15, monthlyCredits: 450, maxDomains: 2, price: '$0' },
  standard: { name: 'Standard', dailyCredits: 50, monthlyCredits: 1500, maxDomains: 5, price: '$19/mo' },
  pro: { name: 'Pro', dailyCredits: 300, monthlyCredits: 9000, maxDomains: 10, price: '$99/mo' },
  enterprise: { name: 'Enterprise', dailyCredits: 500, monthlyCredits: 25000, maxDomains: 10, price: 'Custom' },
};

interface CreditSummary {
  balance: number;
  plan: string;
  plan_name?: string;
  monthly_credits?: number;
  daily_credits_available?: boolean;
  daily_credits_balance?: number;
  daily_fresh_credits?: number;
  extra_credits?: number;
  streak?: number;
  total_consumed?: number;
  max_domains?: number;
  billing_interval?: string;
}

interface UsageItem {
  date: string;
  api_service: string;
  api_operation: string;
  credits_consumed: number;
  task_type?: string;
}

function BillingContent() {
  const router = useRouter();
  const { user, session, signOut } = useAuth();

  const [creditSummary, setCreditSummary] = useState<CreditSummary | null>(null);
  const [usageHistory, setUsageHistory] = useState<UsageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [claimingDaily, setClaimingDaily] = useState(false);
  const [dailyClaimed, setDailyClaimed] = useState(false);

  // Modal states
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [showCreditsModal, setShowCreditsModal] = useState(false);

  const getAuthHeaders = useCallback(() => {
    const token = session?.access_token;
    return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
  }, [session]);

  useEffect(() => {
    if (user && session) {
      fetchData();
    }
  }, [user, session]);

  const fetchData = async () => {
    try {
      const [creditsRes, usageRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/billing/credits`, { headers: getAuthHeaders() }),
        fetch(`${API_URL}/api/v1/billing/usage?days=30`, { headers: getAuthHeaders() }),
      ]);

      const creditsData = await creditsRes.json();
      const usageData = await usageRes.json();

      if (creditsData.success) setCreditSummary(creditsData.data);
      if (usageData.success) setUsageHistory(usageData.history || []);
    } catch (error) {
      console.error('Error fetching billing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimDaily = async () => {
    setClaimingDaily(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/billing/credits/claim-daily`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      const data = await res.json();
      if (data.success) {
        setDailyClaimed(true);
        setCreditSummary(prev => prev ? { ...prev, balance: data.new_balance, streak: data.streak } : prev);
      }
    } catch (error) {
      console.error('Error claiming daily credits:', error);
    } finally {
      setClaimingDaily(false);
    }
  };

  const handleManageSubscription = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/subscriptions/portal`, { headers: getAuthHeaders() });
      const data = await res.json();
      if (data.success && data.url) {
        window.open(data.url, '_blank');
      }
    } catch (error) {
      console.error('Error opening portal:', error);
    }
  };

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
      });
    } catch { return '—'; }
  };

  const plan = creditSummary?.plan || 'free';
  const planInfo = PLAN_DETAILS[plan] || PLAN_DETAILS.free;
  const balance = creditSummary?.balance || 0;
  const dailyBalance = creditSummary?.daily_credits_balance || 0;
  const extraCredits = creditSummary?.extra_credits || 0;
  const totalConsumed = creditSummary?.total_consumed || 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A]">
        <header className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A] border-b border-white/[0.08]">
          <div className="h-16 lg:h-[72px] flex items-center justify-between px-6 lg:px-8">
            <Link href="/dashboard" className="flex items-center gap-2 text-white/60 hover:text-white"><ChevronLeft className="h-5 w-5" /></Link>
            <span className="font-editorial text-xl text-white tracking-[0.02em]">McLeuker<span className="text-white/30">.ai</span></span>
            <div className="w-10" />
          </div>
        </header>
        <main className="pt-24 pb-12 px-4 lg:px-8 max-w-5xl mx-auto">
          <div className="space-y-6 animate-pulse">
            <div className="h-12 bg-[#1A1A1A] rounded w-1/3" />
            <div className="h-48 bg-[#1A1A1A] rounded-lg" />
            <div className="h-48 bg-[#1A1A1A] rounded-lg" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {/* Modals */}
      <UpgradePlanModal open={showUpgradeModal} onOpenChange={setShowUpgradeModal} />
      <BuyCreditsModal open={showCreditsModal} onOpenChange={setShowCreditsModal} />

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A] border-b border-white/[0.08]">
        <div className="h-16 lg:h-[72px] flex items-center justify-between px-6 lg:px-8">
          <Link href="/dashboard" className="flex items-center gap-2 text-white/60 hover:text-white transition-colors">
            <ChevronLeft className="h-5 w-5" />
            <span className="hidden sm:inline">Back to Dashboard</span>
          </Link>
          <Link href="/" className="flex items-center justify-center">
            <span className="font-editorial text-xl lg:text-[22px] text-white tracking-[0.02em]">McLeuker<span className="text-white/30">.ai</span></span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/settings" className="text-white/60 hover:text-white transition-colors">
              <Settings className="h-5 w-5" />
            </Link>
            <button onClick={handleSignOut} className="flex items-center gap-2 text-white/60 hover:text-white transition-colors">
              <LogOut className="h-5 w-5" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 lg:pt-28 pb-12 px-4 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="mb-8 lg:mb-12 flex items-start justify-between">
            <div>
              <h1 className="text-3xl lg:text-4xl font-serif font-light tracking-tight text-white">Billing & Credits</h1>
              <p className="text-white/60 mt-2">Manage your subscription, credits, and billing history</p>
            </div>
            {/* Quick action buttons */}
            <div className="flex items-center gap-2">
              <Button
                onClick={() => setShowCreditsModal(true)}
                className="bg-white text-black hover:bg-white/90 text-sm"
              >
                <Plus className="h-4 w-4 mr-1.5" />
                Buy Credits
              </Button>
              {(plan === 'free' || plan === 'standard') && (
                <Button
                  onClick={() => setShowUpgradeModal(true)}
                  variant="outline"
                  className="border-white/[0.12] text-white hover:bg-white/[0.08] text-sm"
                >
                  <TrendingUp className="h-4 w-4 mr-1.5" />
                  Upgrade
                </Button>
              )}
            </div>
          </div>

          <div className="space-y-8">
            {/* Current Plan Card */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                      <CreditCard className="h-5 w-5" />
                      Current Plan
                    </CardTitle>
                    <CardDescription className="mt-1">Your active subscription tier</CardDescription>
                  </div>
                  <Badge className={cn(
                    plan === 'free' ? 'bg-white/10 text-white/60' :
                    plan === 'standard' ? 'bg-blue-600/20 text-blue-400 border-blue-500/30' :
                    plan === 'pro' ? 'bg-purple-600/20 text-purple-400 border-purple-500/30' :
                    'bg-green-600/20 text-green-400 border-green-500/30'
                  )}>
                    {planInfo.name}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-6 sm:grid-cols-4">
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Plan</p>
                    <p className="text-2xl font-light text-white">{planInfo.name}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Daily Credits</p>
                    <p className="text-2xl font-light text-white">{planInfo.dailyCredits}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Domains</p>
                    <p className="text-2xl font-light text-white">{planInfo.maxDomains === 10 ? 'All 10' : planInfo.maxDomains}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Price</p>
                    <p className="text-2xl font-light text-white">{planInfo.price}</p>
                  </div>
                </div>

                <Separator className="bg-white/[0.08]" />

                {/* Upgrade prompt for free/standard users */}
                {(plan === 'free' || plan === 'standard') && (
                  <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-white/[0.05] flex items-center justify-center">
                          <Crown className="h-5 w-5 text-white/50" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">
                            {plan === 'free' ? 'Upgrade to Standard or Pro' : 'Upgrade to Pro'}
                          </p>
                          <p className="text-xs text-white/40">
                            {plan === 'free'
                              ? 'Unlock deep search, file exports, and more domains'
                              : 'Unlock agent mode and all 10 domains'}
                          </p>
                        </div>
                      </div>
                      <Button
                        onClick={() => setShowUpgradeModal(true)}
                        className="bg-white text-black hover:bg-white/90 text-sm"
                      >
                        <TrendingUp className="h-4 w-4 mr-2" />
                        Upgrade
                      </Button>
                    </div>
                  </div>
                )}

                <div className="flex flex-wrap gap-3">
                  <Button
                    variant="outline"
                    className="border-white/[0.08] text-white hover:bg-white/[0.08]"
                    onClick={() => setShowUpgradeModal(true)}
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    {plan === 'free' ? 'View Plans' : 'Change Plan'}
                  </Button>
                  {plan !== 'free' && (
                    <Button variant="outline" className="border-white/[0.08] text-white hover:bg-white/[0.08]" onClick={handleManageSubscription}>
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Manage Subscription
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Credit Overview */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                    <Coins className="h-5 w-5" />
                    Credit Balance
                  </CardTitle>
                  <Button
                    onClick={() => setShowCreditsModal(true)}
                    className="bg-white text-black hover:bg-white/90 text-sm"
                    size="sm"
                  >
                    <Plus className="h-3.5 w-3.5 mr-1" />
                    Buy Credits
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-6 sm:grid-cols-3">
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Total Balance</p>
                    <p className="text-4xl font-light text-white">{balance.toLocaleString()}</p>
                    <p className="text-xs text-white/40">credits available</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-white/60 flex items-center gap-1">
                      <Gift className="h-3 w-3" /> Daily Fresh
                    </p>
                    <p className="text-2xl font-light text-white">{dailyBalance}</p>
                    <p className="text-xs text-white/30">of {planInfo.dailyCredits} &middot; Instant search only</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-white/60 flex items-center gap-1">
                      <ShoppingCart className="h-3 w-3" /> Purchased
                    </p>
                    <p className="text-2xl font-light text-white">{extraCredits.toLocaleString()}</p>
                    <p className="text-xs text-white/30">All task types &middot; Never expires</p>
                  </div>
                </div>

                {balance < 20 && (
                  <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-between">
                    <p className="text-sm text-orange-400 flex items-center gap-1">
                      <Zap className="h-4 w-4" />
                      Low credits — claim daily credits or purchase more
                    </p>
                    <Button
                      onClick={() => setShowCreditsModal(true)}
                      size="sm"
                      className="bg-orange-500/20 text-orange-400 hover:bg-orange-500/30 border border-orange-500/20 text-xs"
                    >
                      Buy Now
                    </Button>
                  </div>
                )}

                <Separator className="bg-white/[0.08]" />

                {/* Daily Credits Claim */}
                <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-white/[0.05] flex items-center justify-center">
                        <Gift className="h-5 w-5 text-white/50" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">Daily Fresh Credits</p>
                        <p className="text-xs text-white/40">
                          Claim {planInfo.dailyCredits} credits every day &middot; Usable for instant search
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {creditSummary?.streak && creditSummary.streak > 1 && (
                        <div className="flex items-center gap-1 text-orange-400">
                          <Flame className="h-4 w-4" />
                          <span className="text-sm font-medium">{creditSummary.streak}-day streak</span>
                        </div>
                      )}
                      <Button
                        onClick={handleClaimDaily}
                        disabled={claimingDaily || dailyClaimed || !creditSummary?.daily_credits_available}
                        className={cn(
                          "text-sm",
                          dailyClaimed || !creditSummary?.daily_credits_available
                            ? "bg-white/[0.05] text-white/30"
                            : "bg-white text-black hover:bg-white/90"
                        )}
                      >
                        {dailyClaimed ? (
                          <><CheckCircle className="h-4 w-4 mr-1" /> Claimed</>
                        ) : !creditSummary?.daily_credits_available ? (
                          <><Clock className="h-4 w-4 mr-1" /> Already Claimed</>
                        ) : claimingDaily ? (
                          'Claiming...'
                        ) : (
                          <><Gift className="h-4 w-4 mr-1" /> Claim Now</>
                        )}
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Credit type explanation */}
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="p-3 rounded-lg bg-white/[0.02] border border-white/[0.04]">
                    <div className="flex items-center gap-2 mb-1">
                      <Search className="h-3.5 w-3.5 text-white/40" />
                      <span className="text-xs font-medium text-white/60">Daily Fresh Credits</span>
                    </div>
                    <p className="text-[11px] text-white/30">Instant mode only. Refresh daily. Cannot be used for auto or agent mode tasks.</p>
                  </div>
                  <div className="p-3 rounded-lg bg-white/[0.02] border border-white/[0.04]">
                    <div className="flex items-center gap-2 mb-1">
                      <Brain className="h-3.5 w-3.5 text-white/40" />
                      <span className="text-xs font-medium text-white/60">Purchased Credits</span>
                    </div>
                    <p className="text-[11px] text-white/30">All modes: auto, instant, agent. File exports included. Never expire.</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Credit Cost Reference */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <Zap className="h-5 w-5" />
                  Credit Usage Guide
                </CardTitle>
                <CardDescription>How many credits each task type costs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] text-center">
                    <Search className="h-5 w-5 mx-auto text-white/40 mb-2" />
                    <p className="text-sm font-medium text-white">Auto Mode</p>
                    <p className="text-xs text-white/40 mt-1">3-20 credits per task</p>
                    <p className="text-[10px] text-white/30 mt-0.5">Smart routing, deep analysis, file exports</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] text-center">
                    <Zap className="h-5 w-5 mx-auto text-white/40 mb-2" />
                    <p className="text-sm font-medium text-white">Instant Mode</p>
                    <p className="text-xs text-white/40 mt-1">2-8 credits per task</p>
                    <p className="text-[10px] text-white/30 mt-0.5">Fast answers, quick lookups</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] text-center">
                    <Brain className="h-5 w-5 mx-auto text-white/40 mb-2" />
                    <p className="text-sm font-medium text-white">Agent Mode</p>
                    <p className="text-xs text-white/40 mt-1">5-40 credits per task</p>
                    <p className="text-[10px] text-white/30 mt-0.5">Multi-step reasoning, complex tasks</p>
                  </div>
                </div>

                <div className="mt-4 text-center">
                  <Button
                    onClick={() => setShowCreditsModal(true)}
                    className="bg-white text-black hover:bg-white/90"
                  >
                    <ShoppingCart className="h-4 w-4 mr-2" />
                    Purchase Credits
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Usage History */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <Receipt className="h-5 w-5" />
                  Recent Usage
                </CardTitle>
                <CardDescription>Your recent AI research activities (last 30 days) &middot; {totalConsumed} credits consumed</CardDescription>
              </CardHeader>
              <CardContent>
                {usageHistory.length === 0 ? (
                  <div className="text-center py-8">
                    <Coins className="h-12 w-12 mx-auto text-white/20 mb-3" />
                    <p className="text-white/60">No usage history yet</p>
                    <p className="text-sm text-white/40 mt-1">Start using AI research to see your activity here</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="border-white/[0.08]">
                        <TableHead className="text-white/60">Date</TableHead>
                        <TableHead className="text-white/60">Service</TableHead>
                        <TableHead className="text-white/60">Operation</TableHead>
                        <TableHead className="text-right text-white/60">Credits</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {usageHistory.slice(0, 20).map((item, i) => (
                        <TableRow key={i} className="border-white/[0.08]">
                          <TableCell className="text-white/60">{formatDate(item.date)}</TableCell>
                          <TableCell className="text-white capitalize">{item.api_service}</TableCell>
                          <TableCell className="text-white/60">{item.api_operation}</TableCell>
                          <TableCell className="text-right text-red-400">-{item.credits_consumed}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function BillingPage() {
  return (
    <ProtectedRoute>
      <BillingContent />
    </ProtectedRoute>
  );
}
