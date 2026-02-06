import { createBrowserClient } from '@supabase/ssr';

// Hardcode the Supabase credentials directly to ensure they're always available
// This is a temporary fix - in production, these should come from environment variables
const SUPABASE_URL = 'https://cvnpoarfgkzswwjkhoes.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2bnBvYXJmZ2t6c3d3amtob2VzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNTEzNTYsImV4cCI6MjA3NjYyNzM1Nn0.BH49KtjHLlwAjTDO4eGYwnb3D2meFQ-ffl63XDbRtYQ';

// Validate that credentials are available
if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  throw new Error('Supabase credentials are missing');
}

// Create Supabase client with proper SSR cookie handling for PKCE flow
export const supabase = createBrowserClient(
  SUPABASE_URL,
  SUPABASE_ANON_KEY,
  {
    auth: {
      // Use PKCE flow (required for SSR)
      flowType: 'pkce',
      // Automatically refresh token before expiry
      autoRefreshToken: true,
      // Persist session in cookies
      persistSession: true,
      // Detect session from URL (for OAuth callbacks)
      detectSessionInUrl: true,
      // Storage key prefix
      storageKey: 'sb-auth',
      // Cookie options
      cookieOptions: {
        name: 'sb-auth-token',
        lifetime: 60 * 60 * 24 * 365, // 1 year
        domain: typeof window !== 'undefined' ? window.location.hostname : '',
        path: '/',
        sameSite: 'lax',
      }
    },
  }
);

// Helper function to ensure session is refreshed
export async function ensureSession() {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();
    
    if (error) {
      console.error('Error getting session:', error);
      return null;
    }
    
    if (!session) {
      return null;
    }
    
    // Check if token needs refresh (within 5 minutes of expiry)
    const expiresAt = session.expires_at;
    if (expiresAt) {
      const now = Math.floor(Date.now() / 1000);
      const fiveMinutes = 5 * 60;
      
      if (expiresAt - now < fiveMinutes) {
        const { data: { session: refreshedSession }, error: refreshError } = 
          await supabase.auth.refreshSession();
        
        if (refreshError) {
          console.error('Error refreshing session:', refreshError);
          return session;
        }
        
        return refreshedSession;
      }
    }
    
    return session;
  } catch (error) {
    console.error('Unexpected error in ensureSession:', error);
    return null;
  }
}

// Helper to update last login timestamp
export async function updateLastLogin(userId: string) {
  try {
    await supabase
      .from('users')
      .update({ last_login_at: new Date().toISOString() })
      .eq('id', userId);
  } catch (error) {
    console.error('Error updating last login:', error);
  }
}

// Helper to get current user from session
export async function getCurrentUser() {
  const { data: { user }, error } = await supabase.auth.getUser();
  if (error) {
    console.error('Error getting current user:', error);
    return null;
  }
  return user;
}
