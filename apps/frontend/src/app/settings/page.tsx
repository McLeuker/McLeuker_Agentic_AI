'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AccountOverview } from '@/components/profile/AccountOverview';
import { Security } from '@/components/profile/Security';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  User,
  Shield,
  CreditCard,
  Settings,
  ChevronLeft,
  LogOut,
} from 'lucide-react';

const settingsTabs = [
  { id: 'account', label: 'Account', icon: User },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'billing', label: 'Billing', icon: CreditCard },
  { id: 'preferences', label: 'Preferences', icon: Settings },
];

function SettingsContent() {
  const router = useRouter();
  const { signOut } = useAuth();
  const [activeTab, setActiveTab] = useState('account');

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

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
              <BillingPlaceholder />
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

function BillingPlaceholder() {
  return (
    <div className="space-y-6">
      <div className="p-8 rounded-lg border border-white/[0.08] bg-[#1A1A1A] text-center">
        <CreditCard className="h-12 w-12 mx-auto text-white/40 mb-4" />
        <h3 className="text-xl font-medium text-white mb-2">Billing & Credits</h3>
        <p className="text-white/60 mb-6 max-w-md mx-auto">
          Manage your subscription, view credit usage, and access billing history.
        </p>
        <Link
          href="/billing"
          className="inline-flex items-center gap-2 px-6 py-3 bg-white text-black rounded-lg hover:bg-white/90 transition-colors"
        >
          Go to Billing
        </Link>
      </div>
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
