'use client';

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";
import { ArrowRight, Eye, EyeOff, Check, AlertCircle } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [sessionReady, setSessionReady] = useState(false);
  const [sessionError, setSessionError] = useState(false);

  // Handle the auth callback - Supabase will set the session from the URL hash
  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Check if there's a hash fragment with access_token (Supabase recovery flow)
        const hash = window.location.hash;
        if (hash && hash.includes('access_token')) {
          // Supabase client will automatically pick up the session from the URL
          const { data: { session }, error } = await supabase.auth.getSession();
          if (error) {
            console.error('Session error:', error);
            setSessionError(true);
            return;
          }
          if (session) {
            setSessionReady(true);
            return;
          }
        }

        // Also check for code parameter (PKCE flow)
        const code = searchParams.get('code');
        if (code) {
          const { error } = await supabase.auth.exchangeCodeForSession(code);
          if (error) {
            console.error('Code exchange error:', error);
            setSessionError(true);
            return;
          }
          setSessionReady(true);
          return;
        }

        // Check if there's already an active session (user might have clicked the link)
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          setSessionReady(true);
          return;
        }

        // Listen for auth state changes (recovery event)
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
          (event, session) => {
            if (event === 'PASSWORD_RECOVERY' || (event === 'SIGNED_IN' && session)) {
              setSessionReady(true);
            }
          }
        );

        // Give it a few seconds to process
        setTimeout(() => {
          if (!sessionReady) {
            // Check one more time
            supabase.auth.getSession().then(({ data: { session } }) => {
              if (session) {
                setSessionReady(true);
              } else {
                setSessionError(true);
              }
            });
          }
        }, 3000);

        return () => subscription.unsubscribe();
      } catch {
        setSessionError(true);
      }
    };

    handleAuthCallback();
  }, [searchParams, sessionReady]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setIsLoading(true);

    try {
      const { error } = await supabase.auth.updateUser({
        password: password,
      });

      if (error) {
        setError(error.message || "Failed to update password");
        setIsLoading(false);
      } else {
        setSuccess(true);
        setIsLoading(false);
        // Redirect to dashboard after a short delay
        setTimeout(() => {
          router.push("/dashboard");
        }, 2000);
      }
    } catch {
      setError("An unexpected error occurred. Please try again.");
      setIsLoading(false);
    }
  };

  // Success state
  if (success) {
    return (
      <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <Link href="/" className="inline-block">
              <span className="font-editorial text-2xl text-white tracking-[0.02em]">McLeuker<span className="text-white/30">.ai</span></span>
            </Link>
          </div>

          <div className={cn(
            "p-8 rounded-[20px]",
            "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
            "border border-white/[0.08]"
          )}>
            <div className="text-center">
              <div className="w-16 h-16 bg-[#2E3524]/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Check className="w-8 h-8 text-[#5c6652]" />
              </div>
              <h2 className="text-2xl font-editorial text-white/[0.92] mb-2">
                Password updated
              </h2>
              <p className="text-white/55">
                Your password has been successfully reset. Redirecting to dashboard...
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Session error - invalid or expired link
  if (sessionError) {
    return (
      <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <Link href="/" className="inline-block">
              <span className="font-editorial text-2xl text-white tracking-[0.02em]">McLeuker<span className="text-white/30">.ai</span></span>
            </Link>
          </div>

          <div className={cn(
            "p-8 rounded-[20px]",
            "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
            "border border-white/[0.08]"
          )}>
            <div className="text-center">
              <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="w-8 h-8 text-red-400" />
              </div>
              <h2 className="text-2xl font-editorial text-white/[0.92] mb-2">
                Invalid or expired link
              </h2>
              <p className="text-white/55 mb-6">
                This password reset link is invalid or has expired. Please request a new one.
              </p>
              <Link
                href="/forgot-password"
                className={cn(
                  "inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full",
                  "bg-gradient-to-r from-[#2E3524] to-[#21261A] text-white font-medium",
                  "hover:from-[#3a4330] hover:to-[#2a3021] transition-all"
                )}
              >
                Request new link
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          <div className="text-center mt-8">
            <Link href="/login" className="text-sm text-white/40 hover:text-white/70 transition-colors">
              ← Back to sign in
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Loading state - waiting for session
  if (!sessionReady) {
    return (
      <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <Link href="/" className="inline-block">
              <span className="font-editorial text-2xl text-white tracking-[0.02em]">McLeuker<span className="text-white/30">.ai</span></span>
            </Link>
          </div>

          <div className={cn(
            "p-8 rounded-[20px]",
            "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
            "border border-white/[0.08]"
          )}>
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-white/20 border-t-[#5c6652] rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-white/55">Verifying your reset link...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Reset password form
  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <Link href="/" className="inline-block">
            <span className="font-editorial text-2xl text-white tracking-[0.02em]">McLeuker<span className="text-white/30">.ai</span></span>
          </Link>
        </div>

        {/* Reset Password Card */}
        <div className={cn(
          "p-8 rounded-[20px]",
          "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
          "border border-white/[0.08]"
        )}>
          <h1 className="text-2xl font-editorial text-white/[0.92] mb-2 text-center">
            Set new password
          </h1>
          <p className="text-white/55 text-center mb-8">
            Enter your new password below.
          </p>

          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm text-white/70 mb-2">New password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={cn(
                    "w-full h-12 px-4 pr-12 rounded-lg",
                    "bg-white/[0.06] border border-white/[0.10]",
                    "text-white placeholder:text-white/40",
                    "focus:outline-none focus:border-white/[0.18]"
                  )}
                  placeholder="••••••••"
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-xs text-white/40 mt-1">Minimum 8 characters</p>
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-2">Confirm new password</label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={cn(
                    "w-full h-12 px-4 pr-12 rounded-lg",
                    "bg-white/[0.06] border border-white/[0.10]",
                    "text-white placeholder:text-white/40",
                    "focus:outline-none focus:border-white/[0.18]",
                    confirmPassword && password !== confirmPassword
                      ? "border-red-500/30"
                      : confirmPassword && password === confirmPassword
                      ? "border-[#2E3524]/50"
                      : ""
                  )}
                  placeholder="••••••••"
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {confirmPassword && password !== confirmPassword && (
                <p className="text-xs text-red-400 mt-1">Passwords do not match</p>
              )}
              {confirmPassword && password === confirmPassword && (
                <p className="text-xs text-[#5c6652] mt-1 flex items-center gap-1">
                  <Check className="w-3 h-3" />
                  Passwords match
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading || !password || !confirmPassword || password !== confirmPassword}
              className={cn(
                "w-full flex items-center justify-center gap-2 px-6 py-3 rounded-full",
                "bg-gradient-to-r from-[#2E3524] to-[#21261A] text-white font-medium",
                "hover:from-[#3a4330] hover:to-[#2a3021] transition-all",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {isLoading ? "Updating password..." : "Update password"}
              {!isLoading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>
        </div>

        {/* Back to login */}
        <div className="text-center mt-8">
          <Link href="/login" className="text-sm text-white/40 hover:text-white/70 transition-colors">
            ← Back to sign in
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#070707] flex items-center justify-center">
        <div className="text-white/40">Loading...</div>
      </div>
    }>
      <ResetPasswordContent />
    </Suspense>
  );
}
