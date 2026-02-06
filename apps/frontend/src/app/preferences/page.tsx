'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import {
  Settings,
  FileText,
  Globe,
  Sparkles,
  Clock,
  Check,
  ChevronLeft,
  LogOut,
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

function PreferencesContent() {
  const router = useRouter();
  const { signOut } = useAuth();
  const { toast } = useToast();

  const [currentSector, setCurrentSector] = useState('fashion');
  const [exportFormat, setExportFormat] = useState('pdf');
  const [outputStyle, setOutputStyle] = useState('strategic');
  const [language, setLanguage] = useState('en');
  const [timezone, setTimezone] = useState('Europe/Paris');
  const [aiDetail, setAiDetail] = useState('detailed');

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  const handleSave = () => {
    // In production, this would save to the database
    toast({
      title: 'Preferences saved',
      description: 'Your workspace preferences have been updated.',
    });
  };

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
                  value={currentSector}
                  onValueChange={setCurrentSector}
                  className="grid grid-cols-2 sm:grid-cols-3 gap-3"
                >
                  {SECTORS.map((sector) => (
                    <Label
                      key={sector.id}
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors',
                        currentSector === sector.id
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value={sector.id} className="sr-only" />
                      <span className="text-sm font-medium text-white">{sector.label}</span>
                      {currentSector === sector.id && <Check className="h-4 w-4 ml-auto text-white" />}
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
                  value={exportFormat}
                  onValueChange={setExportFormat}
                  className="flex gap-4"
                >
                  <Label
                    className={cn(
                      'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                      exportFormat === 'pdf'
                        ? 'border-white bg-white/[0.05]'
                        : 'border-white/[0.08] hover:border-white/30'
                    )}
                  >
                    <RadioGroupItem value="pdf" className="sr-only" />
                    <div>
                      <span className="text-sm font-medium text-white">PDF</span>
                      <p className="text-xs text-white/60">Best for sharing</p>
                    </div>
                    {exportFormat === 'pdf' && <Check className="h-4 w-4 ml-auto text-white" />}
                  </Label>
                  <Label
                    className={cn(
                      'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                      exportFormat === 'excel'
                        ? 'border-white bg-white/[0.05]'
                        : 'border-white/[0.08] hover:border-white/30'
                    )}
                  >
                    <RadioGroupItem value="excel" className="sr-only" />
                    <div>
                      <span className="text-sm font-medium text-white">Excel</span>
                      <p className="text-xs text-white/60">Best for analysis</p>
                    </div>
                    {exportFormat === 'excel' && <Check className="h-4 w-4 ml-auto text-white" />}
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
                    value={outputStyle}
                    onValueChange={setOutputStyle}
                    className="flex gap-4"
                  >
                    <Label
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                        outputStyle === 'strategic'
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value="strategic" className="sr-only" />
                      <div>
                        <span className="text-sm font-medium text-white">Strategic</span>
                        <p className="text-xs text-white/60">High-level insights</p>
                      </div>
                      {outputStyle === 'strategic' && <Check className="h-4 w-4 ml-auto text-white" />}
                    </Label>
                    <Label
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                        outputStyle === 'operational'
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value="operational" className="sr-only" />
                      <div>
                        <span className="text-sm font-medium text-white">Operational</span>
                        <p className="text-xs text-white/60">Actionable details</p>
                      </div>
                      {outputStyle === 'operational' && <Check className="h-4 w-4 ml-auto text-white" />}
                    </Label>
                  </RadioGroup>
                </div>

                <div className="space-y-3">
                  <Label className="text-sm text-white/60">Response Length</Label>
                  <RadioGroup value={aiDetail} onValueChange={setAiDetail} className="flex gap-4">
                    <Label
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                        aiDetail === 'concise'
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value="concise" className="sr-only" />
                      <div>
                        <span className="text-sm font-medium text-white">Concise</span>
                        <p className="text-xs text-white/60">Quick answers</p>
                      </div>
                      {aiDetail === 'concise' && <Check className="h-4 w-4 ml-auto text-white" />}
                    </Label>
                    <Label
                      className={cn(
                        'flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors flex-1',
                        aiDetail === 'detailed'
                          ? 'border-white bg-white/[0.05]'
                          : 'border-white/[0.08] hover:border-white/30'
                      )}
                    >
                      <RadioGroupItem value="detailed" className="sr-only" />
                      <div>
                        <span className="text-sm font-medium text-white">Detailed</span>
                        <p className="text-xs text-white/60">Comprehensive analysis</p>
                      </div>
                      {aiDetail === 'detailed' && <Check className="h-4 w-4 ml-auto text-white" />}
                    </Label>
                  </RadioGroup>
                </div>
              </CardContent>
            </Card>

            {/* Language & Timezone */}
            <Card className="border-white/[0.08] bg-[#1A1A1A]">
              <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                  <Clock className="h-5 w-5" />
                  Language & Region
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-6 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label className="text-sm text-white/60">Language</Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger className="bg-[#0F0F0F] border-white/[0.08] text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="fr">Français</SelectItem>
                        <SelectItem value="de">Deutsch</SelectItem>
                        <SelectItem value="es">Español</SelectItem>
                        <SelectItem value="it">Italiano</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm text-white/60">Timezone</Label>
                    <Select value={timezone} onValueChange={setTimezone}>
                      <SelectTrigger className="bg-[#0F0F0F] border-white/[0.08] text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Europe/Paris">Paris (CET)</SelectItem>
                        <SelectItem value="Europe/London">London (GMT)</SelectItem>
                        <SelectItem value="America/New_York">New York (EST)</SelectItem>
                        <SelectItem value="America/Los_Angeles">Los Angeles (PST)</SelectItem>
                        <SelectItem value="Asia/Tokyo">Tokyo (JST)</SelectItem>
                        <SelectItem value="Asia/Shanghai">Shanghai (CST)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button
                onClick={handleSave}
                size="lg"
                className="bg-white text-black hover:bg-white/90"
              >
                Save Preferences
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
