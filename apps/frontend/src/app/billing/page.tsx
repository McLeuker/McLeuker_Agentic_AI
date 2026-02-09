'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
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
  Calendar,
  TrendingUp,
  ArrowUpRight,
  Zap,
  Receipt,
  ChevronLeft,
  LogOut,
  CheckCircle,
  Clock,
  XCircle,
  Gift,
  ShoppingCart,
  ExternalLink,
  Flame,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

interface CreditSummary {
  balance: number;
  plan: string;
  plan_name?: string;
  monthly_credits?: number;
  daily_credits_available?: boolean;
  streak?: number;
  total_consumed?: number;
}

interface UsageItem {
  date: string;
  api_service: string;
  api_operation: string;
  credits_consumed: number;
  task_type?: string;
}

interface CreditPackage {
  slug: string;
  name: string;
  credits: number;
  price_usd: number;
  bonus_credits: number;
  popular?: boolean;
}

function BillingContent() {
  const router = useRouter();
  const { user, session, signOut } = useAuth();

  const [creditSummary, setCreditSummary] = useState<CreditSummary | null>(null);
  const [usageHistory, setUsageHistory] = useState<UsageItem[]>([]);
  const [creditPackages, setCreditPackages] = useState<CreditPackage[]>([]);
  const [loading, setLoading] = useState(true);
  const [claimingDaily, setClaimingDaily] = useState(false);
  const [dailyClaimed, setDailyClaimed] = useState(false);

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
      const [creditsRes, usageRes, packagesRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/billing/credits`, { headers: getAuthHeaders() }),
        fetch(`${API_URL}/api/v1/billing/usage?days=30`, { headers: getAuthHeaders() }),
        fetch(`${API_URL}/api/v1/billing/credits/packages`),
      ]);

      const creditsData = await creditsRes.json();
      const usageData = await usageRes.json();
      const packagesData = await packagesRes.json();

      if (creditsData.success) setCreditSummary(creditsData.data);
      if (usageData.success) setUsageHistory(usageData.history || []);
      if (packagesData.success) setCreditPackages(packagesData.packages || []);
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

  const balance = creditSummary?.balance || 0;
  const plan = creditSummary?.plan || 'free';
  const planName = creditSummary?.plan_name || plan.charAt(0).toUpperCase() + plan.slice(1);
  const monthlyCredits = creditSummary?.monthly_credits || 50;
  const totalConsumed = creditSummary?.total_consumed || 0;
  const usagePercentage = monthlyCredits > 0 ? Math.min(100, (balance / monthlyCredits) * 100) : 0;

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
          <button onClick={handleSignOut} className="flex items-center gap-2 text-white/60 hover:text-white transition-colors">
            <LogOut className="h-5 w-5" />
            <span className="hidden sm:inline">Sign Out</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 lg:pt-28 pb-12 px-4 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="mb-8 lg:mb-12">
            <h1 className="text-3xl lg:text-4xl font-serif font-light tracking-tight text-white">Billing & Credits</h1>
            <p className="text-white/60 mt-2">Manage your subscription, credits, and billing history</p>
          </div>

          <div className="space-y-8">
            {/* Current Plan */}
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
                  <Badge className={cn(plan === 'free' ? 'bg-white/10 text-white/60' : 'bg-green-600/20 text-green-400 border-green-500/30')}>
                    {planName}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-6 sm:grid-cols-3">
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Plan</p>
                    <p className="text-2xl font-light text-white">{planName}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Monthly Credits</p>
                    <p className="text-2xl font-light text-white">{monthlyCredits.toLocaleString()}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Total Used</p>
                    <p className="text-2xl font-light text-white">{totalConsumed.toLocaleString()}</p>
                  </div>
                </div>

                <Separator className="bg-white/[0.08]" />

                <div className="flex flex-wrap gap-3">
                  <Link href="/pricing">
                    <Button variant="outline" className="border-white/[0.08] text-white hover:bg-white/[0.08]">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      {plan === 'free' ? 'Upgrade Plan' : 'Change Plan'}
                    </Button>
                  </Link>
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
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <Coins className="h-5 w-5" />
                  Credit Balance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-4xl font-light text-white">{balance.toLocaleString()}</p>
                      <p className="text-sm text-white/60">credits available</p>
                    </div>
                    {creditSummary?.streak && creditSummary.streak > 1 && (
                      <div className="flex items-center gap-1.5 text-orange-400">
                        <Flame className="h-4 w-4" />
                        <span className="text-sm font-medium">{creditSummary.streak}-day streak</span>
                      </div>
                    )}
                  </div>
                  <Progress value={usagePercentage} className="h-2 bg-white/[0.08]" />
                  {balance < 20 && (
                    <p className="text-sm text-orange-400 flex items-center gap-1">
                      <Zap className="h-4 w-4" />
                      Low credits — claim daily credits or purchase more
                    </p>
                  )}
                </div>

                <Separator className="bg-white/[0.08]" />

                {/* Daily Credits Claim */}
                <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-white/[0.05] flex items-center justify-center">
                        <Gift className="h-5 w-5 text-white/50" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">Daily Free Credits</p>
                        <p className="text-xs text-white/40">Claim 50 free credits every day</p>
                      </div>
                    </div>
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
              </CardContent>
            </Card>

            {/* Credit Packages */}
            {creditPackages.length > 0 && (
              <Card className="border-white/[0.08] bg-[#1A1A1A]">
                <CardHeader>
                  <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                    <ShoppingCart className="h-5 w-5" />
                    Buy Credits
                  </CardTitle>
                  <CardDescription>Purchase additional credits anytime</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                    {creditPackages.map((pkg) => (
                      <div
                        key={pkg.slug}
                        className={cn(
                          "p-4 rounded-xl border transition-all cursor-pointer hover:border-white/20",
                          pkg.popular ? "border-white/15 bg-white/[0.04]" : "border-white/[0.06] bg-white/[0.02]"
                        )}
                      >
                        {pkg.popular && (
                          <Badge className="mb-2 bg-white/10 text-white/70 text-[10px]">Popular</Badge>
                        )}
                        <p className="text-2xl font-light text-white">{pkg.credits.toLocaleString()}</p>
                        <p className="text-xs text-white/40">credits</p>
                        {pkg.bonus_credits > 0 && (
                          <p className="text-xs text-green-400 mt-1">+{pkg.bonus_credits} bonus</p>
                        )}
                        <p className="text-lg font-medium text-white mt-3">${pkg.price_usd}</p>
                        <p className="text-[10px] text-white/30">${(pkg.price_usd / (pkg.credits + pkg.bonus_credits) * 100).toFixed(1)}¢ per credit</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Usage History */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <Receipt className="h-5 w-5" />
                  Recent Usage
                </CardTitle>
                <CardDescription>Your recent AI research activities (last 30 days)</CardDescription>
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
