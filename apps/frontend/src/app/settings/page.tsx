'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AccountOverview } from '@/components/profile/AccountOverview';
import { Security } from '@/components/profile/Security';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  User,
  Shield,
  CreditCard,
  Settings,
  ChevronLeft,
  LogOut,
  Crown,
  TrendingUp,
  Coins,
  Globe,
  ArrowRight,
  ExternalLink,
  Zap,
  Lock,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

const PLAN_DETAILS: Record<string, { name: string; dailyCredits: number; monthlyCredits: number; maxDomains: number; price: string; color: string }> = {
  free: { name: 'Free', dailyCredits: 15, monthlyCredits: 450, maxDomains: 2, price: '$0', color: 'bg-white/10 text-white/60' },
  standard: { name: 'Standard', dailyCredits: 50, monthlyCredits: 1500, maxDomains: 5, price: '$19/mo', color: 'bg-blue-600/20 text-blue-400 border-blue-500/30' },
  pro: { name: 'Pro', dailyCredits: 300, monthlyCredits: 9000, maxDomains: 10, price: '$99/mo', color: 'bg-purple-600/20 text-purple-400 border-purple-500/30' },
  enterprise: { name: 'Enterprise', dailyCredits: 500, monthlyCredits: 25000, maxDomains: 10, price: 'Custom', color: 'bg-green-600/20 text-green-400 border-green-500/30' },
};

const settingsTabs = [
  { id: 'account', label: 'Account', icon: User },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'billing', label: 'Billing', icon: CreditCard },
  { id: 'preferences', label: 'Preferences', icon: Settings },
];

