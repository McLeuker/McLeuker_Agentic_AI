'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { User, Mail, Calendar, Clock, Building2, Briefcase, Loader2 } from 'lucide-react';
import { ProfileImageUpload } from './ProfileImageUpload';

interface UserData {
  name: string | null;
  email: string;
  profile_image: string | null;
  subscription_tier: string;
  created_at: string;
  last_active_at: string | null;
  auth_provider: string;
  company: string | null;
  role: string | null;
}

const ROLES = [
  { value: 'designer', label: 'Designer' },
  { value: 'brand', label: 'Brand' },
  { value: 'supplier', label: 'Supplier' },
  { value: 'consultant', label: 'Consultant' },
  { value: 'buyer', label: 'Buyer' },
  { value: 'other', label: 'Other' },
];

export function AccountOverview() {
  const { user } = useAuth();
  const { toast } = useToast();

  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    role: '',
    profile_image: null as string | null,
  });

  // Track original values to detect changes
  const [originalData, setOriginalData] = useState({
    name: '',
    company: '',
    role: '',
    profile_image: null as string | null,
  });

  // Pending image for preview (not yet saved)
  const [pendingImage, setPendingImage] = useState<string | null>(null);

  const hasChanges =
    formData.name !== originalData.name ||
    formData.company !== originalData.company ||
    formData.role !== originalData.role ||
    pendingImage !== null;

  useEffect(() => {
    if (user) {
      fetchUserData();
    }
  }, [user]);

  const fetchUserData = async () => {
    if (!user) return;

    try {
      // First try to get from users table
      const { data: usersData, error: usersError } = await supabase
        .from('users')
        .select('name, email, profile_image, subscription_tier, created_at, last_active_at, auth_provider, company, role')
        .eq('id', user.id)
        .single();

      if (usersData && !usersError) {
        setUserData(usersData);
        const initialData = {
          name: usersData.name || '',
          company: usersData.company || '',
          role: usersData.role || '',
          profile_image: usersData.profile_image,
        };
        setFormData(initialData);
        setOriginalData(initialData);
      } else {
        // User doesn't exist in users table, create them
        console.log('User not found in users table, creating...');
        
        const newUserData = {
          id: user.id,
          email: user.email || '',
          name: user.user_metadata?.full_name || user.user_metadata?.name || '',
          auth_provider: user.app_metadata?.provider || 'email',
          last_active_at: new Date().toISOString(),
        };

        const { data: insertedUser, error: insertError } = await supabase
          .from('users')
          .insert(newUserData)
          .select()
          .single();

        if (insertError) {
          console.error('Error creating user:', insertError);
          // Use fallback data from auth
          const fallbackData: UserData = {
            name: user.user_metadata?.full_name || user.user_metadata?.name || '',
            email: user.email || '',
            profile_image: null,
            subscription_tier: 'free',
            created_at: user.created_at || new Date().toISOString(),
            last_active_at: new Date().toISOString(),
            auth_provider: user.app_metadata?.provider || 'email',
            company: null,
            role: null,
          } as UserData;
          setUserData(fallbackData);
          const initialData = {
            name: fallbackData.name || '',
            company: '',
            role: '',
            profile_image: null,
          };
          setFormData(initialData);
          setOriginalData(initialData);
        } else if (insertedUser) {
          setUserData(insertedUser);
          const initialData = {
            name: insertedUser.name || '',
            company: insertedUser.company || '',
            role: insertedUser.role || '',
            profile_image: insertedUser.profile_image,
          };
          setFormData(initialData);
          setOriginalData(initialData);
        }
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
      // Use auth user data as fallback
      const fallbackData: UserData = {
        name: user.user_metadata?.full_name || '',
        email: user.email || '',
        profile_image: null,
        subscription_tier: 'free',
        created_at: user.created_at || new Date().toISOString(),
        last_active_at: new Date().toISOString(),
        auth_provider: user.app_metadata?.provider || 'email',
        company: null,
        role: null,
      } as UserData;
      setUserData(fallbackData);
      const initialData = {
        name: fallbackData.name || '',
        company: '',
        role: '',
        profile_image: null,
      };
      setFormData(initialData);
      setOriginalData(initialData);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!user || !hasChanges) return;

    setSaving(true);

    try {
      // Build update object with all changed fields
      const updates: Record<string, string | null> = {
        updated_at: new Date().toISOString(),
      };

      if (formData.name !== originalData.name) {
        updates.name = formData.name.trim() || null;
      }

      if (formData.company !== originalData.company) {
        updates.company = formData.company.trim() || null;
      }

      if (formData.role !== originalData.role) {
        updates.role = formData.role || null;
      }

      if (pendingImage) {
        updates.profile_image = pendingImage;
      }

      console.log('Saving profile updates:', updates);

      // Update users table
      const { data: updatedData, error: usersError } = await supabase
        .from('users')
        .update(updates)
        .eq('id', user.id)
        .select('profile_image, name, company, role')
        .single();

      console.log('Supabase update result:', { updatedData, usersError });

      if (usersError) {
        console.error('Users table update failed:', usersError);
        
        // If user doesn't exist, try to insert
        if (usersError.code === 'PGRST116') {
          const { error: insertError } = await supabase
            .from('users')
            .insert({
              id: user.id,
              email: user.email || '',
              name: formData.name.trim() || null,
              company: formData.company.trim() || null,
              role: formData.role || null,
              profile_image: pendingImage || null,
              auth_provider: user.app_metadata?.provider || 'email',
            });

          if (insertError) {
            throw insertError;
          }
        } else {
          throw usersError;
        }
      }

      // profiles table removed during database restructure - users table is the single source of truth

      // Update local state using the confirmed data from Supabase
      const confirmedImage = updatedData?.profile_image ?? pendingImage ?? originalData.profile_image;
      const confirmedName = updatedData?.name ?? formData.name.trim();
      const confirmedCompany = updatedData?.company ?? formData.company.trim();
      const confirmedRole = updatedData?.role ?? formData.role;

      setUserData((prev) =>
        prev
          ? {
              ...prev,
              name: confirmedName,
              company: confirmedCompany,
              role: confirmedRole,
              profile_image: confirmedImage,
            }
          : null
      );

      const newOriginalData = {
        name: confirmedName,
        company: confirmedCompany,
        role: confirmedRole,
        profile_image: confirmedImage,
      };

      setOriginalData(newOriginalData);
      setFormData({
        name: confirmedName,
        company: confirmedCompany,
        role: confirmedRole,
        profile_image: confirmedImage,
      });
      setPendingImage(null);

      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully.',
      });

      // Trigger a page refresh to update avatar in navigation
      window.dispatchEvent(new CustomEvent('profile-updated'));
    } catch (error) {
      console.error('Error saving profile:', error);
      toast({
        title: 'Update failed',
        description: 'Failed to save your changes. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData(originalData);
    setPendingImage(null);
  };

  const getPlanBadgeVariant = (plan: string): 'default' | 'secondary' | 'outline' | 'destructive' => {
    switch (plan?.toLowerCase()) {
      case 'pro':
        return 'default';
      case 'studio':
        return 'secondary';
      case 'enterprise':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return '—';
    }
  };

  const formatDateTime = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      });
    } catch {
      return '—';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-48 bg-[#1A1A1A] rounded-lg" />
        <div className="h-32 bg-[#1A1A1A] rounded-lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Profile Card */}
      <Card className="border-white/[0.08] bg-[#1A1A1A]">
        <CardHeader>
          <CardTitle className="text-lg font-medium text-white">Profile Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Avatar Section */}
          <div className="flex flex-col sm:flex-row items-start gap-6">
            <ProfileImageUpload
              currentImage={pendingImage || formData.profile_image}
              name={formData.name}
              onImageSelect={(base64) => setPendingImage(base64)}
              onError={(msg) => toast({ title: 'Image Error', description: msg, variant: 'destructive' })}
              disabled={saving}
            />

            <div className="flex-1 space-y-1">
              <h2 className="text-2xl font-serif font-light text-white">
                {formData.name || 'Unnamed User'}
              </h2>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant={getPlanBadgeVariant(userData?.subscription_tier || 'free')}>
                  {userData?.subscription_tier?.toUpperCase() || 'FREE'}
                </Badge>
                {userData?.auth_provider && userData.auth_provider !== 'email' && (
                  <Badge variant="outline" className="text-xs">
                    {userData.auth_provider.charAt(0).toUpperCase() + userData.auth_provider.slice(1)}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          <Separator className="bg-white/[0.08]" />

          {/* Editable Fields */}
          <div className="grid gap-6 sm:grid-cols-2">
            {/* Full Name */}
            <div className="space-y-2">
              <Label htmlFor="name" className="text-white/60 flex items-center gap-2">
                <User className="h-4 w-4" />
                Full Name
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                placeholder="Enter your full name"
                className="bg-[#0F0F0F] border-white/[0.08] text-white"
                disabled={saving}
              />
            </div>

            {/* Email (Read-only) */}
            <div className="space-y-2">
              <Label className="text-white/60 flex items-center gap-2">
                <Mail className="h-4 w-4" />
                Email Address
              </Label>
              <Input
                value={userData?.email || ''}
                disabled
                className="bg-[#0A0A0A] border-white/[0.08] text-white/60 cursor-not-allowed"
              />
              <p className="text-xs text-white/40">Contact support to change email</p>
            </div>

            {/* Company */}
            <div className="space-y-2">
              <Label htmlFor="company" className="text-white/60 flex items-center gap-2">
                <Building2 className="h-4 w-4" />
                Company / Organization
              </Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => setFormData((prev) => ({ ...prev, company: e.target.value }))}
                placeholder="Enter company name"
                className="bg-[#0F0F0F] border-white/[0.08] text-white"
                disabled={saving}
              />
            </div>

            {/* Role */}
            <div className="space-y-2">
              <Label className="text-white/60 flex items-center gap-2">
                <Briefcase className="h-4 w-4" />
                Role
              </Label>
              <Select
                value={formData.role}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, role: value }))}
                disabled={saving}
              >
                <SelectTrigger className="bg-[#0F0F0F] border-white/[0.08] text-white">
                  <SelectValue placeholder="Select your role" />
                </SelectTrigger>
                <SelectContent>
                  {ROLES.map((role) => (
                    <SelectItem key={role.value} value={role.value}>
                      {role.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator className="bg-white/[0.08]" />

          {/* Read-only Account Details */}
          <div className="grid gap-6 sm:grid-cols-3">
            <div className="space-y-2">
              <Label className="text-white/60 flex items-center gap-2">
                <User className="h-4 w-4" />
                Account Type
              </Label>
              <p className="text-sm font-medium capitalize text-white">
                {userData?.subscription_tier || 'Free'} Plan
              </p>
            </div>

            <div className="space-y-2">
              <Label className="text-white/60 flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Member Since
              </Label>
              <p className="text-sm font-medium text-white">
                {userData?.created_at ? formatDate(userData.created_at) : '—'}
              </p>
            </div>

            <div className="space-y-2">
              <Label className="text-white/60 flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Last Login
              </Label>
              <p className="text-sm font-medium text-white">
                {userData?.last_active_at ? formatDateTime(userData.last_active_at) : '—'}
              </p>
            </div>
          </div>

          <Separator className="bg-white/[0.08]" />

          {/* Save/Cancel Buttons */}
          <div className="flex flex-col-reverse sm:flex-row gap-3 sm:justify-end">
            {hasChanges && (
              <Button
                variant="outline"
                onClick={handleCancel}
                disabled={saving}
                className="sm:w-auto border-white/[0.08] text-white hover:bg-white/[0.08]"
              >
                Cancel
              </Button>
            )}
            <Button
              onClick={handleSave}
              disabled={!hasChanges || saving}
              className="bg-white text-black hover:bg-white/90 sm:w-auto"
            >
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
