'use client';

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { ArrowRight, Eye, EyeOff, Check } from "lucide-react";

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    company: ""
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    // Simulate signup - in production, this would call your auth API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // For demo purposes, redirect to dashboard
    router.push("/dashboard");
  };

  const benefits = [
    "5 free research queries to start",
    "Access to all fashion domains",
    "Professional-grade reports",
    "No credit card required"
  ];

  return (
    <div className="min-h-screen bg-[#070707] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <Link href="/" className="inline-block">
            <span className="font-editorial text-2xl text-white">McLeuker</span>
          </Link>
        </div>

        {/* Signup Card */}
        <div className={cn(
          "p-8 rounded-[20px]",
          "bg-gradient-to-b from-[#141414] to-[#0F0F0F]",
          "border border-white/[0.08]"
        )}>
          <h1 className="text-2xl font-editorial text-white/[0.92] mb-2 text-center">
            Create your account
          </h1>
          <p className="text-white/55 text-center mb-8">
            Start your free trial today
          </p>

          {/* Benefits */}
          <div className="mb-8 p-4 rounded-lg bg-white/[0.04] border border-white/[0.06]">
            <ul className="space-y-2">
              {benefits.map((benefit, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-white/60">
                  <Check className="w-4 h-4 text-white/40" />
                  {benefit}
                </li>
              ))}
            </ul>
          </div>

          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm text-white/70 mb-2">Full Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className={cn(
                  "w-full h-12 px-4 rounded-lg",
                  "bg-white/[0.06] border border-white/[0.10]",
                  "text-white placeholder:text-white/40",
                  "focus:outline-none focus:border-white/[0.18]"
                )}
                placeholder="Your name"
                required
              />
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-2">Work Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className={cn(
                  "w-full h-12 px-4 rounded-lg",
                  "bg-white/[0.06] border border-white/[0.10]",
                  "text-white placeholder:text-white/40",
                  "focus:outline-none focus:border-white/[0.18]"
                )}
                placeholder="your@company.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-2">Company (optional)</label>
              <input
                type="text"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                className={cn(
                  "w-full h-12 px-4 rounded-lg",
                  "bg-white/[0.06] border border-white/[0.10]",
                  "text-white placeholder:text-white/40",
                  "focus:outline-none focus:border-white/[0.18]"
                )}
                placeholder="Your company"
              />
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-2">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
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

            <div className="flex items-start gap-2">
              <input 
                type="checkbox" 
                id="terms"
                className="w-4 h-4 mt-0.5 rounded bg-white/[0.06] border-white/[0.10]" 
                required
              />
              <label htmlFor="terms" className="text-sm text-white/55">
                I agree to the{" "}
                <Link href="/terms" className="text-white hover:underline">Terms of Service</Link>
                {" "}and{" "}
                <Link href="/privacy" className="text-white hover:underline">Privacy Policy</Link>
              </label>
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
              {isLoading ? "Creating account..." : "Create account"}
              {!isLoading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/[0.08] text-center">
            <p className="text-sm text-white/55">
              Already have an account?{" "}
              <Link href="/login" className="text-white hover:underline">
                Sign in
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
