import { createBrowserClient } from '@supabase/ssr';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Validate environment variables
if (!SUPABASE_URL) {
  console.error('Missing NEXT_PUBLIC_SUPABASE_URL environment variable');
}
if (!SUPABASE_ANON_KEY) {
  console.error('Missing NEXT_PUBLIC_SUPABASE_ANON_KEY environment variable');
}

// Create Supabase client with proper SSR cookie handling for PKCE flow
// This ensures the code verifier is stored in cookies and accessible during OAuth callback
export const supabase = createBrowserClient(
  SUPABASE_URL,
  SUPABASE_ANON_KEY,
  {
    auth: {
      // Use PKCE flow (required for SSR)
      flowType: 'pkce',
      // Automatically refresh token before expiry
      autoRefreshToken: true,
      // Persist session - this will use cookies via @supabase/ssr
      persistSession: true,
      // Detect session from URL (for OAuth callbacks)
      detectSessionInUrl: true,
      // Storage key prefix
      storageKey: 'sb-auth',
    },
    // Cookie options are handled by @supabase/ssr automatically
    // The library stores the PKCE code verifier in cookies for SSR compatibility
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
          return session; // Return existing session as fallback
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
    // Use 'id' column since that's the primary key in your users table
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
