import { NextResponse } from 'next/server';
import { createServerClient, type CookieOptions } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/dashboard';
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');

  // Handle OAuth errors from provider
  if (error) {
    console.error('OAuth provider error:', error, errorDescription);
    const url = new URL('/login', origin);
    url.searchParams.set('error', error);
    if (errorDescription) {
      url.searchParams.set('error_description', errorDescription);
    }
    return NextResponse.redirect(url);
  }

  if (!code) {
    console.error('No code provided in callback');
    const url = new URL('/login', origin);
    url.searchParams.set('error', 'no_code');
    url.searchParams.set('error_description', 'No authorization code was provided');
    return NextResponse.redirect(url);
  }

  const cookieStore = await cookies();
  
  // Create Supabase client with proper cookie handling for PKCE
  const supabase = createServerClient(
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
              // Critical: These settings must match the client-side settings
              sameSite: 'lax',
              secure: process.env.NODE_ENV === 'production',
              path: '/',
              // Long-lived session (1 year)
              maxAge: options.maxAge ?? 60 * 60 * 24 * 365,
            });
          } catch (error) {
            console.error('Error setting cookie:', error);
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
            console.error('Error removing cookie:', error);
          }
        },
      },
    }
  );

  try {
    // Exchange the code for a session
    // The PKCE code verifier is automatically retrieved from cookies by @supabase/ssr
    const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
    
    if (exchangeError) {
      console.error('Error exchanging code for session:', exchangeError.message);
      const url = new URL('/login', origin);
      url.searchParams.set('error', 'auth_failed');
      url.searchParams.set('error_description', exchangeError.message);
      return NextResponse.redirect(url);
    }

    if (data?.session) {
      console.log('Session created successfully for user:', data.session.user.id);
      
      // Upsert user record in database
      try {
        const user = data.session.user;
        await supabase
          .from('users')
          .upsert({
            id: user.id,
            email: user.email || '',
            name: user.user_metadata?.full_name || user.user_metadata?.name || '',
            auth_provider: user.app_metadata?.provider || 'email',
            last_login_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }, {
            onConflict: 'id',
          });
      } catch (dbError) {
        // Don't fail auth for database errors
        console.error('Error upserting user record:', dbError);
      }

      // Redirect to the intended destination
      return NextResponse.redirect(`${origin}${next}`);
    }
  } catch (error) {
    console.error('Unexpected error during auth callback:', error);
  }

  // Fallback: redirect to login with error
  const url = new URL('/login', origin);
  url.searchParams.set('error', 'auth_failed');
  url.searchParams.set('error_description', 'Failed to create session');
  return NextResponse.redirect(url);
}
