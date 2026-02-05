'use client';
import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from "react";
import { User, Session, AuthError } from "@supabase/supabase-js";
import { supabase, ensureSession, updateLastLogin } from "@/integrations/supabase/client";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signInWithGoogle: () => Promise<{ error: AuthError | null }>;
  signUp: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Session refresh interval (every 10 minutes)
const SESSION_REFRESH_INTERVAL = 10 * 60 * 1000;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  // Refresh session function
  const refreshSession = useCallback(async () => {
    try {
      const currentSession = await ensureSession();
      if (currentSession) {
        setSession(currentSession);
        setUser(currentSession.user);
      }
    } catch (error) {
      console.error('Error refreshing session:', error);
    }
  }, []);

  // Initialize session on mount
  useEffect(() => {
    let mounted = true;

    const initSession = async () => {
      try {
        // First, try to get session from Supabase
        const { data: { session: initialSession }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Error getting initial session:', error);
        }

        if (mounted) {
          if (initialSession) {
            setSession(initialSession);
            setUser(initialSession.user);
            
            // Update last login timestamp
            if (initialSession.user) {
              updateLastLogin(initialSession.user.id);
            }
          }
          setLoading(false);
          setInitialized(true);
        }
      } catch (error) {
        console.error('Error initializing session:', error);
        if (mounted) {
          setLoading(false);
          setInitialized(true);
        }
      }
    };

    initSession();

    return () => {
      mounted = false;
    };
  }, []);

  // Listen for auth state changes
  useEffect(() => {
    if (!initialized) return;

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, currentSession) => {
        console.log('Auth state change:', event);
        
        setSession(currentSession);
        setUser(currentSession?.user ?? null);
        setLoading(false);

        // Handle specific events
        if (event === 'SIGNED_IN' && currentSession?.user) {
          // Update last login on sign in
          updateLastLogin(currentSession.user.id);
        }

        if (event === 'TOKEN_REFRESHED') {
          console.log('Token refreshed successfully');
        }

        if (event === 'SIGNED_OUT') {
          // Clear any local storage
          localStorage.removeItem('mcleuker-auth-token');
        }
      }
    );

    return () => subscription.unsubscribe();
  }, [initialized]);

  // Periodic session refresh to prevent expiry
  useEffect(() => {
    if (!session) return;

    const intervalId = setInterval(() => {
      refreshSession();
    }, SESSION_REFRESH_INTERVAL);

    return () => clearInterval(intervalId);
  }, [session, refreshSession]);

  // Handle visibility change - refresh session when tab becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && session) {
        refreshSession();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [session, refreshSession]);

  // Handle focus - refresh session when window gains focus
  useEffect(() => {
    const handleFocus = () => {
      if (session) {
        refreshSession();
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [session, refreshSession]);

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    return { error };
  };

  const signInWithGoogle = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        },
      },
    });
    return { error };
  };

  const signUp = async (email: string, password: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    return { error };
  };

  const signOut = async () => { 
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
    // Clear local storage
    localStorage.removeItem('mcleuker-auth-token');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      session, 
      loading, 
      signIn, 
      signInWithGoogle, 
      signUp, 
      signOut,
      refreshSession 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
