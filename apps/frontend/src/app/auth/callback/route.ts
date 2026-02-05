import { NextResponse } from 'next/server';
import { createServerClient, type CookieOptions } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/dashboard';
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');

  // Handle OAuth errors
  if (error) {
    console.error('OAuth error:', error, errorDescription);
    const url = new URL('/login', origin);
    url.searchParams.set('error', error);
    if (errorDescription) {
      url.searchParams.set('error_description', errorDescription);
    }
    return NextResponse.redirect(url);
  }

  if (code) {
    const cookieStore = await cookies();
    
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
                // Ensure long-lived session
                maxAge: options.maxAge ?? 60 * 60 * 24 * 365, // 1 year
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
              });
            } catch (error) {
              // Handle cookie setting errors gracefully
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
      const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
      
      if (exchangeError) {
        console.error('Error exchanging code for session:', exchangeError);
        const url = new URL('/login', origin);
        url.searchParams.set('error', 'auth_failed');
        url.searchParams.set('error_description', exchangeError.message);
        return NextResponse.redirect(url);
      }

      if (data?.session) {
        console.log('Session created successfully for user:', data.session.user.id);
        
        // Update last login in users table
        try {
          await supabase
            .from('users')
            .upsert({
              user_id: data.session.user.id,
              email: data.session.user.email || '',
              name: data.session.user.user_metadata?.full_name || data.session.user.user_metadata?.name || '',
              auth_provider: data.session.user.app_metadata?.provider || 'email',
              last_login_at: new Date().toISOString(),
            }, {
              onConflict: 'user_id',
            });
        } catch (dbError) {
          console.error('Error updating user record:', dbError);
          // Don't fail the auth flow for this
        }

        // Redirect to the intended destination
        return NextResponse.redirect(`${origin}${next}`);
      }
    } catch (error) {
      console.error('Unexpected error during auth callback:', error);
    }
  }

  // Fallback: redirect to login with error
  const url = new URL('/login', origin);
  url.searchParams.set('error', 'auth_failed');
  return NextResponse.redirect(url);
}
