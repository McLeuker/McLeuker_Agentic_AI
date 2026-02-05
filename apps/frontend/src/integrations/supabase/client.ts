import { createBrowserClient } from '@supabase/ssr';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Create Supabase client with enhanced session persistence
export const supabase = createBrowserClient(
  SUPABASE_URL,
  SUPABASE_ANON_KEY,
  {
    cookieOptions: {
      // Session persists for 1 year
      maxAge: 60 * 60 * 24 * 365,
      // Allow cross-site requests for OAuth redirects
      sameSite: 'lax',
      // Secure in production
      secure: process.env.NODE_ENV === 'production',
      // Cookie accessible on all paths
      path: '/',
    },
    auth: {
      // Automatically refresh token before expiry
      autoRefreshToken: true,
      // Persist session in localStorage as backup
      persistSession: true,
      // Detect session from URL (for OAuth callbacks)
      detectSessionInUrl: true,
      // Storage key for session
      storageKey: 'mcleuker-auth-token',
      // Flow type for OAuth
      flowType: 'pkce',
    },
  }
);

// Helper function to ensure session is refreshed
export async function ensureSession() {
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
}

// Helper to update last login timestamp
export async function updateLastLogin(userId: string) {
  try {
    await supabase
      .from('users')
      .update({ last_login_at: new Date().toISOString() })
      .eq('user_id', userId);
  } catch (error) {
    console.error('Error updating last login:', error);
  }
}
