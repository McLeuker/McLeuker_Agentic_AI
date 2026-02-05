'use client';

import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
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
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Public routes that don't require authentication
const PUBLIC_ROUTES = ['/', '/login', '/signup', '/auth/callback', '/pricing', '/about', '/contact', '/domains', '/how-it-works', '/solutions', '/press', '/careers', '/help', '/terms', '/privacy', '/cookies'];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // Refresh session manually
  const refreshSession = useCallback(async () => {
    try {
      const { data: { session: refreshedSession }, error } = await supabase.auth.refreshSession();
      if (!error && refreshedSession) {
        setSession(refreshedSession);
        setUser(refreshedSession.user);
      }
    } catch (err) {
      console.error("Session refresh error:", err);
    }
  }, []);

  // Initialize auth state - only once
  useEffect(() => {
    if (initialized) return;

    let mounted = true;

    const initializeAuth = async () => {
      try {
        // Get session from Supabase
        const { data: { session: existingSession }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error("Error getting session:", error);
          if (mounted) {
            setLoading(false);
            setInitialized(true);
          }
          return;
        }

        if (mounted) {
          if (existingSession) {
            setSession(existingSession);
            setUser(existingSession.user);
            
            // Check if token needs refresh (within 10 minutes of expiry)
            const expiresAt = existingSession.expires_at;
            if (expiresAt) {
              const expiryTime = expiresAt * 1000;
              const now = Date.now();
              const tenMinutes = 10 * 60 * 1000;
              
              if (expiryTime - now < tenMinutes) {
                await refreshSession();
              }
            }
          }
          
          setLoading(false);
          setInitialized(true);
        }
      } catch (err) {
        console.error("Auth initialization error:", err);
        if (mounted) {
          setLoading(false);
          setInitialized(true);
        }
      }
    };

    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, currentSession) => {
        console.log("Auth state changed:", event, currentSession?.user?.email);
        
        if (!mounted) return;

        // Update state
        setSession(currentSession);
        setUser(currentSession?.user ?? null);
        setLoading(false);

        // Handle different auth events
        if (event === 'SIGNED_IN') {
          // Check if we have a return URL stored
          const returnTo = typeof window !== 'undefined' ? localStorage.getItem('auth-return-to') : null;
          if (returnTo) {
            localStorage.removeItem('auth-return-to');
            router.replace(returnTo);
          } else if (pathname === '/login' || pathname === '/signup' || pathname === '/auth/callback') {
            router.replace('/dashboard');
          }
        } else if (event === 'SIGNED_OUT') {
          router.replace('/');
        } else if (event === 'TOKEN_REFRESHED') {
          console.log('Token refreshed successfully');
        }
      }
    );

    initializeAuth();

    // Set up periodic token refresh (every 5 minutes)
    const refreshInterval = setInterval(async () => {
      const { data: { session: currentSession } } = await supabase.auth.getSession();
      if (currentSession) {
        const expiresAt = currentSession.expires_at;
        if (expiresAt) {
          const expiryTime = expiresAt * 1000;
          const now = Date.now();
          const tenMinutes = 10 * 60 * 1000;
          
          if (expiryTime - now < tenMinutes) {
            await refreshSession();
          }
        }
      }
    }, 5 * 60 * 1000);

    return () => {
      mounted = false;
      subscription.unsubscribe();
      clearInterval(refreshInterval);
    };
  }, [initialized, refreshSession, router, pathname]);

  // Redirect unauthenticated users from protected routes
  useEffect(() => {
    // Don't redirect while loading or not initialized
    if (loading || !initialized) return;
    
    // Check if current path is public
    const isPublicRoute = PUBLIC_ROUTES.some(route => 
      pathname === route || 
      pathname.startsWith('/auth/') ||
      pathname.startsWith('/domain/') ||
      pathname.startsWith('/solutions/')
    );
    
    // Only redirect if not on a public route and not authenticated
    if (!user && !isPublicRoute) {
      router.replace('/login');
    }
  }, [loading, initialized, user, pathname, router]);

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

      if (error) {
        console.error("Signup error:", error);
        return { error: error as Error };
      }

      return { error: null };
    } catch (err) {
      console.error("Unexpected signup error:", err);
      return { error: err as Error };
    }
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: email.trim().toLowerCase(),
        password,
      });
      
      if (error) {
        console.error("SignIn error:", error);
        return { error: error as Error };
      }

      return { error: null };
    } catch (err) {
      console.error("Unexpected signin error:", err);
      return { error: err as Error };
    }
  }, []);

  const signInWithGoogle = useCallback(async () => {
    try {
      // Store the current URL to redirect back after login
      if (typeof window !== 'undefined') {
        const returnTo = pathname !== '/login' && pathname !== '/signup' ? pathname : '/dashboard';
        localStorage.setItem('auth-return-to', returnTo);
      }

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
      
      if (error) {
        console.error("Google OAuth error:", error);
        return { error: error as Error };
      }

      return { error: null };
    } catch (err) {
      console.error("Unexpected Google OAuth error:", err);
      return { error: err as Error };
    }
  }, [pathname]);

  const signOut = useCallback(async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error("SignOut error:", error);
      }
    } catch (err) {
      console.error("Unexpected signout error:", err);
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
