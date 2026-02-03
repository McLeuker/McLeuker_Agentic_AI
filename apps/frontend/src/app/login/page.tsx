'use client';

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { ArrowRight, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    // Simulate login - in production, this would call your auth API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // For demo purposes, redirect to dashboard
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <Link href="/" className="inline-block">
            <span className="font-editorial text-2xl text-white">McLeuker</span>
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
              disabled={isLoading}
              className={cn(
                "w-full flex items-center justify-center gap-2 px-6 py-3 rounded-full",
                "bg-white text-black font-medium",
                "hover:bg-white/90 transition-colors",
                "disabled:opacity-50"
              )}
            >
              {isLoading ? "Signing in..." : "Sign in"}
              {!isLoading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/[0.08] text-center">
            <p className="text-sm text-white/55">
              Don't have an account?{" "}
              <Link href="/signup" className="text-white hover:underline">
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
