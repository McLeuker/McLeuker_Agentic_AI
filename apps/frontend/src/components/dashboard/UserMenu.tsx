'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import {
  User,
  Settings,
  CreditCard,
  Sliders,
  LogOut,
  ChevronDown,
  Sparkles,
} from 'lucide-react';
import { supabase } from '@/integrations/supabase/client';

interface UserMenuProps {
  collapsed?: boolean;
}

export function UserMenu({ collapsed = false }: UserMenuProps) {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [profileImage, setProfileImage] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Fetch profile image from users table
  const fetchProfileImage = useCallback(async () => {
    if (!user) return;
    const { data } = await supabase
      .from('users')
      .select('profile_image')
      .eq('id', user.id)
      .single();
    if (data?.profile_image) {
      setProfileImage(data.profile_image);
    }
  }, [user]);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch profile image on mount and listen for updates
  useEffect(() => {
    fetchProfileImage();
    const handleProfileUpdate = () => fetchProfileImage();
    window.addEventListener('profile-updated', handleProfileUpdate);
    return () => window.removeEventListener('profile-updated', handleProfileUpdate);
  }, [fetchProfileImage]);

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  const getInitials = (name: string | undefined, email: string | undefined) => {
    if (name) {
      return name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    if (email) {
      return email.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  const displayName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';
  const initials = getInitials(user?.user_metadata?.full_name, user?.email);

  if (!user) return null;

  const menuItems = [
    { label: 'Account Settings', href: '/settings', icon: Settings },
    { label: 'Billing & Credits', href: '/billing', icon: CreditCard },
    { label: 'Preferences', href: '/preferences', icon: Sliders },
  ];

  if (collapsed) {
    return (
      <div ref={menuRef} className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'w-10 h-10 rounded-full flex items-center justify-center overflow-hidden',
            'bg-gradient-to-br from-[#2E3524] to-[#2A3021]',
            'border border-white/[0.12] hover:border-white/30',
            'transition-all duration-200',
            isOpen && 'ring-2 ring-[#2E3524]/30'
          )}
        >
          {profileImage || user?.user_metadata?.avatar_url ? (
            <img src={profileImage || user?.user_metadata?.avatar_url} alt="Profile" className="w-full h-full object-cover" />
          ) : (
            <span className="text-sm font-medium text-white">{initials}</span>
          )}
        </button>

        {isOpen && (
          <div className="absolute bottom-full left-0 mb-2 w-56 bg-[#1A1A1A] border border-white/[0.08] rounded-lg shadow-xl overflow-hidden z-50">
            {/* User Info */}
            <div className="p-3 border-b border-white/[0.08]">
              <p className="text-sm font-medium text-white truncate">{displayName}</p>
              <p className="text-xs text-white/50 truncate">{user.email}</p>
            </div>

            {/* Menu Items */}
            <div className="py-1">
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className="flex items-center gap-3 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/[0.05] transition-colors"
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </Link>
                );
              })}
            </div>

            {/* Sign Out */}
            <div className="border-t border-white/[0.08] py-1">
              <button
                onClick={handleSignOut}
                className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg',
          'hover:bg-white/[0.05] transition-all',
          isOpen && 'bg-white/[0.05]'
        )}
      >
        {/* Avatar */}
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#2E3524] to-[#2A3021] border border-white/[0.12] flex items-center justify-center flex-shrink-0 overflow-hidden">
          {profileImage || user?.user_metadata?.avatar_url ? (
            <img src={profileImage || user?.user_metadata?.avatar_url} alt="Profile" className="w-full h-full object-cover" />
          ) : (
            <span className="text-sm font-medium text-white">{initials}</span>
          )}
        </div>

        {/* User Info */}
        <div className="flex-1 min-w-0 text-left">
          <p className="text-sm font-medium text-white truncate">{displayName}</p>
          <p className="text-xs text-white/50 truncate">{user.email}</p>
        </div>

        {/* Chevron */}
        <ChevronDown
          className={cn(
            'w-4 h-4 text-white/40 transition-transform',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute bottom-full left-0 right-0 mb-2 bg-[#1A1A1A] border border-white/[0.08] rounded-lg shadow-xl overflow-hidden z-50">
          {/* Plan Badge */}
          <div className="px-3 py-2 border-b border-white/[0.08] flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-xs text-white/60">Free Plan</span>
            <Link
              href="/pricing"
              className="ml-auto text-xs text-purple-400 hover:text-purple-300"
            >
              Upgrade
            </Link>
          </div>

          {/* Menu Items */}
          <div className="py-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-white/[0.05] transition-colors"
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>

          {/* Sign Out */}
          <div className="border-t border-white/[0.08] py-1">
            <button
              onClick={handleSignOut}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
