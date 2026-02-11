import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

const SUPABASE_URL = 'https://auth.mcleukerai.com';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2bnBvYXJmZ2t6c3d3amtob2VzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNTEzNTYsImV4cCI6MjA3NjYyNzM1Nn0.BH49KtjHLlwAjTDO4eGYwnb3D2meFQ-ffl63XDbRtYQ';

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/dashboard';
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');
  const type = searchParams.get('type');

  // Handle OAuth errors from provider
  if (error) {
    const url = new URL('/login', origin);
    url.searchParams.set('error', error);
    if (errorDescription) {
      url.searchParams.set('error_description', errorDescription);
    }
    return NextResponse.redirect(url);
  }

  if (!code) {
    const url = new URL('/login', origin);
    url.searchParams.set('error', 'no_code');
    url.searchParams.set('error_description', 'No authorization code was provided');
    return NextResponse.redirect(url);
  }

  const cookieStore = await cookies();

  // Create Supabase server client with cookie handling matching the browser client defaults
  const supabase = createServerClient(
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing sessions.
          }
        },
      },
    }
  );

  try {
    const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

    if (exchangeError) {
      console.error('Error exchanging code for session:', exchangeError.message);
      const url = new URL('/login', origin);
      url.searchParams.set('error', 'auth_failed');
      url.searchParams.set('error_description', exchangeError.message);
      return NextResponse.redirect(url);
    }

    if (data?.session) {
      // Check if this is a password recovery flow
      // Supabase sets type=recovery in the redirect URL for password reset
      const isRecovery = type === 'recovery' || next === '/reset-password';
      
      if (isRecovery) {
        // Redirect to reset-password page with the session established
        return NextResponse.redirect(`${origin}/reset-password`);
      }

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
            last_active_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }, {
            onConflict: 'id',
          });
      } catch (dbError) {
        console.error('Error upserting user record:', dbError);
      }

      return NextResponse.redirect(`${origin}${next}`);
    }
  } catch (err) {
    console.error('Unexpected error during auth callback:', err);
  }

  const url = new URL('/login', origin);
  url.searchParams.set('error', 'auth_failed');
  url.searchParams.set('error_description', 'Failed to create session');
  return NextResponse.redirect(url);
}
