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
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Public routes that don't require authentication
const PUBLIC_ROUTES = ['/', '/login', '/signup', '/auth/callback', '/pricing', '/about', '/contact'];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();
  const initRef = useRef(false);
  const sessionCheckRef = useRef(false);

  // Refresh session manually
  const refreshSession = useCallback(async () => {
    try {
      const { data: { session: refreshedSession }, error } = await supabase.auth.refreshSession();
      if (!error && refreshedSession) {
        setSession(refreshedSession);
        setUser(refreshedSession.user);
        // Also store in localStorage as backup
        if (typeof window !== 'undefined') {
          localStorage.setItem('mcleuker-user-id', refreshedSession.user.id);
        }
      }
    } catch (err) {
      console.error("Session refresh error:", err);
    }
  }, []);

  // Initialize auth state - IMPROVED VERSION
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;

    let mounted = true;

    const initializeAuth = async () => {
      try {
        // CRITICAL: Check localStorage first for faster initial load
        const storedUserId = typeof window !== 'undefined' ? localStorage.getItem('mcleuker-user-id') : null;
        
        // Get session from Supabase
        const { data: { session: existingSession }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error("Error getting session:", error);
          // Clear stored user ID if session is invalid
          if (typeof window !== 'undefined') {
            localStorage.removeItem('mcleuker-user-id');
          }
          if (mounted) {
            setLoading(false);
          }
          return;
        }

        if (mounted) {
          if (existingSession) {
            setSession(existingSession);
            setUser(existingSession.user);
            
            // Store user ID for faster subsequent loads
            if (typeof window !== 'undefined') {
              localStorage.setItem('mcleuker-user-id', existingSession.user.id);
            }
            
            // Check if token needs refresh (within 10 minutes of expiry)
            const expiresAt = existingSession.expires_at;
            if (expiresAt) {
              const expiryTime = expiresAt * 1000;
              const now = Date.now();
              const tenMinutes = 10 * 60 * 1000;
              
              if (expiryTime - now < tenMinutes) {
                // Token is about to expire, refresh it
                await refreshSession();
              }
            }
          } else if (storedUserId) {
            // We have a stored user ID but no session - try to refresh
            console.log("Stored user ID found, attempting session refresh...");
            const { data: { session: refreshedSession } } = await supabase.auth.refreshSession();
            if (refreshedSession) {
              setSession(refreshedSession);
              setUser(refreshedSession.user);
            } else {
              // Clear invalid stored data
              localStorage.removeItem('mcleuker-user-id');
            }
          }
          
          setLoading(false);

          // If user is logged in and on login page, redirect to dashboard
          if (existingSession?.user && (pathname === '/login' || pathname === '/signup')) {
            router.replace('/dashboard');
          }
        }
      } catch (err) {
        console.error("Auth initialization error:", err);
        if (mounted) {
          setLoading(false);
        }
      }
    };

    // Set up auth state listener FIRST
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, currentSession) => {
        console.log("Auth state changed:", event, currentSession?.user?.email);
        
        if (!mounted) return;

        // Update state
        setSession(currentSession);
        setUser(currentSession?.user ?? null);
        setLoading(false);

        // Store/clear user ID
        if (typeof window !== 'undefined') {
          if (currentSession?.user) {
            localStorage.setItem('mcleuker-user-id', currentSession.user.id);
          } else {
            localStorage.removeItem('mcleuker-user-id');
          }
        }

        // Handle different auth events
        if (event === 'SIGNED_IN') {
          // User signed in - redirect to dashboard if on public route
          if (pathname === '/login' || pathname === '/signup' || pathname === '/') {
            router.replace('/dashboard');
          }
        } else if (event === 'SIGNED_OUT') {
          // User signed out - redirect to home
          router.replace('/');
        } else if (event === 'TOKEN_REFRESHED') {
          console.log('Token refreshed successfully');
        } else if (event === 'USER_UPDATED') {
          console.log('User updated');
        }
      }
    );

    // Then initialize
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
  }, [pathname, router, refreshSession]);

  // Redirect unauthenticated users from protected routes
  useEffect(() => {
    if (!loading && !user && !PUBLIC_ROUTES.some(route => pathname === route || pathname.startsWith('/auth/'))) {
      router.replace('/login');
    }
  }, [loading, user, pathname, router]);

  const signUp = useCallback(async (email: string, password: string, fullName: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
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
            // CRITICAL: Use 'none' to skip consent if already authorized
            // This prevents re-login on every visit
            prompt: 'none',
          },
        },
      });
      
      if (error) {
        // If 'none' fails (user needs to consent), fall back to 'select_account'
        if (error.message?.includes('interaction_required') || error.message?.includes('consent_required')) {
          const { error: retryError } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
              redirectTo: `${window.location.origin}/auth/callback`,
              queryParams: {
                access_type: 'offline',
                prompt: 'select_account',
              },
            },
          });
          
          if (retryError) {
            console.error("Google OAuth retry error:", retryError);
            return { error: retryError as Error };
          }
          return { error: null };
        }
        
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
      // Clear all auth-related storage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('mcleuker-auth-session');
        localStorage.removeItem('mcleuker-auth-token');
        localStorage.removeItem('mcleuker-user-id');
        localStorage.removeItem('auth-return-to');
        localStorage.removeItem('mcleuker-active-chat');
        localStorage.removeItem('mcleuker-chat-messages');
      }
      
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