function SettingsContent() {
  const router = useRouter();
  const { user, session, signOut } = useAuth();
  const [activeTab, setActiveTab] = useState('account');
  const [plan, setPlan] = useState('free');
  const [creditBalance, setCreditBalance] = useState(0);

  const getAuthHeaders = useCallback(() => {
    const token = session?.access_token;
    return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
  }, [session]);

  useEffect(() => {
    if (user && session) {
      fetchPlanInfo();
    }
  }, [user, session]);

  const fetchPlanInfo = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/billing/credits`, { headers: getAuthHeaders() });
      const data = await res.json();
      if (data.success) {
        setPlan(data.data?.plan || 'free');
        setCreditBalance(data.data?.balance || 0);
      }
    } catch (error) {
      console.error('Error fetching plan info:', error);
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

  const planInfo = PLAN_DETAILS[plan] || PLAN_DETAILS.free;

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A] border-b border-white/[0.08]">
        <div className="h-16 lg:h-[72px] flex items-center justify-between px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 text-white/60 hover:text-white transition-colors"
            >
              <ChevronLeft className="h-5 w-5" />
              <span className="hidden sm:inline">Back to Dashboard</span>
            </Link>
          </div>
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
        <div className="max-w-4xl mx-auto">
          {/* Page Title */}
          <div className="mb-8 lg:mb-12">
            <h1 className="text-3xl lg:text-4xl font-serif font-light tracking-tight text-white">
              Account Settings
            </h1>
            <p className="text-white/60 mt-2">
              Manage your account, security, and preferences
            </p>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
            <TabsList className="w-full justify-start bg-transparent border-b border-white/[0.08] rounded-none p-0 h-auto">
              {settingsTabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <TabsTrigger
                    key={tab.id}
                    value={tab.id}
                    className={cn(
                      'flex items-center gap-2 px-4 py-3 rounded-none border-b-2 border-transparent',
                      'data-[state=active]:border-white data-[state=active]:text-white',
                      'text-white/60 hover:text-white transition-colors',
                      'bg-transparent data-[state=active]:bg-transparent'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="hidden sm:inline">{tab.label}</span>
                  </TabsTrigger>
                );
              })}
            </TabsList>

            <TabsContent value="account" className="mt-8">
              <AccountOverview />
            </TabsContent>

            <TabsContent value="security" className="mt-8">
              <Security />
            </TabsContent>

            <TabsContent value="billing" className="mt-8">
              <BillingTab
                plan={plan}
                planInfo={planInfo}
                creditBalance={creditBalance}
                onManageSubscription={handleManageSubscription}
              />
            </TabsContent>

            <TabsContent value="preferences" className="mt-8">
              <PreferencesPlaceholder />
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}

function BillingTab({ plan, planInfo, creditBalance, onManageSubscription }: {
  plan: string;
  planInfo: typeof PLAN_DETAILS['free'];
  creditBalance: number;
  onManageSubscription: () => void;
}) {
  return (
    <div className="space-y-6">
      {/* Current Plan Card */}
      <Card className="border-white/[0.08] bg-[#1A1A1A]">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                <Crown className="h-5 w-5" />
                Your Plan
              </CardTitle>
              <CardDescription className="mt-1">Current subscription and usage</CardDescription>
            </div>
            <Badge className={planInfo.color}>{planInfo.name}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="grid gap-4 sm:grid-cols-4">
            <div className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.04]">
              <p className="text-[11px] text-white/40 uppercase tracking-wider mb-1">Plan</p>
              <p className="text-lg font-medium text-white">{planInfo.name}</p>
              <p className="text-[11px] text-white/30">{planInfo.price}</p>
            </div>
            <div className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.04]">
              <p className="text-[11px] text-white/40 uppercase tracking-wider mb-1">Credits</p>
              <p className="text-lg font-medium text-white">{creditBalance.toLocaleString()}</p>
              <p className="text-[11px] text-white/30">available</p>
            </div>
            <div className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.04]">
              <p className="text-[11px] text-white/40 uppercase tracking-wider mb-1">Daily</p>
              <p className="text-lg font-medium text-white">{planInfo.dailyCredits}</p>
              <p className="text-[11px] text-white/30">fresh credits/day</p>
            </div>
            <div className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.04]">
              <p className="text-[11px] text-white/40 uppercase tracking-wider mb-1">Domains</p>
              <p className="text-lg font-medium text-white">{planInfo.maxDomains === 10 ? 'All 10' : planInfo.maxDomains}</p>
              <p className="text-[11px] text-white/30">accessible</p>
            </div>
          </div>

          {/* Upgrade Banner */}
          {(plan === 'free' || plan === 'standard') && (
            <>
              <Separator className="bg-white/[0.06]" />
              <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-white/[0.05] flex items-center justify-center">
                      <TrendingUp className="h-5 w-5 text-white/50" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">
                        {plan === 'free' ? 'Unlock more with Standard or Pro' : 'Go Pro for full access'}
                      </p>
                      <p className="text-xs text-white/40">
                        {plan === 'free'
                          ? 'Deep search, file exports, agent mode, and more domains'
                          : 'Agent mode, creative, all 10 domains, 300 daily credits'}
                      </p>
                    </div>
                  </div>
                  <Link href="/pricing">
                    <Button className="bg-white text-black hover:bg-white/90 text-sm">
                      Upgrade <ArrowRight className="h-4 w-4 ml-1" />
                    </Button>
                  </Link>
                </div>
              </div>
            </>
          )}

          <div className="flex flex-wrap gap-3">
            <Link href="/billing">
              <Button variant="outline" className="border-white/[0.08] text-white hover:bg-white/[0.08]">
                <Coins className="h-4 w-4 mr-2" />
                Full Billing Dashboard
              </Button>
            </Link>
            {plan !== 'free' && (
              <Button variant="outline" className="border-white/[0.08] text-white hover:bg-white/[0.08]" onClick={onManageSubscription}>
                <ExternalLink className="h-4 w-4 mr-2" />
                Manage Subscription
              </Button>
            )}
            <Link href="/pricing">
              <Button variant="outline" className="border-white/[0.08] text-white hover:bg-white/[0.08]">
                <CreditCard className="h-4 w-4 mr-2" />
                View Plans
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Feature Access */}
      <Card className="border-white/[0.08] bg-[#1A1A1A]">
        <CardHeader>
          <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
            <Zap className="h-5 w-5" />
            Feature Access
          </CardTitle>
          <CardDescription>What your current plan includes</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
            {[
              { feature: 'Instant Search', available: true, plans: 'All plans' },
              { feature: 'Deep Search & Analysis', available: plan !== 'free', plans: 'Standard+' },
              { feature: 'Agent Mode', available: plan === 'pro' || plan === 'enterprise', plans: 'Pro+' },
              { feature: 'Creative Mode', available: plan === 'pro' || plan === 'enterprise', plans: 'Pro+' },
              { feature: 'PDF / Excel / PPTX Exports', available: plan !== 'free', plans: 'Standard+' },
              { feature: 'All 10 Domains', available: plan === 'pro' || plan === 'enterprise', plans: 'Pro+' },
              { feature: 'Priority Support', available: plan !== 'free', plans: 'Standard+' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-white/[0.02] transition-colors">
                <div className="flex items-center gap-3">
                  {item.available ? (
                    <div className="w-5 h-5 rounded-full bg-white/[0.06] flex items-center justify-center">
                      <Zap className="w-3 h-3 text-white/50" />
                    </div>
                  ) : (
                    <div className="w-5 h-5 rounded-full bg-white/[0.03] flex items-center justify-center">
                      <Lock className="w-3 h-3 text-white/15" />
                    </div>
                  )}
                  <span className={cn("text-sm", item.available ? "text-white/70" : "text-white/30")}>{item.feature}</span>
                </div>
                <span className="text-[11px] text-white/25">{item.plans}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function PreferencesPlaceholder() {
  return (
    <div className="space-y-6">
      <div className="p-8 rounded-lg border border-white/[0.08] bg-[#1A1A1A] text-center">
        <Settings className="h-12 w-12 mx-auto text-white/40 mb-4" />
        <h3 className="text-xl font-medium text-white mb-2">Workspace Preferences</h3>
        <p className="text-white/60 mb-6 max-w-md mx-auto">
          Customize your research experience, default settings, and AI output preferences.
        </p>
        <Link
          href="/preferences"
          className="inline-flex items-center gap-2 px-6 py-3 bg-white text-black rounded-lg hover:bg-white/90 transition-colors"
        >
          Go to Preferences
        </Link>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}
