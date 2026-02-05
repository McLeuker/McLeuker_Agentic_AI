import { createServerClient, type CookieOptions } from '@supabase/ssr';
import { cookies } from 'next/headers';

/**
 * Creates a Supabase client for use in Server Components, Server Actions, and Route Handlers.
 * This client properly handles cookies for PKCE flow and session management.
 */
export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          try {
            cookieStore.set({
              name,
              value,
              ...options,
              // Ensure proper cookie settings for auth
              sameSite: 'lax',
              secure: process.env.NODE_ENV === 'production',
              path: '/',
              // Long-lived session
              maxAge: options.maxAge ?? 60 * 60 * 24 * 365,
            });
          } catch (error) {
            // The `set` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing user sessions.
            console.error('Error setting cookie in server component:', error);
          }
        },
        remove(name: string, options: CookieOptions) {
          try {
            cookieStore.set({
              name,
              value: '',
              ...options,
              maxAge: 0,
            });
          } catch (error) {
            // The `delete` method was called from a Server Component.
            console.error('Error removing cookie in server component:', error);
          }
        },
      },
    }
  );
}

/**
 * Get the current user from the server-side session.
 * Use this in Server Components and Server Actions.
 */
export async function getServerUser() {
  const supabase = await createClient();
  const { data: { user }, error } = await supabase.auth.getUser();
  
  if (error) {
    console.error('Error getting server user:', error);
    return null;
  }
  
  return user;
}

/**
 * Get the current session from the server-side.
 * Use this in Server Components and Server Actions.
 */
export async function getServerSession() {
  const supabase = await createClient();
  const { data: { session }, error } = await supabase.auth.getSession();
  
  if (error) {
    console.error('Error getting server session:', error);
    return null;
  }
  
  return session;
}
