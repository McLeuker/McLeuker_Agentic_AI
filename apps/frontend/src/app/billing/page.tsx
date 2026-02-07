'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
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
} from 'lucide-react';

interface Transaction {
  id: string;
  amount: number;
  type: string;
  description: string | null;
  balance_after: number;
  created_at: string;
}

// Pricing configuration
const SUBSCRIPTION_PLANS = {
  free: {
    name: 'Free',
    monthlyPrice: 0,
    yearlyPrice: 0,
    credits: 50,
    description: 'Get started with basic AI research',
  },
  starter: {
    name: 'Starter',
    monthlyPrice: 29,
    yearlyPrice: 290,
    credits: 500,
    description: 'For individual researchers',
  },
  pro: {
    name: 'Pro',
    monthlyPrice: 79,
    yearlyPrice: 790,
    credits: 2000,
    description: 'For teams and power users',
  },
  enterprise: {
    name: 'Enterprise',
    monthlyPrice: 199,
    yearlyPrice: 1990,
    credits: 10000,
    description: 'For organizations with advanced needs',
  },
};

function BillingContent() {
  const router = useRouter();
  const { user, signOut } = useAuth();

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [usageTransactions, setUsageTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  // Subscription state (would come from a hook in production)
  const [plan, setPlan] = useState('free');
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly' | null>(null);
  const [subscriptionEnd, setSubscriptionEnd] = useState<string | null>(null);
  const [creditBalance, setCreditBalance] = useState(50);
  const [monthlyCredits, setMonthlyCredits] = useState(50);
  const [extraCredits, setExtraCredits] = useState(0);
  const [subscribed, setSubscribed] = useState(false);

  const planConfig = SUBSCRIPTION_PLANS[plan as keyof typeof SUBSCRIPTION_PLANS] || SUBSCRIPTION_PLANS.free;
  const totalCredits = monthlyCredits + extraCredits;
  const usedCredits = totalCredits - creditBalance;
  const usagePercentage = totalCredits > 0 ? (creditBalance / totalCredits) * 100 : 0;

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    if (!user) return;

    try {
      // Fetch user subscription data
      const { data: userData } = await supabase
        .from('users')
        .select('subscription_tier, credits_balance')
        .eq('id', user.id)
        .single();

      if (userData) {
        setPlan(userData.subscription_tier || 'free');
        setCreditBalance(userData.credits_balance || 50);
        setMonthlyCredits(SUBSCRIPTION_PLANS[userData.subscription_tier as keyof typeof SUBSCRIPTION_PLANS]?.credits || 50);
        setSubscribed(userData.subscription_tier !== 'free');
      }

      // Fetch billing transactions
      const { data: billingData } = await supabase
        .from('credit_transactions')
        .select('*')
        .eq('user_id', user.id)
        .in('type', ['purchase', 'subscription_reset', 'refill'])
        .order('created_at', { ascending: false })
        .limit(20);

      // Fetch usage transactions
      const { data: usageData } = await supabase
        .from('credit_transactions')
        .select('*')
        .eq('user_id', user.id)
        .eq('type', 'usage')
        .order('created_at', { ascending: false })
        .limit(50);

      setTransactions(billingData || []);
      setUsageTransactions(usageData || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  const getStatusBadge = () => {
    if (!subscribed) return <Badge variant="outline">Free</Badge>;
    if (subscriptionEnd && new Date(subscriptionEnd) < new Date()) {
      return <Badge variant="destructive">Expired</Badge>;
    }
    return <Badge className="bg-green-600 hover:bg-green-600">Active</Badge>;
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return '—';
    }
  };

  const getActionType = (description: string | null) => {
    if (description?.toLowerCase().includes('research')) return 'AI Research';
    if (description?.toLowerCase().includes('market')) return 'Market Analysis';
    if (description?.toLowerCase().includes('trend')) return 'Trend Report';
    if (description?.toLowerCase().includes('supplier')) return 'Supplier Search';
    if (description?.toLowerCase().includes('pdf')) return 'PDF Export';
    if (description?.toLowerCase().includes('excel')) return 'Excel Export';
    return 'AI Query';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A]">
        <header className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A] border-b border-white/[0.08]">
          <div className="h-16 lg:h-[72px] flex items-center justify-between px-6 lg:px-8">
            <Link href="/dashboard" className="flex items-center gap-2 text-white/60 hover:text-white">
              <ChevronLeft className="h-5 w-5" />
            </Link>
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
          <Link
            href="/dashboard"
            className="flex items-center gap-2 text-white/60 hover:text-white transition-colors"
          >
            <ChevronLeft className="h-5 w-5" />
            <span className="hidden sm:inline">Back to Dashboard</span>
          </Link>
          <Link href="/" className="flex items-center justify-center">
            <span className="font-editorial text-xl lg:text-[22px] text-white tracking-[0.02em]">
              McLeuker<span className="text-white/30">.ai</span>
            </span>
          </Link>
          <button
            onClick={handleSignOut}
            className="flex items-center gap-2 text-white/60 hover:text-white transition-colors"
          >
            <LogOut className="h-5 w-5" />
            <span className="hidden sm:inline">Sign Out</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 lg:pt-28 pb-12 px-4 lg:px-8">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-8 lg:mb-12">
            <h1 className="text-3xl lg:text-4xl font-serif font-light tracking-tight text-white">
              Billing & Credits
            </h1>
            <p className="text-white/60 mt-2">
              Manage your subscription, credits, and billing history
            </p>
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
                    <CardDescription className="mt-1">{planConfig.description}</CardDescription>
                  </div>
                  {getStatusBadge()}
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Plan</p>
                    <p className="text-2xl font-light capitalize text-white">{plan}</p>
                  </div>

                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Billing Cycle</p>
                    <p className="text-2xl font-light capitalize text-white">
                      {billingCycle || '—'}
                    </p>
                  </div>

                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Price</p>
                    <p className="text-2xl font-light text-white">
                      {planConfig.monthlyPrice === 0
                        ? '€0'
                        : `€${
                            billingCycle === 'yearly'
                              ? Math.round((planConfig.yearlyPrice || 0) / 12)
                              : planConfig.monthlyPrice
                          }/mo`}
                    </p>
                  </div>

                  <div className="space-y-1">
                    <p className="text-sm text-white/60">Renewal Date</p>
                    <p className="text-2xl font-light text-white">
                      {subscriptionEnd ? formatDate(subscriptionEnd) : '—'}
                    </p>
                  </div>
                </div>

                <Separator className="bg-white/[0.08]" />

                <div className="flex flex-wrap gap-3">
                  <Link href="/pricing">
                    <Button variant="outline" className="border-white/[0.08] text-white hover:bg-white/[0.08]">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      {subscribed ? 'Change Plan' : 'Upgrade Plan'}
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>

            {/* Credit Overview */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <Coins className="h-5 w-5" />
                  Credit Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Main Credit Display */}
                <div className="space-y-3">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-4xl font-light text-white">{creditBalance.toLocaleString()}</p>
                      <p className="text-sm text-white/60">credits available</p>
                    </div>
                    <div className="text-right text-sm text-white/60">
                      <p>{usedCredits.toLocaleString()} used this period</p>
                    </div>
                  </div>

                  <Progress value={usagePercentage} className="h-2 bg-white/[0.08]" />

                  {usagePercentage < 20 && creditBalance > 0 && (
                    <p className="text-sm text-white/60 flex items-center gap-1">
                      <Zap className="h-4 w-4" />
                      Low credits — consider a refill
                    </p>
                  )}
                </div>

                <Separator className="bg-white/[0.08]" />

                {/* Credit Breakdown */}
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="p-4 rounded-lg bg-white/[0.03]">
                    <p className="text-sm text-white/60">Monthly Allocation</p>
                    <p className="text-xl font-light text-white mt-1">
                      {monthlyCredits.toLocaleString()} credits
                    </p>
                    <p className="text-xs text-white/40 mt-1">Resets each billing cycle</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/[0.03]">
                    <p className="text-sm text-white/60">Extra Credits</p>
                    <p className="text-xl font-light text-white mt-1">
                      {extraCredits.toLocaleString()} credits
                    </p>
                    <p className="text-xs text-white/40 mt-1">Never expires</p>
                  </div>
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
                <CardDescription>Your recent AI research activities</CardDescription>
              </CardHeader>
              <CardContent>
                {usageTransactions.length === 0 ? (
                  <div className="text-center py-8">
                    <Coins className="h-12 w-12 mx-auto text-white/20 mb-3" />
                    <p className="text-white/60">No usage history yet</p>
                    <p className="text-sm text-white/40 mt-1">
                      Start using AI research to see your activity here
                    </p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="border-white/[0.08]">
                        <TableHead className="text-white/60">Date</TableHead>
                        <TableHead className="text-white/60">Action</TableHead>
                        <TableHead className="text-right text-white/60">Credits</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {usageTransactions.slice(0, 10).map((tx) => (
                        <TableRow key={tx.id} className="border-white/[0.08]">
                          <TableCell className="text-white/60">{formatDate(tx.created_at)}</TableCell>
                          <TableCell className="text-white">{getActionType(tx.description || '')}</TableCell>
                          <TableCell className="text-right text-red-400">-{Math.abs(tx.amount)}</TableCell>
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
