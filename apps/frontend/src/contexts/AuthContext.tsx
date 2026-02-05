'use client';

import { createContext, useContext, useEffect, useState, ReactNode, useCallback, useRef } from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase } from "@/integrations/supabase/client";
import { useRouter, usePathname } from "next/navigation";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signUp: (email: string, password: string, fullName: string) => Promise<{ error: Error | null }>;
  signIn: (email: string, password: string) => Promise<{ error: Error | null }>;
  signInWithGoogle: () => Promise<{ error: Error | null }>;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Public routes that don't require authentication
const PUBLIC_ROUTES = [
  '/', '/login', '/signup', '/auth/callback', '/pricing', '/about', '/contact', 
  '/domains', '/how-it-works', '/solutions', '/press', '/careers', '/help', 
  '/terms', '/privacy', '/cookies'
];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const initRef = useRef(false);
  const router = useRouter();
  const pathname = usePathname();

  // Refresh session
  const refreshSession = useCallback(async () => {
    try {
      const { data: { session: refreshedSession }, error } = await supabase.auth.refreshSession();
      if (!error && refreshedSession) {
        setSession(refreshedSession);
        setUser(refreshedSession.user);
        return true;
      }
    } catch (err) {
      console.error("Session refresh error:", err);
    }
    return false;
  }, []);

  // Initialize auth - only once per mount
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;

    let mounted = true;

    const initAuth = async () => {
      try {
        // First, check if we have a confirmed session from callback
        const sessionConfirmed = typeof window !== 'undefined' && localStorage.getItem('mcleuker-session-confirmed');
        
        // Get current session
        const { data: { session: currentSession }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error("Session error:", error);
          if (mounted) {
            setLoading(false);
          }
          return;
        }

        if (currentSession && mounted) {
          setSession(currentSession);
          setUser(currentSession.user);
          
          // Clear the confirmation flag
          if (sessionConfirmed) {
            localStorage.removeItem('mcleuker-session-confirmed');
          }
        }
        
        if (mounted) {
          setLoading(false);
        }
      } catch (err) {
        console.error("Auth init error:", err);
        if (mounted) {
          setLoading(false);
        }
      }
    };

    // Set up auth state listener FIRST
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, currentSession) => {
        if (!mounted) return;

        console.log("Auth event:", event);

        // Update state immediately
        setSession(currentSession);
        setUser(currentSession?.user ?? null);
        setLoading(false);

        // Handle navigation based on event
        if (event === 'SIGNED_IN') {
          // Only redirect if on login/signup pages
          if (pathname === '/login' || pathname === '/signup') {
            const returnTo = localStorage.getItem('auth-return-to') || '/dashboard';
            localStorage.removeItem('auth-return-to');
            router.replace(returnTo);
          }
        } else if (event === 'SIGNED_OUT') {
          // Clear any stored user data
          localStorage.removeItem('mcleuker-session-confirmed');
          localStorage.removeItem('mcleuker-user-id');
          router.replace('/');
        }
      }
    );

    // Then initialize
    initAuth();

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []); // Empty deps - only run once

  // Redirect protection - separate effect
  useEffect(() => {
    if (loading) return;
    
    const isPublicRoute = PUBLIC_ROUTES.some(route => 
      pathname === route || 
      pathname.startsWith('/auth/') ||
      pathname.startsWith('/domain/') ||
      pathname.startsWith('/solutions/')
    );
    
    // Only redirect if not authenticated and not on public route
    if (!user && !isPublicRoute) {
      // Store current path for return
      localStorage.setItem('auth-return-to', pathname);
      router.replace('/login');
    }
  }, [loading, user, pathname, router]);

  const signUp = useCallback(async (email: string, password: string, fullName: string) => {
    try {
      const { error } = await supabase.auth.signUp({
        email: email.trim().toLowerCase(),
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
          data: { full_name: fullName.trim() },
        },
      });
      return { error: error as Error | null };
    } catch (err) {
      return { error: err as Error };
    }
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: email.trim().toLowerCase(),
        password,
      });
      return { error: error as Error | null };
    } catch (err) {
      return { error: err as Error };
    }
  }, []);

  const signInWithGoogle = useCallback(async () => {
    try {
      // Store return URL
      const returnTo = pathname !== '/login' && pathname !== '/signup' ? pathname : '/dashboard';
      localStorage.setItem('auth-return-to', returnTo);

      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'select_account',
          },
        },
      });
      
      return { error: error as Error | null };
    } catch (err) {
      return { error: err as Error };
    }
  }, [pathname]);

  const signOut = useCallback(async () => {
    try {
      await supabase.auth.signOut();
      // Clear local storage
      localStorage.removeItem('mcleuker-session-confirmed');
      localStorage.removeItem('mcleuker-user-id');
      localStorage.removeItem('auth-return-to');
    } catch (err) {
      console.error("SignOut error:", err);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ 
      user, 
      session, 
      loading, 
      signUp, 
      signIn, 
      signInWithGoogle, 
      signOut,
      refreshSession 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
