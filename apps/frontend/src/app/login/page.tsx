'use client';

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";
import { ArrowRight, Eye, EyeOff } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

function LoginContent() {
  const router = useRouter();
  const { signIn, signInWithGoogle, loading: authLoading } = useAuth();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const searchParams = useSearchParams();

  // Check for OAuth errors in URL params
  useEffect(() => {
    const errorParam = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');
    
    if (errorParam) {
      if (errorDescription) {
        setError(decodeURIComponent(errorDescription.replace(/\+/g, ' ')));
      } else {
        setError('Authentication failed. Please try again.');
      }
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    const { error } = await signIn(email, password);
    
    if (error) {
      setError(error.message || "Failed to sign in");
      setIsLoading(false);
    } else {
      router.push("/dashboard");
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError("");
    
    const { error } = await signInWithGoogle();
    
    if (error) {
      setError(error.message || "Failed to sign in with Google");
      setIsLoading(false);
    }
    // Google OAuth will redirect, so no need to handle success here
  };

  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <Link href="/" className="inline-block">
            <span className="font-editorial text-2xl text-white tracking-[0.02em]">McLeuker<span className="text-white/30">.ai</span></span>
          </Link>
        </div>

        {/* Login Card */}
        <div className={cn(
          "p-8 rounded-[20px]",
          "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
          "border border-white/[0.08]"
        )}>
          <h1 className="text-2xl font-editorial text-white/[0.92] mb-2 text-center">
            Welcome back
          </h1>
          <p className="text-white/55 text-center mb-8">
            Sign in to your account
          </p>

          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Google Login Button */}
          <button
            onClick={handleGoogleLogin}
            disabled={isLoading || authLoading}
            className={cn(
              "w-full flex items-center justify-center gap-3 px-6 py-3 rounded-full mb-6",
              "bg-white text-black font-medium",
              "hover:bg-white/90 transition-colors",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/[0.08]"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-[#0F0F0F] text-white/40">or continue with email</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm text-white/70 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={cn(
                  "w-full h-12 px-4 rounded-lg",
                  "bg-white/[0.06] border border-white/[0.10]",
                  "text-white placeholder:text-white/40",
                  "focus:outline-none focus:border-white/[0.18]"
                )}
                placeholder="your@email.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-2">Password</label>
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
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded bg-white/[0.06] border-white/[0.10]" />
                <span className="text-sm text-white/55">Remember me</span>
              </label>
              <Link href="/forgot-password" className="text-sm text-white/55 hover:text-white transition-colors">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={isLoading || authLoading}
              className={cn(
                "w-full flex items-center justify-center gap-2 px-6 py-3 rounded-full",
                "bg-gradient-to-r from-[#2E3524] to-[#21261A] text-white font-medium",
                "hover:from-[#3a4330] hover:to-[#2a3021] transition-all",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {isLoading ? "Signing in..." : "Sign in with Email"}
              {!isLoading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/[0.08] text-center">
            <p className="text-sm text-white/55">
              Don&apos;t have an account?{" "}
              <Link href="/signup" className="text-[#5c6652] hover:text-[#7a8a6e] transition-colors">
                Sign up
              </Link>
            </p>
          </div>
        </div>

        {/* Back to home */}
        <div className="text-center mt-8">
          <Link href="/" className="text-sm text-white/40 hover:text-white/70 transition-colors">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#070707] flex items-center justify-center">
        <div className="text-white/40">Loading...</div>
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}
