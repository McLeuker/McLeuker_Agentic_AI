'use client';

import { useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { ArrowRight, ArrowLeft, Mail, Check } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (error) {
        setError(error.message || "Failed to send reset email");
        setIsLoading(false);
      } else {
        setSuccess(true);
        setIsLoading(false);
      }
    } catch {
      setError("An unexpected error occurred. Please try again.");
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          {/* Logo */}
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
                <Mail className="w-8 h-8 text-[#5c6652]" />
              </div>
              <h1 className="text-2xl font-editorial text-white/[0.92] mb-2">
                Check your email
              </h1>
              <p className="text-white/55 mb-6">
                We&apos;ve sent a password reset link to
              </p>
              <p className="text-white/80 font-medium mb-6 break-all">
                {email}
              </p>
              <p className="text-white/40 text-sm mb-8">
                Click the link in the email to reset your password. If you don&apos;t see the email, check your spam folder.
              </p>

              <button
                onClick={() => {
                  setSuccess(false);
                  setEmail("");
                }}
                className="text-sm text-[#5c6652] hover:text-[#7a8a6e] transition-colors"
              >
                Didn&apos;t receive the email? Try again
              </button>
            </div>
          </div>

          <div className="text-center mt-8">
            <Link href="/login" className="text-sm text-white/40 hover:text-white/70 transition-colors inline-flex items-center gap-1">
              <ArrowLeft className="w-3 h-3" />
              Back to sign in
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <Link href="/" className="inline-block">
            <span className="font-editorial text-2xl text-white tracking-[0.02em]">McLeuker<span className="text-white/30">.ai</span></span>
          </Link>
        </div>

        {/* Forgot Password Card */}
        <div className={cn(
          "p-8 rounded-[20px]",
          "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
          "border border-white/[0.08]"
        )}>
          <h1 className="text-2xl font-editorial text-white/[0.92] mb-2 text-center">
            Reset your password
          </h1>
          <p className="text-white/55 text-center mb-8">
            Enter your email address and we&apos;ll send you a link to reset your password.
          </p>

          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm text-white/70 mb-2">Email address</label>
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

            <button
              type="submit"
              disabled={isLoading}
              className={cn(
                "w-full flex items-center justify-center gap-2 px-6 py-3 rounded-full",
                "bg-gradient-to-r from-[#2E3524] to-[#21261A] text-white font-medium",
                "hover:from-[#3a4330] hover:to-[#2a3021] transition-all",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {isLoading ? "Sending reset link..." : "Send reset link"}
              {!isLoading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/[0.08] text-center">
            <p className="text-sm text-white/55">
              Remember your password?{" "}
              <Link href="/login" className="text-[#5c6652] hover:text-[#7a8a6e] transition-colors">
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Back to home */}
        <div className="text-center mt-8">
          <Link href="/" className="text-sm text-white/40 hover:text-white/70 transition-colors inline-flex items-center gap-1">
            <ArrowLeft className="w-3 h-3" />
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
