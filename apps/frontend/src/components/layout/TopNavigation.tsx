'use client';

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Menu, X } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

interface TopNavigationProps {
  variant?: "app" | "marketing";
}

const marketingLinks = [
  { name: "About", href: "/about" },
  { name: "Solutions", href: "/solutions" },
  { name: "Pricing", href: "/pricing" },
  { name: "Contact", href: "/contact" },
];

export function TopNavigation({ variant = "marketing" }: TopNavigationProps) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, loading } = useAuth();
  
  const isMarketing = variant === "marketing";
  const isActiveLink = (path: string) => pathname === path;

  // Hide on auth pages
  if (["/login", "/signup"].includes(pathname)) return null;

  return (
    <header className={cn(
      "fixed top-0 left-0 right-0 z-50",
      "bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A]",
      "border-b border-white/[0.08]",
      "backdrop-blur-sm",
      "shadow-[0_10px_28px_rgba(0,0,0,0.45)]"
    )}>
      <div className="h-16 lg:h-[72px] flex items-center justify-between px-6 lg:px-8">
        {/* Logo */}
        <div className="flex items-center gap-4 shrink-0">
          <Link href="/" className="flex items-center">
            <span className="font-editorial text-xl lg:text-2xl text-white tracking-[0.02em]">
              McLeuker<span className="text-white/30">.ai</span>
            </span>
          </Link>
        </div>

        {/* Marketing Links - Center */}
        {isMarketing && (
          <nav className="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
            {marketingLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "text-sm transition-colors py-1",
                  isActiveLink(link.href)
                    ? "text-white/90 border-b-2 border-white/[0.18]"
                    : "text-white/60 hover:text-white/90"
                )}
              >
                {link.name}
              </Link>
            ))}
          </nav>
        )}

        {/* Right Side */}
        <div className="flex items-center gap-3">
          {/* Mobile Menu Toggle */}
          {isMarketing && (
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-white/70 hover:text-white focus:outline-none focus:ring-2 focus:ring-white/20"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          )}

          {!loading && user ? (
            /* Logged in - show Dashboard button */
            <Link
              href="/dashboard"
              className="text-sm bg-white text-black hover:bg-white/90 px-4 py-2 rounded-md transition-colors"
            >
              Dashboard
            </Link>
          ) : (
            /* Not logged in - show Sign in and Get started */
            <>
              <Link
                href="/login"
                className="hidden sm:inline-flex text-sm text-white/70 hover:text-white hover:bg-white/10 px-4 py-2 rounded-md transition-colors"
              >
                Sign in
              </Link>
              <Link
                href="/signup"
                className="text-sm bg-white text-black hover:bg-white/90 px-4 py-2 rounded-md transition-colors"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Mobile Marketing Menu */}
      {isMarketing && mobileMenuOpen && (
        <div className="lg:hidden border-t border-white/[0.08] px-6 py-4 bg-[#0A0A0A]">
          <nav className="flex flex-col gap-3">
            {marketingLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  "text-sm py-2 transition-colors",
                  isActiveLink(link.href)
                    ? "text-white"
                    : "text-white/60 hover:text-white"
                )}
              >
                {link.name}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
