import { type EmailOtpType } from '@supabase/supabase-js';
import { type NextRequest, NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

const SUPABASE_URL = 'https://auth.mcleukerai.com';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2bnBvYXJmZ2t6c3d3amtob2VzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNTEzNTYsImV4cCI6MjA3NjYyNzM1Nn0.BH49KtjHLlwAjTDO4eGYwnb3D2meFQ-ffl63XDbRtYQ';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const token_hash = searchParams.get('token_hash');
  const type = searchParams.get('type') as EmailOtpType | null;
  const next = searchParams.get('next') ?? '/dashboard';

  const redirectTo = request.nextUrl.clone();
  redirectTo.pathname = next;
  // Clear all search params for the redirect
  redirectTo.search = '';

  if (token_hash && type) {
    const cookieStore = await cookies();

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
            }
          },
        },
      }
    );

    const { error } = await supabase.auth.verifyOtp({
      type,
      token_hash,
    });

    if (!error) {
      // Successfully verified - redirect to the next page
      return NextResponse.redirect(redirectTo);
    }

    console.error('Error verifying OTP:', error.message);
  }

  // If verification failed, redirect to an error page
  redirectTo.pathname = '/reset-password';
  redirectTo.searchParams.set('error', 'invalid_token');
  return NextResponse.redirect(redirectTo);
}
