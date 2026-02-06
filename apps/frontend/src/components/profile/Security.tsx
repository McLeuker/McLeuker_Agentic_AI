'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Shield, ShieldCheck, Key, LogOut, Monitor, Loader2 } from 'lucide-react';
import { SupportRequest } from './SupportRequest';

export function Security() {
  const { user, signOut } = useAuth();
  const { toast } = useToast();

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);
  const [loggingOutAll, setLoggingOutAll] = useState(false);

  const handleChangePassword = async () => {
    if (!newPassword || !confirmPassword) {
      toast({
        title: 'Missing fields',
        description: 'Please fill in all password fields.',
        variant: 'destructive',
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      toast({
        title: "Passwords don't match",
        description: 'New password and confirmation must match.',
        variant: 'destructive',
      });
      return;
    }

    if (newPassword.length < 8) {
      toast({
        title: 'Password too short',
        description: 'Password must be at least 8 characters.',
        variant: 'destructive',
      });
      return;
    }

    setChangingPassword(true);
    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      });

      if (error) throw error;

      toast({
        title: 'Password updated',
        description: 'Your password has been successfully changed.',
      });

      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      toast({
        title: 'Update failed',
        description: error.message || 'Failed to update password.',
        variant: 'destructive',
      });
    } finally {
      setChangingPassword(false);
    }
  };

  const handleLogoutAllSessions = async () => {
    setLoggingOutAll(true);
    try {
      // Sign out from all sessions
      await supabase.auth.signOut({ scope: 'global' });

      toast({
        title: 'Logged out everywhere',
        description: 'All sessions have been terminated.',
      });

      // Redirect to login
      window.location.href = '/login';
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'Failed to log out from all sessions.',
        variant: 'destructive',
      });
    } finally {
      setLoggingOutAll(false);
    }
  };

  const isOAuthUser = user?.app_metadata?.provider !== 'email';

  return (
    <div className="space-y-6">
      {/* Password Section */}
      <Card className="border-white/[0.08] bg-[#1A1A1A]">
        <CardHeader>
          <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
            <Key className="h-5 w-5" />
            Password
          </CardTitle>
          <CardDescription>Change your account password</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {isOAuthUser ? (
            <div className="py-4 text-center">
              <p className="text-white/60">
                You signed in with Google. Password management is handled through your Google account.
              </p>
            </div>
          ) : (
            <>
              <div className="space-y-2">
                <Label htmlFor="new-password" className="text-white/60">
                  New Password
                </Label>
                <Input
                  id="new-password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password"
                  className="bg-[#0F0F0F] border-white/[0.08] text-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirm-password" className="text-white/60">
                  Confirm New Password
                </Label>
                <Input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm new password"
                  className="bg-[#0F0F0F] border-white/[0.08] text-white"
                />
              </div>

              <Button
                onClick={handleChangePassword}
                disabled={changingPassword || !newPassword || !confirmPassword}
                className="bg-white text-black hover:bg-white/90"
              >
                {changingPassword && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Update Password
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {/* Sessions */}
      <Card className="border-white/[0.08] bg-[#1A1A1A]">
        <CardHeader>
          <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
            <Monitor className="h-5 w-5" />
            Sessions
          </CardTitle>
          <CardDescription>Manage your active sessions across devices</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Current Session */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-white/[0.03]">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-md bg-[#0F0F0F]">
                <Monitor className="h-5 w-5 text-white/60" />
              </div>
              <div>
                <p className="font-medium text-white">Current Session</p>
                <p className="text-sm text-white/60">This device • Active now</p>
              </div>
            </div>
            <Badge className="bg-green-600 hover:bg-green-600">Active</Badge>
          </div>

          <Separator className="bg-white/[0.08]" />

          <div className="space-y-3">
            <Button
              variant="outline"
              className="w-full justify-start text-red-400 hover:text-red-400 border-white/[0.08] hover:bg-red-500/10"
              onClick={handleLogoutAllSessions}
              disabled={loggingOutAll}
            >
              {loggingOutAll ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <LogOut className="h-4 w-4 mr-2" />
              )}
              Log Out From All Devices
            </Button>
            <p className="text-xs text-white/40">
              This will sign you out from all devices including this one
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Leaked Password Protection */}
      <SupportRequest
        featureType="leaked_password_protection"
        title="Leaked Password Protection"
        description="Check passwords against known breach databases to prevent compromised credentials"
        icon={ShieldCheck}
      />

      {/* 2FA (Coming Soon) */}
      <Card className="border-white/[0.08] bg-[#1A1A1A] opacity-60">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
                <Shield className="h-5 w-5" />
                Two-Factor Authentication
              </CardTitle>
              <CardDescription>Add an extra layer of security to your account</CardDescription>
            </div>
            <Badge variant="outline" className="text-white/60 border-white/[0.08]">
              Coming Soon
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-white/60">
            Two-factor authentication will be available in a future update.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
