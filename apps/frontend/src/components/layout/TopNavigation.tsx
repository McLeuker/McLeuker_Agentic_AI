'use client';

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import {
  Menu, X, ChevronDown, ArrowRight,
  TrendingUp, Users, BarChart3, Leaf,
  Shirt, Heart, Droplets, Cpu, Sparkles, Palette, Factory, Globe,
  Layers, FileText, Zap
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

interface TopNavigationProps {
  variant?: "app" | "marketing";
}

const solutionItems = [
  { name: "Trend Forecasting", href: "/solutions/trend-forecasting", icon: TrendingUp, desc: "Runway analysis & trend prediction", color: "#C9A96E" },
  { name: "Supplier Research", href: "/solutions/supplier-research", icon: Users, desc: "Supplier discovery & evaluation", color: "#8ECAE6" },
  { name: "Market Analysis", href: "/solutions/market-analysis", icon: BarChart3, desc: "Competitive intelligence & pricing", color: "#A78BFA" },
  { name: "Sustainability Insights", href: "/solutions/sustainability-insights", icon: Leaf, desc: "ESG compliance & impact analysis", color: "#6b9b8a" },
];

const domainItems = [
  { name: "Fashion", href: "/domain/fashion", icon: Shirt, color: "#C9A96E" },
  { name: "Beauty", href: "/domain/beauty", icon: Heart, color: "#E07A5F" },
  { name: "Skincare", href: "/domain/skincare", icon: Droplets, color: "#8ECAE6" },
  { name: "Sustainability", href: "/domain/sustainability", icon: Leaf, color: "#6b9b8a" },
  { name: "Fashion Tech", href: "/domain/fashion-tech", icon: Cpu, color: "#A78BFA" },
  { name: "Catwalks", href: "/domain/catwalks", icon: Sparkles, color: "#F4D35E" },
  { name: "Culture", href: "/domain/culture", icon: Palette, color: "#E8998D" },
  { name: "Textile", href: "/domain/textile", icon: Factory, color: "#B5838D" },
  { name: "Lifestyle", href: "/domain/lifestyle", icon: Globe, color: "#D4A373" },
];

const resourceItems = [
  { name: "How It Works", href: "/how-it-works", icon: Layers, desc: "Our AI architecture" },
  { name: "Blog", href: "/blog", icon: FileText, desc: "Insights & updates" },
  { name: "About", href: "/about", icon: Zap, desc: "Our mission & team" },
];

export function TopNavigation({ variant = "marketing" }: TopNavigationProps) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [mobileExpanded, setMobileExpanded] = useState<string | null>(null);
  const { user, loading } = useAuth();
  const dropdownTimeout = useRef<NodeJS.Timeout | null>(null);
  
  const isMarketing = variant === "marketing";
  const isActiveLink = (path: string) => pathname === path;
  const isActiveSection = (paths: string[]) => paths.some(p => pathname.startsWith(p));

  // Close dropdown on route change
  useEffect(() => {
    setActiveDropdown(null);
    setMobileMenuOpen(false);
  }, [pathname]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('[data-dropdown]')) {
        setActiveDropdown(null);
      }
    };
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, []);

  const handleMouseEnter = (id: string) => {
    if (dropdownTimeout.current) clearTimeout(dropdownTimeout.current);
    setActiveDropdown(id);
  };

  const handleMouseLeave = () => {
    dropdownTimeout.current = setTimeout(() => setActiveDropdown(null), 150);
  };

  // Hide on auth pages
  if (["/login", "/signup"].includes(pathname)) return null;

  return (
    <header className={cn(
      "fixed top-0 left-0 right-0 z-50",
      "bg-[#0A0A0A]/95",
      "border-b border-white/[0.06]",
      "backdrop-blur-xl",
    )}>
      <div className="h-16 lg:h-[72px] flex items-center justify-between px-6 lg:px-10 max-w-[1440px] mx-auto">
        {/* Logo */}
        <div className="flex items-center gap-4 shrink-0">
          <Link href="/" className="flex items-center">
            <span className="font-editorial text-xl lg:text-[22px] text-white tracking-[0.02em]">
              McLeuker<span className="text-white/30">.ai</span>
            </span>
          </Link>
        </div>

        {/* Desktop Navigation - Center */}
        {isMarketing && (
          <nav className="hidden lg:flex items-center gap-1 absolute left-1/2 -translate-x-1/2">
            {/* Solutions Dropdown */}
            <div
              data-dropdown="solutions"
              className="relative"
              onMouseEnter={() => handleMouseEnter('solutions')}
              onMouseLeave={handleMouseLeave}
            >
              <button
                className={cn(
                  "flex items-center gap-1 px-3.5 py-2 rounded-lg text-sm transition-all",
                  isActiveSection(['/solutions'])
                    ? "text-white bg-white/[0.06]"
                    : "text-white/55 hover:text-white hover:bg-white/[0.04]"
                )}
              >
                Solutions
                <ChevronDown className={cn("w-3.5 h-3.5 transition-transform", activeDropdown === 'solutions' && "rotate-180")} />
              </button>

              {activeDropdown === 'solutions' && (
                <div className="absolute top-full left-1/2 -translate-x-1/2 pt-2" onMouseEnter={() => handleMouseEnter('solutions')} onMouseLeave={handleMouseLeave}>
                  <div className="w-[420px] p-2 rounded-xl bg-[#111111] border border-white/[0.08] shadow-2xl shadow-black/50">
                    <div className="px-3 py-2 mb-1">
                      <span className="text-[10px] text-white/25 uppercase tracking-[0.15em] font-medium">Research Solutions</span>
                    </div>
                    {solutionItems.map((item) => {
                      const ItemIcon = item.icon;
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/[0.04] transition-colors group"
                        >
                          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border" style={{ backgroundColor: `${item.color}08`, borderColor: `${item.color}15` }}>
                            <ItemIcon className="w-4 h-4" style={{ color: `${item.color}90` }} />
                          </div>
                          <div className="flex-1">
                            <div className="text-sm text-white/80 group-hover:text-white transition-colors">{item.name}</div>
                            <div className="text-[11px] text-white/30">{item.desc}</div>
                          </div>
                        </Link>
                      );
                    })}
                    <div className="border-t border-white/[0.06] mt-2 pt-2 px-3 py-2">
                      <Link href="/solutions" className="flex items-center gap-2 text-xs text-white/40 hover:text-white/70 transition-colors">
                        View all solutions <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Domains Dropdown */}
            <div
              data-dropdown="domains"
              className="relative"
              onMouseEnter={() => handleMouseEnter('domains')}
              onMouseLeave={handleMouseLeave}
            >
              <button
                className={cn(
                  "flex items-center gap-1 px-3.5 py-2 rounded-lg text-sm transition-all",
                  isActiveSection(['/domains', '/domain'])
                    ? "text-white bg-white/[0.06]"
                    : "text-white/55 hover:text-white hover:bg-white/[0.04]"
                )}
              >
                Domains
                <ChevronDown className={cn("w-3.5 h-3.5 transition-transform", activeDropdown === 'domains' && "rotate-180")} />
              </button>

              {activeDropdown === 'domains' && (
                <div className="absolute top-full left-1/2 -translate-x-1/2 pt-2" onMouseEnter={() => handleMouseEnter('domains')} onMouseLeave={handleMouseLeave}>
                  <div className="w-[340px] p-2 rounded-xl bg-[#111111] border border-white/[0.08] shadow-2xl shadow-black/50">
                    <div className="px-3 py-2 mb-1">
                      <span className="text-[10px] text-white/25 uppercase tracking-[0.15em] font-medium">Specialized Domains</span>
                    </div>
                    <div className="grid grid-cols-2 gap-0.5">
                      {domainItems.map((item) => {
                        const ItemIcon = item.icon;
                        return (
                          <Link
                            key={item.href}
                            href={item.href}
                            className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-white/[0.04] transition-colors group"
                          >
                            <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: `${item.color}70` }} />
                            <span className="text-sm text-white/55 group-hover:text-white/90 transition-colors">{item.name}</span>
                          </Link>
                        );
                      })}
                    </div>
                    <div className="border-t border-white/[0.06] mt-2 pt-2 px-3 py-2">
                      <Link href="/domains" className="flex items-center gap-2 text-xs text-white/40 hover:text-white/70 transition-colors">
                        Explore all domains <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Pricing - Direct link */}
            <Link
              href="/pricing"
              className={cn(
                "px-3.5 py-2 rounded-lg text-sm transition-all",
                isActiveLink('/pricing')
                  ? "text-white bg-white/[0.06]"
                  : "text-white/55 hover:text-white hover:bg-white/[0.04]"
              )}
            >
              Pricing
            </Link>

            {/* Resources Dropdown */}
            <div
              data-dropdown="resources"
              className="relative"
              onMouseEnter={() => handleMouseEnter('resources')}
              onMouseLeave={handleMouseLeave}
            >
              <button
                className={cn(
                  "flex items-center gap-1 px-3.5 py-2 rounded-lg text-sm transition-all",
                  isActiveSection(['/how-it-works', '/blog', '/about'])
                    ? "text-white bg-white/[0.06]"
                    : "text-white/55 hover:text-white hover:bg-white/[0.04]"
                )}
              >
                Resources
                <ChevronDown className={cn("w-3.5 h-3.5 transition-transform", activeDropdown === 'resources' && "rotate-180")} />
              </button>

              {activeDropdown === 'resources' && (
                <div className="absolute top-full right-0 pt-2" onMouseEnter={() => handleMouseEnter('resources')} onMouseLeave={handleMouseLeave}>
                  <div className="w-[260px] p-2 rounded-xl bg-[#111111] border border-white/[0.08] shadow-2xl shadow-black/50">
                    {resourceItems.map((item) => {
                      const ItemIcon = item.icon;
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/[0.04] transition-colors group"
                        >
                          <div className="w-7 h-7 rounded-md flex items-center justify-center bg-white/[0.04] flex-shrink-0">
                            <ItemIcon className="w-3.5 h-3.5 text-white/40 group-hover:text-white/70 transition-colors" />
                          </div>
                          <div>
                            <div className="text-sm text-white/70 group-hover:text-white transition-colors">{item.name}</div>
                            <div className="text-[11px] text-white/25">{item.desc}</div>
                          </div>
                        </Link>
                      );
                    })}
                    <div className="border-t border-white/[0.06] mt-2 pt-2">
                      <Link
                        href="/contact"
                        className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/[0.04] transition-colors group"
                      >
                        <div className="w-7 h-7 rounded-md flex items-center justify-center bg-white/[0.04] flex-shrink-0">
                          <span className="text-xs text-white/40 group-hover:text-white/70">@</span>
                        </div>
                        <div>
                          <div className="text-sm text-white/70 group-hover:text-white transition-colors">Contact</div>
                          <div className="text-[11px] text-white/25">Get in touch</div>
                        </div>
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </nav>
        )}

        {/* Right Side */}
        <div className="flex items-center gap-2">
          {/* Mobile Menu Toggle */}
          {isMarketing && (
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/[0.04] transition-all"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          )}

          {!loading && user ? (
            <Link
              href="/dashboard"
              className="text-sm bg-white text-black hover:bg-white/90 px-4 py-2 rounded-lg transition-colors font-medium"
            >
              Dashboard
            </Link>
          ) : (
            <>
              <Link
                href="/login"
                className="hidden sm:inline-flex text-sm text-white/55 hover:text-white px-3.5 py-2 rounded-lg hover:bg-white/[0.04] transition-all"
              >
                Sign in
              </Link>
              <Link
                href="/signup"
                className="text-sm bg-white text-[#0A0A0A] hover:bg-white/90 px-4 py-2 rounded-lg transition-colors font-medium"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Mobile Menu */}
      {isMarketing && mobileMenuOpen && (
        <div className="lg:hidden border-t border-white/[0.06] bg-[#0A0A0A]/98 backdrop-blur-xl max-h-[calc(100vh-64px)] overflow-y-auto">
          <nav className="px-4 py-3">
            {/* Solutions Group */}
            <div className="mb-1">
              <button
                onClick={() => setMobileExpanded(mobileExpanded === 'solutions' ? null : 'solutions')}
                className="flex items-center justify-between w-full px-3 py-3 rounded-lg text-sm text-white/70 hover:bg-white/[0.04] transition-all"
              >
                <span>Solutions</span>
                <ChevronDown className={cn("w-4 h-4 transition-transform", mobileExpanded === 'solutions' && "rotate-180")} />
              </button>
              {mobileExpanded === 'solutions' && (
                <div className="pl-3 pb-2 space-y-0.5">
                  {solutionItems.map((item) => {
                    const ItemIcon = item.icon;
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setMobileMenuOpen(false)}
                        className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-white/50 hover:text-white/80 hover:bg-white/[0.03] transition-all"
                      >
                        <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: `${item.color}70` }} />
                        {item.name}
                      </Link>
                    );
                  })}
                  <Link
                    href="/solutions"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center gap-2 px-3 py-2 text-xs text-white/30 hover:text-white/60 transition-colors"
                  >
                    View all <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              )}
            </div>

            {/* Domains Group */}
            <div className="mb-1">
              <button
                onClick={() => setMobileExpanded(mobileExpanded === 'domains' ? null : 'domains')}
                className="flex items-center justify-between w-full px-3 py-3 rounded-lg text-sm text-white/70 hover:bg-white/[0.04] transition-all"
              >
                <span>Domains</span>
                <ChevronDown className={cn("w-4 h-4 transition-transform", mobileExpanded === 'domains' && "rotate-180")} />
              </button>
              {mobileExpanded === 'domains' && (
                <div className="pl-3 pb-2 grid grid-cols-2 gap-0.5">
                  {domainItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-white/50 hover:text-white/80 hover:bg-white/[0.03] transition-all"
                    >
                      <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: `${item.color}70` }} />
                      {item.name}
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Direct Links */}
            <Link
              href="/pricing"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center px-3 py-3 rounded-lg text-sm text-white/70 hover:bg-white/[0.04] transition-all"
            >
              Pricing
            </Link>
            <Link
              href="/how-it-works"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center px-3 py-3 rounded-lg text-sm text-white/70 hover:bg-white/[0.04] transition-all"
            >
              How It Works
            </Link>
            <Link
              href="/about"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center px-3 py-3 rounded-lg text-sm text-white/70 hover:bg-white/[0.04] transition-all"
            >
              About
            </Link>
            <Link
              href="/blog"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center px-3 py-3 rounded-lg text-sm text-white/70 hover:bg-white/[0.04] transition-all"
            >
              Blog
            </Link>
            <Link
              href="/contact"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center px-3 py-3 rounded-lg text-sm text-white/70 hover:bg-white/[0.04] transition-all"
            >
              Contact
            </Link>

            {/* Mobile Auth */}
            <div className="border-t border-white/[0.06] mt-3 pt-3 flex gap-2 sm:hidden">
              <Link
                href="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="flex-1 text-center text-sm text-white/70 py-2.5 rounded-lg border border-white/[0.08] hover:bg-white/[0.04] transition-all"
              >
                Sign in
              </Link>
              <Link
                href="/signup"
                onClick={() => setMobileMenuOpen(false)}
                className="flex-1 text-center text-sm bg-white text-[#0A0A0A] py-2.5 rounded-lg font-medium hover:bg-white/90 transition-all"
              >
                Get started
              </Link>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
