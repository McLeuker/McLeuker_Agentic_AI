'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useToast } from '@/hooks/use-toast';
import {
  Settings,
  FileText,
  Globe,
  Sparkles,
  Check,
  ChevronLeft,
  LogOut,
  Loader2,
} from 'lucide-react';

// Sectors configuration
const SECTORS = [
  { id: 'fashion', label: 'Fashion' },
  { id: 'beauty', label: 'Beauty' },
  { id: 'lifestyle', label: 'Lifestyle' },
  { id: 'luxury', label: 'Luxury' },
  { id: 'tech', label: 'Technology' },
  { id: 'sustainability', label: 'Sustainability' },
];

// Default preferences
const DEFAULT_PREFERENCES = {
  default_sector: 'fashion',
  export_format: 'pdf',
  output_style: 'strategic',
  ai_detail: 'detailed',
};

interface UserPreferences {
  default_sector: string;
  export_format: string;
  output_style: string;
  ai_detail: string;
}

function PreferencesContent() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const { toast } = useToast();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [preferences, setPreferences] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [originalPreferences, setOriginalPreferences] = useState<UserPreferences>(DEFAULT_PREFERENCES);

  const hasChanges =
    preferences.default_sector !== originalPreferences.default_sector ||
    preferences.export_format !== originalPreferences.export_format ||
    preferences.output_style !== originalPreferences.output_style ||
    preferences.ai_detail !== originalPreferences.ai_detail;

  // Load preferences from Supabase
  const loadPreferences = useCallback(async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('users')
        .select('preferences')
        .eq('id', user.id)
        .single();

      if (error) {
        console.error('Error loading preferences:', error);
        return;
      }

      if (data?.preferences) {
        const saved = typeof data.preferences === 'string'
          ? JSON.parse(data.preferences)
          : data.preferences;

        const merged: UserPreferences = {
          default_sector: saved.default_sector || DEFAULT_PREFERENCES.default_sector,
          export_format: saved.export_format || DEFAULT_PREFERENCES.export_format,
          output_style: saved.output_style || DEFAULT_PREFERENCES.output_style,
          ai_detail: saved.ai_detail || DEFAULT_PREFERENCES.ai_detail,
        };

        setPreferences(merged);
        setOriginalPreferences(merged);
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  const handleSave = async () => {
    if (!user || !hasChanges) return;

    setSaving(true);

    try {
      const { error } = await supabase
        .from('users')
        .update({
          preferences: preferences,
          updated_at: new Date().toISOString(),
        })
        .eq('id', user.id);

      if (error) {
        console.error('Error saving preferences:', error);
        toast({
          title: 'Save failed',
          description: `Failed to save preferences: ${error.message}`,
          variant: 'destructive',
        });
        return;
      }

      setOriginalPreferences({ ...preferences });

      toast({
        title: 'Preferences saved',
        description: 'Your workspace preferences have been updated and will apply across sessions.',
      });

      // Dispatch event so other components can react to preference changes
      window.dispatchEvent(new CustomEvent('preferences-updated', { detail: preferences }));
    } catch (error) {
      console.error('Error saving preferences:', error);
      toast({
        title: 'Save failed',
        description: 'An unexpected error occurred. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <div className="flex items-center gap-3 text-white/60">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading preferences...</span>
        </div>
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
          <Link href="/" className="flex items-center">
            <span className="font-editorial text-xl lg:text-2xl text-white tracking-[0.02em]">
              McLeuker
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
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="mb-8 lg:mb-12">
            <h1 className="text-3xl lg:text-4xl font-serif font-light tracking-tight text-white">
              Workspace Preferences
            </h1>
            <p className="text-white/60 mt-2">Customize your research experience</p>
          </div>

          <div className="space-y-6">
            {/* Default Research Domain */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <Globe className="h-5 w-5" />
                  Default Research Domain
                </CardTitle>
                <CardDescription>Your preferred industry focus for AI research</CardDescription>
              </CardHeader>
              <CardContent>
                <RadioGroup
                  value={preferences.default_sector}
                  onValueChange={(value) =>
                    setPreferences((prev) => ({ ...prev, default_sector: value }))
                  }
                  className="grid grid-cols-2 sm:grid-cols-3 gap-3"
                >
                  {SECTORS.map((sector) => (
                    <Label
                      key={sector.id}
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors',
                        preferences.default_sector === sector.id
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value={sector.id} className="sr-only" />
                      <span className="text-sm font-medium text-white">{sector.label}</span>
                      {preferences.default_sector === sector.id && (
                        <Check className="h-4 w-4 ml-auto text-white" />
                      )}
                    </Label>
                  ))}
                </RadioGroup>
              </CardContent>
            </Card>

            {/* Export Format */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <FileText className="h-5 w-5" />
                  Default Export Format
                </CardTitle>
                <CardDescription>Preferred format for downloading reports</CardDescription>
              </CardHeader>
              <CardContent>
                <RadioGroup
                  value={preferences.export_format}
                  onValueChange={(value) =>
                    setPreferences((prev) => ({ ...prev, export_format: value }))
                  }
                  className="flex gap-4"
                >
                  <Label
                    className={cn(
                      'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                      preferences.export_format === 'pdf'
                        ? 'border-white bg-white/[0.05]'
                        : 'border-white/[0.08] hover:border-white/30'
                    )}
                  >
                    <RadioGroupItem value="pdf" className="sr-only" />
                    <div>
                      <span className="text-sm font-medium text-white">PDF</span>
                      <p className="text-xs text-white/60">Best for sharing</p>
                    </div>
                    {preferences.export_format === 'pdf' && (
                      <Check className="h-4 w-4 ml-auto text-white" />
                    )}
                  </Label>
                  <Label
                    className={cn(
                      'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                      preferences.export_format === 'excel'
                        ? 'border-white bg-white/[0.05]'
                        : 'border-white/[0.08] hover:border-white/30'
                    )}
                  >
                    <RadioGroupItem value="excel" className="sr-only" />
                    <div>
                      <span className="text-sm font-medium text-white">Excel</span>
                      <p className="text-xs text-white/60">Best for analysis</p>
                    </div>
                    {preferences.export_format === 'excel' && (
                      <Check className="h-4 w-4 ml-auto text-white" />
                    )}
                  </Label>
                </RadioGroup>
              </CardContent>
            </Card>

            {/* Output Style */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <Sparkles className="h-5 w-5" />
                  AI Output Style
                </CardTitle>
                <CardDescription>Customize how AI responses are structured</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-3">
                  <Label className="text-sm text-white/60">Response Tone</Label>
                  <RadioGroup
                    value={preferences.output_style}
                    onValueChange={(value) =>
                      setPreferences((prev) => ({ ...prev, output_style: value }))
                    }
                    className="flex gap-4"
                  >
                    <Label
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                        preferences.output_style === 'strategic'
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value="strategic" className="sr-only" />
                      <div>
                        <span className="text-sm font-medium text-white">Strategic</span>
                        <p className="text-xs text-white/60">High-level insights</p>
                      </div>
                      {preferences.output_style === 'strategic' && (
                        <Check className="h-4 w-4 ml-auto text-white" />
                      )}
                    </Label>
                    <Label
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                        preferences.output_style === 'operational'
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value="operational" className="sr-only" />
                      <div>
                        <span className="text-sm font-medium text-white">Operational</span>
                        <p className="text-xs text-white/60">Actionable details</p>
                      </div>
                      {preferences.output_style === 'operational' && (
                        <Check className="h-4 w-4 ml-auto text-white" />
                      )}
                    </Label>
                  </RadioGroup>
                </div>

                <div className="space-y-3">
                  <Label className="text-sm text-white/60">Response Length</Label>
                  <RadioGroup
                    value={preferences.ai_detail}
                    onValueChange={(value) =>
                      setPreferences((prev) => ({ ...prev, ai_detail: value }))
                    }
                    className="flex gap-4"
                  >
                    <Label
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                        preferences.ai_detail === 'concise'
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value="concise" className="sr-only" />
                      <div>
                        <span className="text-sm font-medium text-white">Concise</span>
                        <p className="text-xs text-white/60">Quick answers</p>
                      </div>
                      {preferences.ai_detail === 'concise' && (
                        <Check className="h-4 w-4 ml-auto text-white" />
                      )}
                    </Label>
                    <Label
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                        preferences.ai_detail === 'detailed'
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value="detailed" className="sr-only" />
                      <div>
                        <span className="text-sm font-medium text-white">Detailed</span>
                        <p className="text-xs text-white/60">Comprehensive analysis</p>
                      </div>
                      {preferences.ai_detail === 'detailed' && (
                        <Check className="h-4 w-4 ml-auto text-white" />
                      )}
                    </Label>
                  </RadioGroup>
                </div>
              </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button
                onClick={handleSave}
                disabled={!hasChanges || saving}
                size="lg"
                className="bg-white text-black hover:bg-white/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Preferences'
                )}
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function PreferencesPage() {
  return (
    <ProtectedRoute>
      <PreferencesContent />
    </ProtectedRoute>
  );
}
